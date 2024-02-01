# 카메라

---

## Lepton
아마 Lepton 폴더에 libLepton.so 파일이 있을겁니다.<br>
만약 없다면 Lepton 폴더에 가셔서
```shell
sudo apt install gcc
sudo apt install g++
source ./maker
```
를 실행시키면 libLepton.so 파일이 만들어 질 겁니다.<br>
만약 Lepton.cpp 파일을 수정하신다고 해도 위의 방법으로 라이브러리를 업데이트 시킬 수 있습니다.<br>

## raspberry pi camera

이건 라즈베리파이 운영체제에서만 가능합니다.
```shell
pip install picamera2
```

## 웹캠

아직 이걸 구현하지는 않았지만 사용하고 싶으면 아래 명령어를 작성하셔야 합니다.
```shell
pip install opencv-python
```


---

# 얼굴 감지, 인식

---

## 얼굴 인식

얼굴을 인식시키는 파이썬 코드는 FaceRecognitionManager.py로

여기에는 face_recognition 모듈이 있다. 이 모듈은 dlib라는 라이브러리를 기반으로 만들어 졌는데

windows 운영체제에도 있기는 하지만 리눅스에 비해 낮은 버전이라서 호환이 잘 되지 않는다.

그래서 ubuntu나 rasbian 처럼 리눅스 환경에서 돌려야 한다.

```shell
sudo apt install cmake
pip install cmake
pip install face_recognition
```

## 얼굴 감지
얼굴을 감지하는 파이썬 코드는 FaceDetection으로 여러 모듈을 사용한다.
```shell
pip install mediapipe
pip install numpy
```