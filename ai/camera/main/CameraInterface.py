from abc import abstractmethod, ABCMeta
import numpy as np


class CameraInterface(metaclass=ABCMeta):
    '''
    카메라 클래스 만들 때 상속할 추상 클래스로 필수는 아니지만 개발할 때 도움이 될 것으로 보이기 때문에 작성함
    '''
    @abstractmethod
    def get_width(self) -> int:
        '''
        카메라의 가로 길이를 반환한다.
        :return: 가로 길이 int
        '''
        raise NotImplementedError

    @abstractmethod
    def get_height(self) -> int:
        '''
        카메라의 세로 길이를 반환한다.
        :return: 세로길이 int
        '''
        raise NotImplementedError

    @abstractmethod
    def get_image(self) -> np.ndarray:
        '''
        이미지를 numpy의 ndarray로 반환한다.
        :return: 이미지
        '''
        raise NotImplementedError
