# controllers/ui_controller.py
"""
UI 컨트롤러 - UI와 비즈니스 로직을 연결
"""
from typing import List, Optional
from datetime import datetime
import numpy as np

from strategies.base.camera_strategy import CameraStrategy
from strategies.base.ocr_strategy import OCRStrategy, OCRResult
from strategies.base.storage_strategy import StorageStrategy
from strategies.base.filename_strategy import FilenameStrategy


class UIController:
    """UI와 전략들을 연결하는 컨트롤러"""
    
    def __init__(self, camera_strategy: CameraStrategy, ocr_strategy: OCRStrategy,
                 storage_strategy: StorageStrategy, filename_strategy: FilenameStrategy):
        self.camera_strategy = camera_strategy
        self.ocr_strategy = ocr_strategy
        self.storage_strategy = storage_strategy
        self.filename_strategy = filename_strategy
        
        self.current_image: Optional[np.ndarray] = None
        self.ocr_results: List[OCRResult] = []
        self.users: List[str] = []
        
        # 카메라 초기화
        self.initialize_camera()
        
        # 사용자 목록 로드
        self.load_users()
    
    def initialize_camera(self) -> bool:
        """카메라 초기화"""
        return self.camera_strategy.initialize()
    
    def get_camera_frame(self) -> Optional[np.ndarray]:
        """현재 카메라 프레임 가져오기"""
        return self.camera_strategy.get_frame()
    
    def capture_photo(self) -> bool:
        """사진 촬영"""
        image = self.camera_strategy.capture_photo()
        if image is not None:
            self.current_image = image
            return True
        return False
    
    def analyze_image_ocr(self) -> List[OCRResult]:
        """현재 이미지에 대해 OCR 수행"""
        if self.current_image is None:
            return []
        
        self.ocr_results = self.ocr_strategy.extract_text(self.current_image)
        return self.ocr_results
    
    def save_photo(self, user: str, ocr_content: str) -> bool:
        """사진 저장"""
        if self.current_image is None:
            return False
        
        try:
            # 파일명 생성
            timestamp = datetime.now()
            filename = self.filename_strategy.generate_filename(user, ocr_content, timestamp)
            
            # 폴더명 생성
            folder_name = self.filename_strategy.generate_folder_name(timestamp)
            
            # 전체 경로 생성
            file_path = f"{folder_name}/{filename}"
            
            # 저장
            result = self.storage_strategy.save_image(self.current_image, file_path)
            
            return result.success
            
        except Exception as e:
            print(f"사진 저장 중 오류: {e}")
            return False
    
    def load_users(self) -> List[str]:
        """사용자 목록 로드"""
        try:
            from utils.file_utils import FileUtils
            self.users = FileUtils.load_user_list()
            return self.users
        except Exception as e:
            print(f"사용자 목록 로드 실패: {e}")
            self.users = ["기본사용자"]
