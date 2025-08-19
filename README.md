# 사진 촬영 및 OCR 애플리케이션

전략 패턴(Strategy Pattern)을 사용하여 설계된 데스크톱 애플리케이션입니다. 웹캠으로 사진을 촬영하고, OCR로 텍스트를 추출하여 Dropbox 동기화 폴더에 체계적으로 저장합니다.

## 주요 기능

- **웹캠 사진 촬영**: OpenCV를 사용한 실시간 카메라 뷰 및 촬영
- **OCR 텍스트 추출**: Tesseract OCR을 사용한 이미지 텍스트 인식
- **자동 파일 관리**: 날짜별 폴더 자동 생성 및 규칙 기반 파일명
- **사용자 관리**: 텍스트 파일 기반 사용자 목록 관리
- **확장 가능한 아키텍처**: 전략 패턴으로 각 기능 모듈 교체 가능

## 파일명 규칙

```
03.물품사진_yymmdd_USER_OCR내용.jpg
```

**예시**: `03.물품사진_241201_김철수_컴퓨터모니터.jpg`

## 폴더 구조

```
YY년 MM월/
├── 03.물품사진_241201_김철수_컴퓨터모니터.jpg
├── 03.물품사진_241201_이영희_키보드.jpg
└── ...
```

## 설치 요구사항

### 1. Python 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. Tesseract OCR 설치

#### Windows
1. [Tesseract 다운로드](https://github.com/UB-Mannheim/tesseract/wiki)
2. 설치 후 한국어 언어팩 포함 확인
3. 설치 경로가 다른 경우 `strategies/ocr/tesseract_ocr.py`에서 경로 수정

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install tesseract-ocr tesseract-ocr-kor
```

#### macOS
```bash
brew install tesseract tesseract-lang
```

### 3. 웹캠 준비
- USB 웹캠 또는 내장 카메라
- 카메라 권한 허용 필요

## 실행 방법

```bash
python main.py
```

## 사용 방법

1. **애플리케이션 실행**
   - `python main.py` 실행
   - 카메라 연결 확인

2. **사용자 선택**
   - 우측 패널에서 사용자 드롭다운 선택
   - 새 사용자 추가: `config/user_list.txt` 파일 편집

3. **사진 촬영**
   - "사진 촬영" 버튼 클릭
   - 자동으로 OCR 분석 수행

4. **OCR 결과 확인**
   - 여러 후보 중 선택하거나 직접 수정
   - 신뢰도가 높은 순으로 정렬 표시

5. **사진 저장**
   - "사진 저장" 버튼 클릭
   - 자동으로 날짜별 폴더에 저장

## 설정 파일

### config/user_list.txt
```text
# 사용자 목록 파일
김철수
이영희
박민수
최은정
관리자
```

### Dropbox 동기화 폴더
- 자동으로 다음 경로를 순서대로 탐색:
  - `~/Dropbox`
  - `~/Dropbox (Personal)`
  - `~/Dropbox (Business)`
  - `~/PhotoCapture` (최종 대안)

## 전략 패턴 아키텍처

### 교체 가능한 전략들

#### 1. CameraStrategy (카메라 전략)
- **현재**: `OpenCVCamera` (OpenCV 기반)
- **확장 가능**: IP 카메라, 전용 카메라 SDK

#### 2. OCRStrategy (OCR 전략)  
- **현재**: `TesseractOCR` (Tesseract 기반)
- **확장 가능**: `EasyOCR`, Google Vision API, Azure OCR

#### 3. StorageStrategy (저장 전략)
- **현재**: `DropboxLocal` (로컬 폴더)
- **확장 가능**: Dropbox API, Google Drive, AWS S3

#### 4. FilenameStrategy (파일명 전략)
- **현재**: `StandardNaming` (고정 규칙)
- **확장 가능**: Excel 연동, 데이터베이스 기반, 사용자 정의

### 새로운 전략 추가 방법

1. **추상 클래스 상속**
```python
from strategies.base.ocr_strategy import OCRStrategy

class EasyOCR(OCRStrategy):
    def extract_text(self, image):
        # EasyOCR 구현
        pass
```

2. **main.py에서 교체**
```python
# ocr_strategy = TesseractOCR()  # 기존
ocr_strategy = EasyOCR()        # 새로운 전략
```

## 프로젝트 구조

```
photo_capture_app/
├── main.py                     # 진입점
├── requirements.txt            # 의존성
├── config/
│   ├── settings.py            # 설정값
│   └── user_list.txt          # 사용자 목록
├── strategies/                # 전략 패턴 구현
│   ├── base/                  # 추상 클래스들
│   ├── camera/                # 카메라 전략
│   ├── ocr/                   # OCR 전략
│   ├── storage/               # 저장 전략
│   └── filename/              # 파일명 전략
├── ui/                        # PyQt5 UI
├── controllers/               # 컨트롤러
└── utils/                     # 유틸리티
```

## 트러블슈팅

### 카메라 관련
- **카메라 인식 안됨**: 다른 애플리케이션에서 카메라 사용 중인지 확인
- **권한 오류**: 카메라 접근 권한 허용 필요

### OCR 관련
- **Tesseract 오류**: 설치 경로 확인 및 언어팩 설치
- **인식률 낮음**: 조명 개선, 텍스트 크기 조정

### 저장 관련
- **Dropbox 폴더 없음**: 수동으로 경로 지정 또는 기본 폴더 사용
- **권한 오류**: 폴더 쓰기 권한 확인

## 개발자 정보

- **아키텍처**: 전략 패턴(Strategy Pattern)
- **GUI 프레임워크**: PyQt5
- **컴퓨터 비전**: OpenCV
- **OCR 엔진**: Tesseract OCR
- **확장성**: 모듈 교체 가능한 구조

## 라이선스

Apache License 2.0
