# config/settings.py
"""
애플리케이션 설정 파일
"""
import os
from pathlib import Path


class AppSettings:
    """애플리케이션 설정 클래스"""
    
    # 애플리케이션 정보
    APP_NAME = "사진 촬영 및 OCR 애플리케이션"
    APP_VERSION = "1.0.0"
    
    # 파일 및 폴더 설정
    DEFAULT_IMAGE_FORMAT = "jpg"
    FILENAME_PREFIX = "03.물품사진"
    MAX_FILENAME_LENGTH = 255
    MAX_OCR_CONTENT_LENGTH = 50
    
    # 카메라 설정
    DEFAULT_CAMERA_INDEX = 0
    CAMERA_WIDTH = 640
    CAMERA_HEIGHT = 480
    CAMERA_FPS = 30
    
    # OCR 설정
    DEFAULT_OCR_LANGUAGE = "kor+eng"
    MIN_OCR_CONFIDENCE = 30.0
    OCR_PREPROCESSING = True
    
    # UI 설정
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800
    CAMERA_UPDATE_INTERVAL = 30  # milliseconds
    
    # 경로 설정
    @staticmethod
    def get_user_list_path():
        """사용자 목록 파일 경로"""
        return os.path.join("config", "user_list.txt")
    
    @staticmethod
    def get_dropbox_paths():
        """가능한 Dropbox 경로들"""
        home = Path.home()
        return [
            home / "Dropbox",
            home / "Dropbox (Personal)",
            home / "Dropbox (Business)",
            home / "OneDrive",  # 대안으로 OneDrive도 포함
            home / "PhotoCapture"  # 최종 대안
        ]
    
    # Tesseract 경로 설정
    @staticmethod
    def get_tesseract_paths():
        """가능한 Tesseract 실행 파일 경로들"""
        return [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            "/usr/bin/tesseract",
            "/opt/homebrew/bin/tesseract",
            "tesseract"  # PATH에 있는 경우
        ]


# config/user_list.txt (예시 내용)
"""
# 사용자 목록 파일
# 한 줄에 한 사용자씩 작성하세요
# '#'으로 시작하는 줄은 주석입니다

김철수
이영희
박민수
최은정
관리자
"""


# config/__init__.py
"""
설정 패키지 초기화
"""
from .settings import AppSettings

__all__ = ['AppSettings']
