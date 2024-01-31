import mediapipe as mp


class Face(object):
    x:int
    y:int
    width:int
    height:int
    right_eye:object
    left_eye:object


class FaceDetector(object):

    def __init__(self, model_selection=0, min_detection_confidence=0.7) -> None:
        self.model_selection = model_selection
        self.min_detection_confidence = min_detection_confidence
        self.mp_face_detection = mp.solutions.face_detection
        self.face_detector = self.mp_face_detection.FaceDetection(
            model_selection=model_selection,
            min_detection_confidence=min_detection_confidence
        )


    def set_model_selection(self, model_selection) -> None:
        self.set_face_detector(model_selection, self.min_detection_confidence)

    def set_min_detection_confidence(self, min_detection_confidence) -> None:
        self.set_face_detector(self.model_selection, min_detection_confidence)

    def set_face_detector(self, model_selection, min_detection_confidence) -> None:
        self.face_detector = self.mp_face_detection.FaceDetection(
            model_selection=model_selection,
            min_detection_confidence=min_detection_confidence
        )

    def detect(self, image) -> list[Face]:
        results = self.face_detector.process(image)
        faces:list[Face] = list()
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
                face = Face()
                face.x = x
                face.y = y
                face.width = width
                face.height = height
                face.right_eye = right_eye
                face.left_eye = left_eye
            return faces

        else:
            return list()

