# strategies/camera/opencv_camera.py
"""
OpenCV 기반 카메라 구현체
"""
import cv2
import numpy as np
from typing import Optional, Tuple
from strategies.base.camera_strategy import CameraStrategy


class OpenCVCamera(CameraStrategy):
    """OpenCV를 사용한 카메라 구현체"""
    
    def __init__(self, camera_index: int = 0):
        self.camera_index = camera_index
        self.cap: Optional[cv2.VideoCapture] = None
        self.is_initialized = False
    
    def initialize(self) -> bool:
        """카메라 초기화"""
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            if not self.cap.isOpened():
                return False
            
            # 카메라 설정
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            self.is_initialized = True
            return True
        except Exception as e:
            print(f"카메라 초기화 실패: {e}")
            return False
    
    def get_frame(self) -> Optional[np.ndarray]:
        """현재 프레임 가져오기"""
        if not self.is_initialized or self.cap is None:
            return None
        
        ret, frame = self.cap.read()
        if ret:
            return frame
        return None
    
    def capture_photo(self) -> Optional[np.ndarray]:
        """사진 촬영"""
        return self.get_frame()
    
    def release(self) -> None:
        """카메라 리소스 해제"""
        if self.cap is not None:
            self.cap.release()
        self.is_initialized = False
    
    def is_connected(self) -> bool:
        """카메라 연결 상태 확인"""
        return self.is_initialized and self.cap is not None and self.cap.isOpened()
    
    def get_resolution(self) -> Tuple[int, int]:
        """카메라 해상도 가져오기"""
        if not self.is_connected():
            return (0, 0)
        
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return (width, height)


# strategies/ocr/tesseract_ocr.py
"""
Tesseract OCR 구현체
"""
import cv2
import numpy as np
import pytesseract
from typing import List
from strategies.base.ocr_strategy import OCRStrategy, OCRResult


class TesseractOCR(OCRStrategy):
    """Tesseract를 사용한 OCR 구현체"""
    
    def __init__(self, language: str = 'kor+eng'):
        self.language = language
        # Tesseract 실행 파일 경로 설정 (Windows의 경우)
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    
    def extract_text(self, image: np.ndarray) -> List[OCRResult]:
        """이미지에서 텍스트 추출"""
        if not self.is_available():
            return []
        
        try:
            # 이미지 전처리
            processed_image = self.preprocess_image(image)
            
            # OCR 수행 (신뢰도 포함)
            data = pytesseract.image_to_data(
                processed_image, 
                lang=self.language, 
                output_type=pytesseract.Output.DICT
            )
            
            results = []
            texts = []
            
            # 단어별 결과 수집
            for i in range(len(data['text'])):
                text = data['text'][i].strip()
                confidence = float(data['conf'][i])
                
                if text and confidence > 30:  # 신뢰도 30% 이상만
                    bbox = [data['left'][i], data['top'][i], data['width'][i], data['height'][i]]
                    results.append(OCRResult(text, confidence, bbox))
                    texts.append(text)
            
            # 전체 텍스트도 추가
            if texts:
                full_text = ' '.join(texts)
                overall_confidence = sum(r.confidence for r in results) / len(results) if results else 0
                results.insert(0, OCRResult(full_text, overall_confidence))
            
            # 신뢰도 순으로 정렬
            results.sort(key=lambda x: x.confidence, reverse=True)
            
            return results
            
        except Exception as e:
            print(f"OCR 처리 중 오류: {e}")
            return []
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """OCR 전 이미지 전처리"""
        # 그레이스케일 변환
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # 노이즈 제거
        denoised = cv2.medianBlur(gray, 5)
        
        # 이진화
        _, binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return binary
    
    def is_available(self) -> bool:
        """OCR 엔진 사용 가능 여부 확인"""
        try:
            # 간단한 테스트 이미지로 확인
            test_image = np.ones((100, 100), dtype=np.uint8) * 255
            pytesseract.image_to_string(test_image)
            return True
        except Exception:
            return False
    
    def get_supported_languages(self) -> List[str]:
        """지원하는 언어 목록 반환"""
        try:
            langs = pytesseract.get_languages()
            return langs
        except Exception:
            return ['eng', 'kor']  # 기본값


# strategies/storage/dropbox_local.py
"""
Dropbox 로컬 동기화 폴더 저장 구현체
"""
import cv2
import os
from pathlib import Path
from typing import Optional, Dict, Any
import numpy as np
from strategies.base.storage_strategy import StorageStrategy, StorageResult


