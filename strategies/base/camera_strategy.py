# strategies/base/camera_strategy.py
"""
카메라 전략 추상 클래스
웹캠 제어 및 촬영 기능의 인터페이스를 정의
"""
from abc import ABC, abstractmethod
from typing import Optional, Tuple
import numpy as np


class CameraStrategy(ABC):
    """카메라 전략 추상 클래스"""
    
    @abstractmethod
    def initialize(self) -> bool:
        """
        카메라 초기화
        Returns:
            bool: 초기화 성공 여부
        """
        pass
    
    @abstractmethod
    def get_frame(self) -> Optional[np.ndarray]:
        """
        현재 프레임 가져오기
        Returns:
            Optional[np.ndarray]: 현재 프레임 이미지 (BGR 형식)
        """
        pass
    
    @abstractmethod
    def capture_photo(self) -> Optional[np.ndarray]:
        """
        사진 촬영
        Returns:
            Optional[np.ndarray]: 촬영된 이미지 (BGR 형식)
        """
        pass
    
    @abstractmethod
    def release(self) -> None:
        """카메라 리소스 해제"""
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """
        카메라 연결 상태 확인
        Returns:
            bool: 연결 상태
        """
        pass
    
    @abstractmethod
    def get_resolution(self) -> Tuple[int, int]:
        """
        카메라 해상도 가져오기
        Returns:
            Tuple[int, int]: (width, height)
        """
        pass


# strategies/base/ocr_strategy.py
"""
OCR 전략 추상 클래스
이미지에서 텍스트 추출 기능의 인터페이스를 정의
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import numpy as np


class OCRResult:
    """OCR 결과를 담는 데이터 클래스"""
    
    def __init__(self, text: str, confidence: float = 0.0, bbox: Optional[List[int]] = None):
        self.text = text.strip()
        self.confidence = confidence
        self.bbox = bbox or []  # [x, y, width, height]
    
    def __str__(self):
        return f"Text: '{self.text}', Confidence: {self.confidence:.2f}"


class OCRStrategy(ABC):
    """OCR 전략 추상 클래스"""
    
    @abstractmethod
    def extract_text(self, image: np.ndarray) -> List[OCRResult]:
        """
        이미지에서 텍스트 추출
        Args:
            image: 입력 이미지 (BGR 또는 RGB 형식)
        Returns:
            List[OCRResult]: OCR 결과 리스트 (신뢰도 순으로 정렬)
        """
        pass
    
    @abstractmethod
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        OCR 전 이미지 전처리
        Args:
            image: 원본 이미지
        Returns:
            np.ndarray: 전처리된 이미지
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        OCR 엔진 사용 가능 여부 확인
        Returns:
            bool: 사용 가능 여부
        """
        pass
    
    @abstractmethod
    def get_supported_languages(self) -> List[str]:
        """
        지원하는 언어 목록 반환
        Returns:
            List[str]: 언어 코드 리스트 (예: ['ko', 'en'])
        """
        pass


# strategies/base/storage_strategy.py
"""
저장 전략 추상 클래스
파일 저장 기능의 인터페이스를 정의
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from pathlib import Path
import numpy as np


class StorageResult:
    """저장 결과를 담는 데이터 클래스"""
    
    def __init__(self, success: bool, file_path: Optional[str] = None, 
                 error_message: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None):
        self.success = success
        self.file_path = file_path
        self.error_message = error_message
        self.metadata = metadata or {}
    
    def __str__(self):
        if self.success:
            return f"저장 성공: {self.file_path}"
        else:
            return f"저장 실패: {self.error_message}"


class StorageStrategy(ABC):
    """저장 전략 추상 클래스"""
    
    @abstractmethod
    def save_image(self, image: np.ndarray, file_path: str, 
                   metadata: Optional[Dict[str, Any]] = None) -> StorageResult:
        """
        이미지 저장
        Args:
            image: 저장할 이미지
            file_path: 저장 경로 (상대 경로)
            metadata: 추가 메타데이터
        Returns:
            StorageResult: 저장 결과
        """
        pass
    
    @abstractmethod
    def create_directory(self, dir_path: str) -> bool:
        """
        디렉토리 생성
        Args:
            dir_path: 생성할 디렉토리 경로
        Returns:
            bool: 생성 성공 여부
        """
        pass
    
    @abstractmethod
    def exists(self, file_path: str) -> bool:
        """
        파일/디렉토리 존재 여부 확인
        Args:
            file_path: 확인할 경로
        Returns:
            bool: 존재 여부
        """
        pass
    
    @abstractmethod
    def get_base_path(self) -> str:
        """
        기본 저장 경로 반환
        Returns:
            str: 기본 저장 경로
        """
        pass
    
    @abstractmethod
    def get_full_path(self, relative_path: str) -> str:
        """
        상대 경로를 절대 경로로 변환
        Args:
            relative_path: 상대 경로
        Returns:
            str: 절대 경로
        """
        pass


# strategies/base/filename_strategy.py
"""
파일명 전략 추상 클래스
파일명 생성 규칙의 인터페이스를 정의
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from datetime import datetime


class FilenameComponents:
    """파일명 구성 요소를 담는 데이터 클래스"""
    
    def __init__(self, prefix: str = "", date_str: str = "", user: str = "", 
                 content: str = "", extension: str = "jpg"):
        self.prefix = prefix
        self.date_str = date_str
        self.user = user
        self.content = content
        self.extension = extension
    
    def __str__(self):
        return f"Prefix: {self.prefix}, Date: {self.date_str}, User: {self.user}, Content: {self.content}"


class FilenameStrategy(ABC):
    """파일명 전략 추상 클래스"""
    
    @abstractmethod
    def generate_filename(self, user: str, ocr_content: str, 
                         timestamp: Optional[datetime] = None,
                         metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        파일명 생성
        Args:
            user: 사용자명
            ocr_content: OCR로 추출한 내용
            timestamp: 촬영 시각 (None이면 현재 시각 사용)
            metadata: 추가 메타데이터
        Returns:
            str: 생성된 파일명
        """
        pass
    
    @abstractmethod
    def generate_folder_name(self, timestamp: Optional[datetime] = None) -> str:
        """
        폴더명 생성 (날짜 기반)
        Args:
            timestamp: 기준 시각 (None이면 현재 시각 사용)
        Returns:
            str: 생성된 폴더명 (예: "24년 12월")
        """
        pass
    
    @abstractmethod
    def sanitize_text(self, text: str) -> str:
        """
        파일명에 사용할 수 없는 문자 제거/변환
        Args:
            text: 원본 텍스트
        Returns:
            str: 정제된 텍스트
        """
        pass
    
    @abstractmethod
    def validate_filename(self, filename: str) -> bool:
        """
        파일명 유효성 검사
        Args:
            filename: 검사할 파일명
        Returns:
            bool: 유효성 여부
        """
        pass
    
    @abstractmethod
    def parse_filename(self, filename: str) -> Optional[FilenameComponents]:
        """
        파일명에서 구성 요소 추출
        Args:
            filename: 파싱할 파일명
        Returns:
            Optional[FilenameComponents]: 파싱된 구성 요소 (실패시 None)
        """
        pass
