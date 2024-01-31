#include <iostream>

#include "Lepton.h"
#include "Palettes.h"
#include "SPI.h"
#include "Lepton_I2C.h"
#include <cstring>

#define PACKET_SIZE 164
#define PACKET_SIZE_UINT16 (PACKET_SIZE/2)
#define PACKETS_PER_FRAME 60
#define FRAME_SIZE_UINT16 (PACKET_SIZE_UINT16*PACKETS_PER_FRAME)
#define FPS 27;


Lepton::Lepton() {
	loglevel = 0;

	typeColormap = 3;
	selectedColormap = colormap_ironblack;
	selectedColormapSize = get_size_colormap_ironblack();

	//
	typeLepton = 2; // 2:Lepton 2.x  / 3:Lepton 3.x
	myImageWidth = 80;
	myImageHeight = 60;

	//
	spiSpeed = 20 * 1000 * 1000; // SPI bus speed 20MHz

	// min/max value for scaling
	autoRangeMin = true;
	autoRangeMax = true;
	rangeMin = 30000;
	rangeMax = 32000;
}

Lepton::~Lepton() {
}

void Lepton::setLogLevel(uint16_t newLoglevel)
{
	loglevel = newLoglevel;
}

void Lepton::useColormap(int newTypeColormap)
{
	switch (newTypeColormap) {
	case 1:
		typeColormap = 1;
		selectedColormap = colormap_rainbow;
		selectedColormapSize = get_size_colormap_rainbow();
		break;
	case 2:
		typeColormap = 2;
		selectedColormap = colormap_grayscale;
		selectedColormapSize = get_size_colormap_grayscale();
		break;
	default:
		typeColormap = 3;
		selectedColormap = colormap_ironblack;
		selectedColormapSize = get_size_colormap_ironblack();
		break;
	}
}

void Lepton::useLepton(int newTypeLepton)
{
	switch (newTypeLepton) {
	case 3:
		typeLepton = 3;
		myImageWidth = 160;
		myImageHeight = 120;
		break;
	default:
		typeLepton = 2;
		myImageWidth = 80;
		myImageHeight = 60;
	}
}

void Lepton::useSpiSpeedMhz(unsigned int newSpiSpeed)
{
	spiSpeed = newSpiSpeed * 1000 * 1000;
}

void Lepton::setAutomaticScalingRange()
{
	autoRangeMin = true;
	autoRangeMax = true;
}

void Lepton::useRangeMinValue(uint16_t newMinValue)
{
	autoRangeMin = false;
	rangeMin = newMinValue;
}

void Lepton::useRangeMaxValue(uint16_t newMaxValue)
{
	autoRangeMax = false;
	rangeMax = newMaxValue;
}