class DropboxLocal(StorageStrategy):
    """Dropbox 로컬 동기화 폴더에 저장하는 구현체"""
    
    def __init__(self, dropbox_path: Optional[str] = None):
        if dropbox_path:
            self.base_path = Path(dropbox_path)
        else:
            # 기본 Dropbox 경로 시도
            home = Path.home()
            possible_paths = [
                home / "Dropbox",
                home / "Dropbox (Personal)",
                home / "Dropbox (Business)",
            ]
            
            self.base_path = None
            for path in possible_paths:
                if path.exists():
                    self.base_path = path
                    break
            
            if self.base_path is None:
                # Dropbox가 없으면 홈 디렉토리에 생성
                self.base_path = home / "PhotoCapture"
                self.base_path.mkdir(exist_ok=True)
    
    def save_image(self, image: np.ndarray, file_path: str, 
                   metadata: Optional[Dict[str, Any]] = None) -> StorageResult:
        """이미지 저장"""
        try:
            full_path = self.get_full_path(file_path)
            full_path_obj = Path(full_path)
            
            # 디렉토리 생성
            full_path_obj.parent.mkdir(parents=True, exist_ok=True)
            
            # 이미지 저장
            success = cv2.imwrite(str(full_path_obj), image)
            
            if success:
                return StorageResult(
                    success=True,
                    file_path=str(full_path_obj),
                    metadata=metadata
                )
            else:
                return StorageResult(
                    success=False,
                    error_message="이미지 저장 실패"
                )
                
        except Exception as e:
            return StorageResult(
                success=False,
                error_message=f"저장 중 오류: {str(e)}"
            )
    
    def create_directory(self, dir_path: str) -> bool:
        """디렉토리 생성"""
        try:
            full_path = Path(self.get_full_path(dir_path))
            full_path.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            print(f"디렉토리 생성 실패: {e}")
            return False
    
    def exists(self, file_path: str) -> bool:
        """파일/디렉토리 존재 여부 확인"""
        full_path = Path(self.get_full_path(file_path))
        return full_path.exists()
    
    def get_base_path(self) -> str:
        """기본 저장 경로 반환"""
        return str(self.base_path)
    
    def get_full_path(self, relative_path: str) -> str:
        """상대 경로를 절대 경로로 변환"""
        return str(self.base_path / relative_path)


# strategies/filename/standard_naming.py
"""
표준 파일명 규칙 구현체
파일명 형식: "03.물품사진_yymmdd_USER_OCR내용.jpg"
"""
import re
from datetime import datetime
from typing import Optional, Dict, Any
from strategies.base.filename_strategy import FilenameStrategy, FilenameComponents


class StandardNaming(FilenameStrategy):
    """표준 파일명 규칙 구현체"""
    
    def __init__(self):
        self.prefix = "03.물품사진"
        self.max_content_length = 50  # OCR 내용 최대 길이
    
    def generate_filename(self, user: str, ocr_content: str, 
                         timestamp: Optional[datetime] = None,
                         metadata: Optional[Dict[str, Any]] = None) -> str:
        """파일명 생성"""
        if timestamp is None:
            timestamp = datetime.now()
        
        # 날짜 형식: yymmdd
        date_str = timestamp.strftime("%y%m%d")
        
        # 사용자명과 OCR 내용 정제
        clean_user = self.sanitize_text(user)
        clean_content = self.sanitize_text(ocr_content)
        
        # OCR 내용 길이 제한
        if len(clean_content) > self.max_content_length:
            clean_content = clean_content[:self.max_content_length]
        
        # 파일명 조합
        filename = f"{self.prefix}_{date_str}_{clean_user}_{clean_content}.jpg"
        
        return filename
    
    def generate_folder_name(self, timestamp: Optional[datetime] = None) -> str:
        """폴더명 생성"""
        if timestamp is None:
            timestamp = datetime.now()
        
        # 형식: "YY년 MM월"
        folder_name = timestamp.strftime("%y년 %m월")
        return folder_name
    
    def sanitize_text(self, text: str) -> str:
        """파일명에 사용할 수 없는 문자 제거/변환"""
        if not text:
            return "Unknown"
        
        # 파일명에 사용할 수 없는 문자들 제거
        forbidden_chars = r'[<>:"/\\|?*\x00-\x1f]'
        sanitized = re.sub(forbidden_chars, '', text)
        
        # 연속된 공백을 하나로 변경
        sanitized = re.sub(r'\s+', ' ', sanitized)
        
        # 앞뒤 공백 제거
        sanitized = sanitized.strip()
        
        # 비어있으면 기본값
        if not sanitized:
            sanitized = "Unknown"
        
        return sanitized
    
    def validate_filename(self, filename: str) -> bool:
        """파일명 유효성 검사"""
        if not filename:
            return False
        
        # 길이 검사 (Windows 기준 255자)
        if len(filename) > 255:
            return False
        
        # 금지된 문자 검사
        forbidden_chars = r'[<>:"/\\|?*\x00-\x1f]'
        if re.search(forbidden_chars, filename):
            return False
        
        # 확장자 검사
        if not filename.lower().endswith('.jpg'):
            return False
        
        return True
    
    def parse_filename(self, filename: str) -> Optional[FilenameComponents]:
        """파일명에서 구성 요소 추출"""
        try:
            # 확장자 제거
            name_without_ext = filename.replace('.jpg', '').replace('.JPG', '')
            
            # 패턴 매칭: prefix_yymmdd_user_content
            pattern = r'^(.+?)_(\d{6})_([^_]+)_(.+)$'
            match = re.match(pattern, name_without_ext)
            
            if match:
                prefix, date_str, user, content = match.groups()
                return FilenameComponents(
                    prefix=prefix,
                    date_str=date_str,
                    user=user,
                    content=content,
                    extension="jpg"
                )
            
            return None
            
        except Exception:
            return None
