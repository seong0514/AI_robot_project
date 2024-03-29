import cv2
from ai.camera.main.CameraInterface import CameraInterface

class WebCam(CameraInterface):
    '''
    windows 환경에서 테스트하기 위해서 만들어 보긴 했는데 실사용은 안할 것으로 보임
    '''

    def __init__(self):
        pass

    def __enter__(self):
        self.webcam = cv2.VideoCapture(0)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.webcam.release()
        cv2.destroyAllWindows()

    def get_image(self):
        status, frame = self.webcam.read()
        return frame

    def get_width(self) -> int:
        return 1280

    def get_height(self) -> int:
        return 720


if __name__ == '__main__':
    with WebCam() as webcam:
        image = webcam.get_image()

