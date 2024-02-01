import dlib
import cv2
import numpy as np


class EyeGlassDetector:
    '''
    테스트가 필요해 보임
    '''
    def __init__(self):
        pass

    def get_aligned_face(self, grey_img, left_eye, right_eye) -> np.ndarray:
        '''
        무슨 작업을 하는지 이해 못함
        :param grey_img: 이미지를 cv2.cvtColor(img, cv2.COLOR_RGB2GRAY) 함수를 사용해서 흑백으로 바꿔야함
        :param left_eye: 왼쪽 눈 위치
        :param right_eye: 오른쪽 눈 위치
        :return: aligned_face를 반환한다.
        '''
        desired_w = 256
        desired_h = 256
        desired_dist = desired_w * 0.5

        eyescenter = ((left_eye[0] + right_eye[0]) * 0.5, (left_eye[1] + right_eye[1]) * 0.5)  # 眉心
        dx = right_eye[0] - left_eye[0]
        dy = right_eye[1] - left_eye[1]
        dist = np.sqrt(dx * dx + dy * dy)
        scale = desired_dist / dist
        angle = np.degrees(np.arctan2(dy, dx))
        M = cv2.getRotationMatrix2D(eyescenter, angle, scale)

        tX = desired_w * 0.5
        tY = desired_h * 0.5
        M[0, 2] += (tX - eyescenter[0])
        M[1, 2] += (tY - eyescenter[1])

        aligned_face = cv2.warpAffine(grey_img, M, (desired_w, desired_h))
        return aligned_face

    def judge_eyeglass(self, aligned_face) -> bool:
        '''
        원리 이해 못함
        :param aligned_face: get_aligned_face메소드로 얻은 값 넣으면 됨
        :return: True면 안경 쓴거 False면 안경 안쓴거
        '''
        aligned_face = cv2.GaussianBlur(aligned_face, (11, 11), 0)

        sobel_y = cv2.Sobel(aligned_face, cv2.CV_64F, 0, 1, ksize=-1)
        sobel_y = cv2.convertScaleAbs(sobel_y)

        edgeness = sobel_y

        retVal, thresh = cv2.threshold(edgeness, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        d = len(thresh) * 0.5
        x = np.int32(d * 6 / 7)
        y = np.int32(d * 3 / 4)
        w = np.int32(d * 2 / 7)
        h = np.int32(d * 2 / 4)

        x_2_1 = np.int32(d * 1 / 4)
        x_2_2 = np.int32(d * 5 / 4)
        w_2 = np.int32(d * 1 / 2)
        y_2 = np.int32(d * 8 / 7)
        h_2 = np.int32(d * 1 / 2)

        roi_1 = thresh[y:y + h, x:x + w]
        roi_2_1 = thresh[y_2:y_2 + h_2, x_2_1:x_2_1 + w_2]
        roi_2_2 = thresh[y_2:y_2 + h_2, x_2_2:x_2_2 + w_2]
        roi_2 = np.hstack([roi_2_1, roi_2_2])

        measure_1 = sum(sum(roi_1 / 255)) / (np.shape(roi_1)[0] * np.shape(roi_1)[1])
        measure_2 = sum(sum(roi_2 / 255)) / (np.shape(roi_2)[0] * np.shape(roi_2)[1])
        measure = measure_1 * 0.3 + measure_2 * 0.7

        if measure > 0.15:
            judge = True
        else:
            judge = False

        return judge

    def detect(self):
        pass