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
        '''
        raise NotImplementedError

    @abstractmethod
    def get_height(self) -> int:
        '''
        
        '''
        raise NotImplementedError

    @abstractmethod
    def get_image(self) -> np.ndarray:
        raise NotImplementedError
