import mediapipe as mp
import numpy as np


class FaceLocation(object):
    '''
    얼굴 위치를 담기 위한 클래스
    '''
    x:int
    y:int
    width:int
    height:int
    right_eye:object
    left_eye:object


class FaceDetector(object):
    '''
    얼굴 감지를 하기 위한 클래스
    '''
    def __init__(self, model_selection=0, min_detection_confidence=0.7) -> None:
        self.model_selection = model_selection
        self.min_detection_confidence = min_detection_confidence
        self.mp_face_detection = mp.solutions.face_detection
        self.face_detector = self.mp_face_detection.FaceDetection(
            model_selection=model_selection,
            min_detection_confidence=min_detection_confidence
        )


    def set_model_selection(self, model_selection) -> None:
        '''
        model_selection 값을 변경시킬 수는 있지만 필자도 무슨 차이인지 잘 모른다.
        :param model_selection:
        :return: None
        '''
        self.set_face_detector(model_selection, self.min_detection_confidence)

    def set_min_detection_confidence(self, min_detection_confidence) -> None:
        '''
        얼마나 확신 할 때 얼굴로 인식시킬 지 확률을 정한다.
        :param min_detection_confidence: 0.0~ 1.0 사이 값을 넣으면 된다.
        :return: None
        '''
        self.set_face_detector(self.model_selection, min_detection_confidence)

    def set_face_detector(self, model_selection, min_detection_confidence) -> None:
        '''
        model_selection과 min_detection_confidence를 동시에 설정하는 메소드다.
        :param model_selection: 필자도 잘 모르는 기능이고 기본값이 0이다.
        :param min_detection_confidence: 얼마나 확신할 때 얼굴로 인식할지 퍼센트다. 0.0~1.0 사이 값을 넣으면 된다.
        :return:
        '''
        self.face_detector = self.mp_face_detection.FaceDetection(
            model_selection=model_selection,
            min_detection_confidence=min_detection_confidence
        )

    def detect(self, image:np.ndarray) -> list[FaceLocation]:
        '''
        얼굴을 감지하고 위치를 담은 Face 객체들을 반환한다.
        :param image: 이미지
        :return: 얼굴 위치를 담은 Face를 반환한다.
        '''
        results = self.face_detector.process(image)
        faces:list[FaceLocation] = list()
        if results.detections:
            for detection in results.detections:
                box = detection.location_data.relative_bounding_box
                keypoints = detection.location_data.relative_keypoints

                h,w, _ = image.shape
                x = int(box.xmin * w)
                y = int(box.ymin * h)
                width = int(box.width * w)
                height = int(box.height * h)
                right_eye = keypoints[0]  # 오른쪽 눈
                left_eye = keypoints[1]
                face = FaceLocation()
                face.x = x
                face.y = y
                face.width = width
                face.height = height
                face.right_eye = right_eye
                face.left_eye = left_eye
            return faces

        else:
            return list()