int* Lepton::get_image()
{
	//create the initial image
	int* image = new int [myImageHeight*myImageWidth*3];
	
	const int* colormap = selectedColormap;
	const int colormapSize = selectedColormapSize;
	uint16_t minValue = rangeMin;
	uint16_t maxValue = rangeMax;
	float diff = maxValue - minValue;
	float scale = 255 / diff;
	uint16_t n_wrong_segment = 0;
	uint16_t n_zero_value_drop_frame = 0;

	//open spi port
	SpiOpenPort(0, spiSpeed);

	

	//read data packets from lepton over SPI
	int resets = 0;
	int segmentNumber = -1;
	for (int j = 0; j < PACKETS_PER_FRAME; j++) {
		//if it's a drop packet, reset j to 0, set to -1 so he'll be at 0 again loop
		read(spi_cs0_fd, result + sizeof(uint8_t) * PACKET_SIZE * j, sizeof(uint8_t) * PACKET_SIZE);
		int packetNumber = result[j * PACKET_SIZE + 1];
		if (packetNumber != j) {
			j = -1;
			resets += 1;
			usleep(1000);
			//Note: we've selected 750 resets as an arbitrary limit, since there should never be 750 "null" packets between two valid transmissions at the current poll rate
			//By polling faster, developers may easily exceed this count, and the down period between frames may then be flagged as a loss of sync
			if (resets == 750) {
				SpiClosePort(0);
				lepton_reboot();
				n_wrong_segment = 0;
				n_zero_value_drop_frame = 0;
				usleep(750000);
				SpiOpenPort(0, spiSpeed);
			}
			continue;
		}
		if ((typeLepton == 3) && (packetNumber == 20)) {
			segmentNumber = (result[j * PACKET_SIZE] >> 4) & 0x0f;
			if ((segmentNumber < 1) || (4 < segmentNumber)) {
				log_message(10, "[ERROR] Wrong segment number " + std::to_string(segmentNumber));
				break;
			}
		}
	}
	if (resets >= 30) {
		log_message(3, "done reading, resets: " + std::to_string(resets));
	}


	//
	int iSegmentStart = 1;
	int iSegmentStop;
	if (typeLepton == 3) {
		if ((segmentNumber < 1) || (4 < segmentNumber)) {
			n_wrong_segment++;
			if ((n_wrong_segment % 12) == 0) {
				log_message(5, "[WARNING] Got wrong segment number continuously " + std::to_string(n_wrong_segment) + " times");
			}
			return image;
		}
		if (n_wrong_segment != 0) {
			log_message(8, "[WARNING] Got wrong segment number continuously " + std::to_string(n_wrong_segment) + " times [RECOVERED] : " + std::to_string(segmentNumber));
			n_wrong_segment = 0;
		}

		//
		memcpy(shelf[segmentNumber - 1], result, sizeof(uint8_t) * PACKET_SIZE * PACKETS_PER_FRAME);
		if (segmentNumber != 4) {
			return image;
		}
		iSegmentStop = 4;
	}
	else {
		memcpy(shelf[0], result, sizeof(uint8_t) * PACKET_SIZE * PACKETS_PER_FRAME);
		iSegmentStop = 1;
	}

	if ((autoRangeMin == true) || (autoRangeMax == true)) {
		if (autoRangeMin == true) {
			maxValue = 65535;
		}
		if (autoRangeMax == true) {
			maxValue = 0;
		}
		for (int iSegment = iSegmentStart; iSegment <= iSegmentStop; iSegment++) {
			for (int i = 0; i < FRAME_SIZE_UINT16; i++) {
				//skip the first 2 uint16_t's of every packet, they're 4 header bytes
				if (i % PACKET_SIZE_UINT16 < 2) {
					continue;
				}

				//flip the MSB and LSB at the last second
				uint16_t value = (shelf[iSegment - 1][i * 2] << 8) + shelf[iSegment - 1][i * 2 + 1];
				if (value == 0) {
					// Why this value is 0?
					continue;
				}
				if ((autoRangeMax == true) && (value > maxValue)) {
					maxValue = value;
				}
				if ((autoRangeMin == true) && (value < minValue)) {
					minValue = value;
				}
			}
		}
		diff = maxValue - minValue;
		scale = 255 / diff;
	}

	int row, column;
	uint16_t value;
	uint16_t valueFrameBuffer;
	
	for (int iSegment = iSegmentStart; iSegment <= iSegmentStop; iSegment++) {
		int ofsRow = 30 * (iSegment - 1);
		for (int i = 0; i < FRAME_SIZE_UINT16; i++) {
			//skip the first 2 uint16_t's of every packet, they're 4 header bytes
			if (i % PACKET_SIZE_UINT16 < 2) {
				continue;
			}

			//flip the MSB and LSB at the last second
			valueFrameBuffer = (shelf[iSegment - 1][i * 2] << 8) + shelf[iSegment - 1][i * 2 + 1];
			if (valueFrameBuffer == 0) {
				// Why this value is 0?
				n_zero_value_drop_frame++;
				if ((n_zero_value_drop_frame % 12) == 0) {
					log_message(5, "[WARNING] Found zero-value. Drop the frame continuously " + std::to_string(n_zero_value_drop_frame) + " times");
				}
				break;
			}

			//
			value = (valueFrameBuffer - minValue) * scale;
			int ofs_r = 3 * value + 0; if (colormapSize <= ofs_r) ofs_r = colormapSize - 1;
			int ofs_g = 3 * value + 1; if (colormapSize <= ofs_g) ofs_g = colormapSize - 1;
			int ofs_b = 3 * value + 2; if (colormapSize <= ofs_b) ofs_b = colormapSize - 1;
			if (typeLepton == 3) {
				column = (i % PACKET_SIZE_UINT16) - 2 + (myImageWidth / 2) * ((i % (PACKET_SIZE_UINT16 * 2)) / PACKET_SIZE_UINT16);
				row = i / PACKET_SIZE_UINT16 / 2 + ofsRow;
			}
			else {
				column = (i % PACKET_SIZE_UINT16) - 2;
				row = i / PACKET_SIZE_UINT16;
			}
			int index = row*myImageHeight +column*myImageWidth;
			image[index] = ofs_r;
			image[index+1] = ofs_g;
			image[index+2] = ofs_b;
		}
	}

	if (n_zero_value_drop_frame != 0) {
		log_message(8, "[WARNING] Found zero-value. Drop the frame continuously " + std::to_string(n_zero_value_drop_frame) + " times [RECOVERED]");
		n_zero_value_drop_frame = 0;
	}
	//finally, close SPI port just bcuz
	SpiClosePort(0);
	//return image_arr
	return image;
}

