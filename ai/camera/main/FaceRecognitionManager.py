import face_recognition
import numpy as np


class NamedFace(object):
    image:np.ndarray

class FaceRecognitionManager(object):
    '''
    얼굴 인식을 담당하는 클래스

    '''
    # 이건 static 변수로 쓸 예정
    # 얼굴 들을 구분하기 위한 용도로 각 얼굴마다 할당할 예정
    # 첫 실행에는 문제가 없지만 두번 이상 부터는 set_pre_face_id 메소드를 통해 id 값을 설정하고 시작해야함
    pre_face_id:int = 0

    def __init__(self) -> None:
        self.known_face_ids:list[int] = []
        self.known_face_encodings:list[np.array] = []

    @staticmethod
    def set_pre_face_id(pre_id: int) -> None:
        '''
        pre_face_id를 설정하는 static method로 객체 생성을 하지 않아도 호출 가능
        :param pre_id: 데이터 베이스에 저장된 값
        :return: None
        '''
        FaceRecognitionManager.pre_face_id = pre_id
        return

    def add_known_face(self, face_id, face_encoding) -> None:
        '''
        새로운 얼굴을 인식시키는 작업
        :param face_id: get_new_face_id 메소드를 통해서 id 값을 가져와서 실행시키길 바람
        :param face_encoding: encoding 된 얼굴 값
        :return: None
        '''
        self.known_face_ids.append(face_id)
        self.known_face_encodings.append(face_encoding)
        return


    def get_new_face_id(self) -> int:
        '''
        static 변수인 pre_face_id 값에 1을 더해서 가져옴
        :return: 기존 pre_face_id에 1을 더한 값
        '''
        FaceRecognitionManager.pre_face_id += 1
        return FaceRecognitionManager.pre_face_id

    def recognize_face(self, image, face_locations) -> list[int]:
        '''
        얼굴 인식 하는 메소드
        :param image: 전체 사진
        :param face_locations: (top, right, bottom, left)로 이루어진 tuple 값
        :return: 인식한 face_id 값들
        '''
        face_encodings = face_recognition.face_encodings(image, face_locations)
        face_ids:list[int] = []
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
            for match_index, match in enumerate(matches):
                if match:
                    face_id = self.known_face_ids[match_index]
                    break
            else:
                face_id = self.get_new_face_id()
                self.add_known_face(face_id, face_encoding)
            face_ids.append(face_id)
        return face_ids







