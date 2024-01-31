import ctypes
import numpy as np
from ai.camera.main.CameraInterface import CameraInterface
import os
import sys

# 이 라이브러리를 블러올 때 상대 경로를 사용하는데 import 할 시 발생하는 경로 불일치를 막기 위해서 길어짐
leptonLibPath = os.path.join(os.path.join(os.path.split(os.path.join(os.getcwd(), __file__))[0], "Lepton\libLepton.so"))


class Lepton(CameraInterface):
    '''
    Lepton 2.5를 사용한다.
    리눅스 환경에서 작동하고 현재는 Ubuntu에서 빌드한 라이브러리를 사용 중

    '''

    def __init__(self) -> None:
        self.mylib = ctypes.CDLL(leptonLibPath)
        self.mylib.Lepton_new.restype = ctypes.POINTER(ctypes.c_int)
        self.lepton = self.mylib.Lepton_new()

    def get_width(self) -> int:
        return self.mylib.Lepton_get_width(self.lepton)

    def get_height(self) -> int:
        return self.mylib.Lepton_get_height(self.lepton)

    def get_image(self) -> np.ndarray:
        image_ctype = self.mylib.Lepton_get_image(self.lepton)
        image_np = np.ctypeslib.as_array(image_ctype, shape=(self.get_height(), self.get_width(), 3))
        return image_np

    def get_image_value(self) -> np.ndarray:
        '''

        :return: 0.01K 단위일 수 있음 섭씨로 바꾸려면 (value-27315)*0.01 부동소수점으로 바꾸면 값이 애매해지므로 왠만해서는 정수의 형태를 유지할 것
        '''
        image_value_ctype = self.mylib.Lepton_get_image_value(self.lepton)
        image_value_np = np.ctypeslib.as_array(image_value_ctype, shape=(self.get_height(), self.get_width()))
        return image_value_np