int* Lepton::get_image_values()
{
	//create the initial image
	int* image_value = new int [myImageHeight*myImageWidth];
	
	const int* colormap = selectedColormap;
	const int colormapSize = selectedColormapSize;
	uint16_t minValue = rangeMin;
	uint16_t maxValue = rangeMax;
	float diff = maxValue - minValue;
	float scale = 255 / diff;
	uint16_t n_wrong_segment = 0;
	uint16_t n_zero_value_drop_frame = 0;

	//open spi port
	SpiOpenPort(0, spiSpeed);

	

	//read data packets from lepton over SPI
	int resets = 0;
	int segmentNumber = -1;
	for (int j = 0; j < PACKETS_PER_FRAME; j++) {
		//if it's a drop packet, reset j to 0, set to -1 so he'll be at 0 again loop
		read(spi_cs0_fd, result + sizeof(uint8_t) * PACKET_SIZE * j, sizeof(uint8_t) * PACKET_SIZE);
		int packetNumber = result[j * PACKET_SIZE + 1];
		if (packetNumber != j) {
			j = -1;
			resets += 1;
			usleep(1000);
			//Note: we've selected 750 resets as an arbitrary limit, since there should never be 750 "null" packets between two valid transmissions at the current poll rate
			//By polling faster, developers may easily exceed this count, and the down period between frames may then be flagged as a loss of sync
			if (resets == 750) {
				SpiClosePort(0);
				lepton_reboot();
				n_wrong_segment = 0;
				n_zero_value_drop_frame = 0;
				usleep(750000);
				SpiOpenPort(0, spiSpeed);
			}
			continue;
		}
		if ((typeLepton == 3) && (packetNumber == 20)) {
			segmentNumber = (result[j * PACKET_SIZE] >> 4) & 0x0f;
			if ((segmentNumber < 1) || (4 < segmentNumber)) {
				log_message(10, "[ERROR] Wrong segment number " + std::to_string(segmentNumber));
				break;
			}
		}
	}
	if (resets >= 30) {
		log_message(3, "done reading, resets: " + std::to_string(resets));
	}


	//
	int iSegmentStart = 1;
	int iSegmentStop;
	if (typeLepton == 3) {
		if ((segmentNumber < 1) || (4 < segmentNumber)) {
			n_wrong_segment++;
			if ((n_wrong_segment % 12) == 0) {
				log_message(5, "[WARNING] Got wrong segment number continuously " + std::to_string(n_wrong_segment) + " times");
			}
			return image_value;
		}
		if (n_wrong_segment != 0) {
			log_message(8, "[WARNING] Got wrong segment number continuously " + std::to_string(n_wrong_segment) + " times [RECOVERED] : " + std::to_string(segmentNumber));
			n_wrong_segment = 0;
		}

		//
		memcpy(shelf[segmentNumber - 1], result, sizeof(uint8_t) * PACKET_SIZE * PACKETS_PER_FRAME);
		if (segmentNumber != 4) {
			return image_value;
		}
		iSegmentStop = 4;
	}
	else {
		memcpy(shelf[0], result, sizeof(uint8_t) * PACKET_SIZE * PACKETS_PER_FRAME);
		iSegmentStop = 1;
	}

	if ((autoRangeMin == true) || (autoRangeMax == true)) {
		if (autoRangeMin == true) {
			maxValue = 65535;
		}
		if (autoRangeMax == true) {
			maxValue = 0;
		}
		for (int iSegment = iSegmentStart; iSegment <= iSegmentStop; iSegment++) {
			for (int i = 0; i < FRAME_SIZE_UINT16; i++) {
				//skip the first 2 uint16_t's of every packet, they're 4 header bytes
				if (i % PACKET_SIZE_UINT16 < 2) {
					continue;
				}

				//flip the MSB and LSB at the last second
				uint16_t value = (shelf[iSegment - 1][i * 2] << 8) + shelf[iSegment - 1][i * 2 + 1];
				if (value == 0) {
					// Why this value is 0?
					continue;
				}
				if ((autoRangeMax == true) && (value > maxValue)) {
					maxValue = value;
				}
				if ((autoRangeMin == true) && (value < minValue)) {
					minValue = value;
				}
			}
		}
		diff = maxValue - minValue;
		scale = 255 / diff;
	}

	int row, column;
	uint16_t value;
	uint16_t valueFrameBuffer;
	
	for (int iSegment = iSegmentStart; iSegment <= iSegmentStop; iSegment++) {
		int ofsRow = 30 * (iSegment - 1);
		for (int i = 0; i < FRAME_SIZE_UINT16; i++) {
			//skip the first 2 uint16_t's of every packet, they're 4 header bytes
			if (i % PACKET_SIZE_UINT16 < 2) {
				continue;
			}

			//flip the MSB and LSB at the last second
			valueFrameBuffer = (shelf[iSegment - 1][i * 2] << 8) + shelf[iSegment - 1][i * 2 + 1];
			if (valueFrameBuffer == 0) {
				// Why this value is 0?
				n_zero_value_drop_frame++;
				if ((n_zero_value_drop_frame % 12) == 0) {
					log_message(5, "[WARNING] Found zero-value. Drop the frame continuously " + std::to_string(n_zero_value_drop_frame) + " times");
				}
				break;
			}

			//
			value = valueFrameBuffer;
			
			if (typeLepton == 3) {
				column = (i % PACKET_SIZE_UINT16) - 2 + (myImageWidth / 2) * ((i % (PACKET_SIZE_UINT16 * 2)) / PACKET_SIZE_UINT16);
				row = i / PACKET_SIZE_UINT16 / 2 + ofsRow;
			}
			else {
				column = (i % PACKET_SIZE_UINT16) - 2;
				row = i / PACKET_SIZE_UINT16;
			}
			int index = row*myImageHeight +column*myImageWidth;
			image_value[index]= value;
		}
	}

	if (n_zero_value_drop_frame != 0) {
		log_message(8, "[WARNING] Found zero-value. Drop the frame continuously " + std::to_string(n_zero_value_drop_frame) + " times [RECOVERED]");
		n_zero_value_drop_frame = 0;
	}
	//finally, close SPI port just bcuz
	SpiClosePort(0);
	//return image_arr
	return image_value;
}

