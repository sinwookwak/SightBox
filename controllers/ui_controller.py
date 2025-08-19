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
            return self.users
    
    def get_users(self) -> List[str]:
        """사용자 목록 반환"""
        return self.users
    
    def get_current_image(self) -> Optional[np.ndarray]:
        """현재 촬영된 이미지 반환"""
        return self.current_image
    
    def get_ocr_results(self) -> List[OCRResult]:
        """OCR 결과 반환"""
        return self.ocr_results
    
    def is_camera_connected(self) -> bool:
        """카메라 연결 상태 확인"""
        return self.camera_strategy.is_connected()
    
    def release_resources(self) -> None:
        """리소스 해제"""
        self.camera_strategy.release()


# utils/file_utils.py
"""
파일 관련 유틸리티 함수들
"""
import os
from pathlib import Path
from typing import List


class FileUtils:
    """파일 관련 유틸리티 클래스"""
    
    @staticmethod
    def load_user_list(file_path: str = "config/user_list.txt") -> List[str]:
        """
        사용자 목록 파일에서 사용자 목록 로드
        Args:
            file_path: 사용자 목록 파일 경로
        Returns:
            List[str]: 사용자 목록
        """
        users = []
        
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        user = line.strip()
                        if user and not user.startswith('#'):  # 주석 제외
                            users.append(user)
            else:
                # 파일이 없으면 기본 사용자 목록 생성
                default_users = ["김철수", "이영희", "박민수", "최은정"]
                FileUtils.save_user_list(default_users, file_path)
                users = default_users
                
        except Exception as e:
            print(f"사용자 목록 로드 실패: {e}")
            users = ["기본사용자"]
        
        return users if users else ["기본사용자"]
    
    @staticmethod
    def save_user_list(users: List[str], file_path: str = "config/user_list.txt") -> bool:
        """
        사용자 목록을 파일에 저장
        Args:
            users: 사용자 목록
            file_path: 저장할 파일 경로
        Returns:
            bool: 저장 성공 여부
        """
        try:
            # 디렉토리 생성
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("# 사용자 목록 파일\n")
                f.write("# 한 줄에 한 사용자씩 작성하세요\n\n")
                for user in users:
                    f.write(f"{user}\n")
            
            return True
            
        except Exception as e:
            print(f"사용자 목록 저장 실패: {e}")
            return False
    
    @staticmethod
    def ensure_directory_exists(directory_path: str) -> bool:
        """
        디렉토리가 존재하지 않으면 생성
        Args:
            directory_path: 디렉토리 경로
        Returns:
            bool: 성공 여부
        """
        try:
            Path(directory_path).mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            print(f"디렉토리 생성 실패: {e}")
            return False
    
    @staticmethod
    def get_safe_filename(filename: str) -> str:
        """
        안전한 파일명으로 변환
        Args:
            filename: 원본 파일명
        Returns:
            str: 안전한 파일명
        """
        import re
        # 파일명에 사용할 수 없는 문자들 제거
        safe_filename = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', filename)
        safe_filename = re.sub(r'\s+', ' ', safe_filename).strip()
        
        # 길이 제한
        if len(safe_filename) > 200:
            name, ext = os.path.splitext(safe_filename)
            safe_filename = name[:200-len(ext)] + ext
        
        return safe_filename if safe_filename else "unknown"


# utils/date_utils.py
"""
날짜 관련 유틸리티 함수들
"""
from datetime import datetime
from typing import Tuple


class DateUtils:
    """날짜 관련 유틸리티 클래스"""
    
    @staticmethod
    def get_folder_name(timestamp: datetime = None) -> str:
        """
        날짜 기반 폴더명 생성 (YY년 MM월)
        Args:
            timestamp: 기준 시각 (None이면 현재 시각)
        Returns:
            str: 폴더명
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        return timestamp.strftime("%y년 %m월")
    
    @staticmethod
    def get_date_string(timestamp: datetime = None, format_type: str = "yymmdd") -> str:
        """
        날짜 문자열 생성
        Args:
            timestamp: 기준 시각 (None이면 현재 시각)
            format_type: 형식 ("yymmdd", "yyyy-mm-dd", "full" 등)
        Returns:
            str: 날짜 문자열
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        if format_type == "yymmdd":
            return timestamp.strftime("%y%m%d")
        elif format_type == "yyyy-mm-dd":
            return timestamp.strftime("%Y-%m-%d")
        elif format_type == "full":
            return timestamp.strftime("%Y년 %m월 %d일 %H시 %M분")
        else:
            return timestamp.strftime("%y%m%d")
    
    @staticmethod
    def parse_date_from_filename(filename: str) -> Tuple[bool, datetime]:
        """
        파일명에서 날짜 추출
        Args:
            filename: 파일명
        Returns:
            Tuple[bool, datetime]: (성공 여부, 추출된 날짜)
        """
        import re
        
        try:
            # yymmdd 형식 찾기
            pattern = r'(\d{6})'
            match = re.search(pattern, filename)
            
            if match:
                date_str = match.group(1)
                # 20XX년대로 가정
                year = 2000 + int(date_str[:2])
                month = int(date_str[2:4])
                day = int(date_str[4:6])
                
                parsed_date = datetime(year, month, day)
                return True, parsed_date
            
            return False, datetime.now()
            
        except Exception:
            return False, datetime.now()
    
    @staticmethod
    def get_time_string(timestamp: datetime = None) -> str:
        """
        시간 문자열 생성 (HH:MM:SS)
        Args:
            timestamp: 기준 시각 (None이면 현재 시각)
        Returns:
            str: 시간 문자열
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        return timestamp.strftime("%H:%M:%S")
