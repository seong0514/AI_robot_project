from ai.camera.main.CameraInterface import CameraInterface
from ai.camera.main.FaceDetector import Face, FaceDetector
import math
import numpy as np
import cv2

class CameraManager:

    def __init__(self):
        pass

    def equalize_ratio(self, standard_camera:CameraInterface, target_camera:CameraInterface) -> tuple[int,int]:
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

        if (target_mul_width_ratio > standard_mul_width_ratio):
            mul = target_height // target_mul_height_ratio
            return (standard_mul_width_ratio*mul, target_height)
        elif (target_mul_height_ratio > standard_mul_height_ratio):
            mul = target_width // target_mul_width_ratio
            return (target_mul_width_ratio*mul, standard_mul_height_ratio*mul)
        else:
            mul = target_height // target_mul_height_ratio
            return (target_mul_width_ratio*mul,target_mul_height_ratio*mul)


    def cut_image(self, image:np.ndarray, target_width, target_height, move_x=0,move_y=0):
        image_height, image_width,_ = image.shape
        width_diff = image_width - target_width
        height_diff = image_height - target_height
        width_start = width_diff//2 +move_x
        height_start = height_diff//2 + move_y
        width_end = image_width - width_diff//2 + move_x
        height_end = image_height - height_diff//2 - move_y
        new_image = image[width_start:width_end,height_start:height_end]
        return new_image

    def get_ratio_point(self, from_image_shape, target_image_shape, from_point):
        from_width, from_height,_ = from_image_shape
        target_width, target_height,_ = target_image_shape
        from_point_x, from_point_y = from_point
        width_gcd = math.gcd(from_width, from_point_x)
        height_gcd = math.gcd(from_height, from_point_y)
        from_width_ratio, from_point_width_ratio = (from_width/width_gcd, from_point_x/width_gcd)
        from_height_ratio, from_point_height_ratio = (from_height/height_gcd, from_point_y/height_gcd)
        target_point_x = target_width*from_point_width_ratio//from_width_ratio
        target_point_y = target_height*from_point_height_ratio//from_height_ratio
        return (target_point_x, target_point_y)

    def point_dot(self, image, x,y, color, thickness=1):
        new_image = image.copy()
        cv2.line(image,(x,y),(x,y), color, thickness)