void Lepton::log_message(uint16_t level, std::string msg)
{
	if (level <= loglevel) {
		std::cerr << msg << std::endl;
	}
}

int Lepton::get_width(){
	return this->myImageWidth;
}

int Lepton::get_height(){
	return this->myImageHeight;
}

extern "C"{
	int typeColormap = 3; // colormap_ironblack
	int typeLepton = 2; // Lepton 2.x
	int spiSpeed = 20; // SPI bus speed 20MHz
	int rangeMin = -1; //
	int rangeMax = -1; //
	int loglevel = 0;

	Lepton* Lepton_new() {
		Lepton* lepton = new Lepton();
		lepton->setLogLevel(loglevel);
		lepton->useColormap(typeColormap);
		lepton->useLepton(typeLepton);
		lepton->useSpiSpeedMhz(spiSpeed);
		lepton->setAutomaticScalingRange();
		if (0 <= rangeMin) lepton->useRangeMinValue(rangeMin);
		if (0 <= rangeMax) lepton->useRangeMaxValue(rangeMax);
		return lepton;
	}
	int Lepton_get_width(Lepton* lepton){return lepton->get_width();}
	int Lepton_get_height(Lepton* lepton){return lepton->get_height();}
	int* Lepton_get_image(Lepton* lepton){return lepton->get_image();}
	int* Lepton_get_image_value(Lepton* lepton){return lepton->get_image_values();}
}