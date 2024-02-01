from ai.camera.main.CameraInterface import CameraInterface
from ai.camera.main.FaceDetector import FaceLocation, FaceDetector
from ai.camera.main.Lepton import Lepton
from ai.camera.main.Camera import Camera
import math
import numpy as np
import cv2


class CameraManager:
    '''
    여기에서 라즈베리파이 카메라와 열화상 카메라를 제어할 예정입니다.
    '''

    def __init__(self):
        self.face_detector = FaceDetector()

    def equalize_ratio(self, standard_camera: CameraInterface, target_camera: CameraInterface) -> tuple[int, int]:
        '''
        현재 프로젝트에서 라즈베리파이 카메라와 렙톤의 카메라의 비율이 일치하지 않는데 카메라 비율을 맞추기 위해

        라즈베리파이 카메라의 일부를 잘라내야 하는데 어떻게 잘라야 하는지 구하는 함수
        :param standard_camera: 기준이 되는 카메라 예시) Lepton 카메라
        :param target_camera: 일부를 잘라낼 카메라 예시) 라즈베리파이 카메라
        :return: 잘라내고 난 다음의 카메라 픽셀 수를 반환한다 (가로, 세로)
        '''

        standard_width = standard_camera.get_width()
        standard_height = standard_camera.get_height()
        target_width = target_camera.get_width()
        target_height = target_camera.get_height()

        standard_gcd = math.gcd(standard_width, standard_height)
        standard_width_ratio = standard_width // standard_gcd
        standard_height_ratio = standard_height // standard_gcd

        target_gcd = math.gcd(target_width, target_height)
        target_width_ratio = target_width // target_gcd
        target_height_ratio = target_height // target_gcd

        width_lcm = math.lcm(standard_width_ratio, target_width_ratio)
        height_lcm = math.lcm(standard_height_ratio, target_height_ratio)

        standard_mul_height_ratio = standard_height_ratio * width_lcm // standard_width_ratio
        target_mul_height_ratio = target_height_ratio * width_lcm // target_width_ratio
        standard_mul_width_ratio = standard_width_ratio * height_lcm // standard_height_ratio
        target_mul_width_ratio = target_width_ratio * height_lcm // target_height_ratio

        if target_mul_width_ratio > standard_mul_width_ratio:
            mul = target_height // target_mul_height_ratio
            return standard_mul_width_ratio * mul, target_height
        elif target_mul_height_ratio > standard_mul_height_ratio:
            mul = target_width // target_mul_width_ratio
            return target_mul_width_ratio * mul, standard_mul_height_ratio * mul
        else:
            mul = target_height // target_mul_height_ratio
            return target_mul_width_ratio * mul, target_mul_height_ratio * mul

    def cut_image(self, image: np.ndarray, target_width, target_height, move_x=0, move_y=0) -> np.ndarray:
        '''
        이미지를 자르는 함수다.

        기본적으로는 중앙을 중심으로 양 끝을 자른다.
        :param image: 자를 이미지
        :param target_width: 자를 가로 길이
        :param target_height: 자를 세로 길이
        :param move_x: 선택적) 자를 범위 x축으로 이동 양수면 오른쪽 방향 음수면 왼쪽 방향
        :param move_y: 선택적) 자를 범위 y축으로 이동 양수면 위쪽 음수면 아래쪽
        :return: 매개변수의 image를 복제하고 자른 이미지
        '''
        image_height, image_width, _ = image.shape
        width_diff = image_width - target_width
        height_diff = image_height - target_height
        width_start = width_diff // 2 + move_x
        height_start = height_diff // 2 + move_y
        width_end = image_width - width_diff // 2 + move_x
        height_end = image_height - height_diff // 2 - move_y
        new_image = image[width_start:width_end, height_start:height_end]
        return new_image

    def get_ratio_point(self,
                        from_image_shape: tuple[int, int, int],
                        target_image_shape: tuple[int, int, int],
                        from_point: tuple[int, int]
                        ) -> tuple[float, float]:
        '''
        A와 B 이미지의 크기가 다를 경우 A의 점위치를 B의 점에 대칭 시키기 위해 비율로 계산해 B에서의 점 위치를 계산하는 함수
        :param from_image_shape: 위 설명에서의 A 이미지의 크기
        :param target_image_shape: 위 설명에서의 B 이미지 크기
        :param from_point: 위 설명 에서의 A이미지의 점 위치
        :return: 위 설명 에서의 B이미지의 점 위치
        '''
        from_width, from_height, _ = from_image_shape
        target_width, target_height, _ = target_image_shape
        from_point_x, from_point_y = from_point
        width_gcd = math.gcd(from_width, from_point_x)
        height_gcd = math.gcd(from_height, from_point_y)
        from_width_ratio, from_point_width_ratio = (from_width / width_gcd, from_point_x / width_gcd)
        from_height_ratio, from_point_height_ratio = (from_height / height_gcd, from_point_y / height_gcd)
        target_point_x = target_width * from_point_width_ratio // from_width_ratio
        target_point_y = target_height * from_point_height_ratio // from_height_ratio
        return target_point_x, target_point_y

    def point_dot(self, image: np.ndarray, x: int, y: int, color: tuple[int, int, int],
                  thickness: int = 1) -> np.ndarray:
        '''
        이미지에 점을 찍어 표시하기 위한 함수

        테스트용으로 사용할 예정이다.
        :param image:
        :param x:
        :param y:
        :param color:
        :param thickness:
        :return:
        '''
        new_image = image.copy()
        cv2.line(new_image, (x, y), (x, y), color, thickness)
        return new_image

    def show_images(self):
        with Lepton() as lepton, Camera() as camera:
            lepton_image = lepton.get_image()
            camera_image = camera.get_image()
