#pragma once

#ifndef LeptonExport
#define LeptonExport

#include <ctime>
#include <stdint.h>

#define PACKET_SIZE 164
#define PACKET_SIZE_UINT16 (PACKET_SIZE/2)
#define PACKETS_PER_FRAME 60
#define FRAME_SIZE_UINT16 (PACKET_SIZE_UINT16*PACKETS_PER_FRAME)

class Lepton
{
public: 
	Lepton(void);
	~Lepton();

	void setLogLevel(uint16_t);
	void useColormap(int);
	void useLepton(int);
	void useSpiSpeedMhz(unsigned int);
	void setAutomaticScalingRange();
	void useRangeMinValue(uint16_t);
	void useRangeMaxValue(uint16_t);
	int* get_image();
	int get_width();
	int get_height();
	int* get_image_values();

private:

	void log_message(uint16_t, std::string);
	uint16_t loglevel;
	int typeColormap;
	const int* selectedColormap;
	int selectedColormapSize;
	int typeLepton;
	unsigned int spiSpeed;
	bool autoRangeMin;
	bool autoRangeMax;
	uint16_t rangeMin;
	uint16_t rangeMax;
	int myImageWidth;
	int myImageHeight;

	uint8_t result[PACKET_SIZE * PACKETS_PER_FRAME];
	uint8_t shelf[4][PACKET_SIZE * PACKETS_PER_FRAME];
	uint16_t* frameBuffer;

};

#endif