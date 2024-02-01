from picamera2 import Picamera2
from ai.camera.main.CameraInterface import CameraInterface

width = 1280
height = 720

class Camera(CameraInterface):
    '''
    라즈베리파이 카메라를 제어한다.
    '''
    def __init__(self) -> None:
        self.pi_cam = Picamera2()
        self.pi_cam.preview_configuration.main.size = (width, height)
        self.pi_cam.preview_configuration.main.format = "RGB888"
        self.pi_cam.preview_configuration.align()
        self.pi_cam.configure("preview")
        self.width = width
        self.height = height

    def __enter__(self) -> 'Camera':
        '''
        with 문과 사용했을 경우
        :return:
        '''
        self.pi_cam.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.pi_cam.close()

    def get_image(self):
        return self.pi_cam.capture_array()

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

if __name__ == '__main__':
    with Camera() as cam:
        pass