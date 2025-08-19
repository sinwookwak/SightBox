# main.py
"""
사진 촬영 및 OCR 애플리케이션 - 메인 진입점
전략 패턴을 사용하여 각 기능을 모듈화하고 확장 가능하도록 구현
"""
import sys
import os
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 전략 구현체들 import
from strategies.camera.opencv_camera import OpenCVCamera
from strategies.ocr.tesseract_ocr import TesseractOCR
from strategies.storage.dropbox_local import DropboxLocal
from strategies.filename.standard_naming import StandardNaming

# 컨트롤러와 UI import
from controllers.ui_controller import UIController
from ui.main_window import MainWindow

# 유틸리티 import
from utils.file_utils import FileUtils


class PhotoCaptureApp:
    """사진 촬영 애플리케이션 메인 클래스"""
    
    def __init__(self):
        self.app = None
        self.main_window = None
        self.controller = None
    
    def initialize_strategies(self):
        """전략 객체들 초기화"""
        try:
            # 카메라 전략 (OpenCV 기반)
            camera_strategy = OpenCVCamera(camera_index=0)
            
            # OCR 전략 (Tesseract 기반)
            ocr_strategy = TesseractOCR(language='kor+eng')
            
            # 저장 전략 (Dropbox 로컬 폴더)
            storage_strategy = DropboxLocal()
            
            # 파일명 전략 (표준 명명 규칙)
            filename_strategy = StandardNaming()
            
            return camera_strategy, ocr_strategy, storage_strategy, filename_strategy
            
        except Exception as e:
            print(f"전략 초기화 중 오류: {e}")
            return None, None, None, None
    
    def check_dependencies(self):
        """필수 의존성 검사"""
        missing_deps = []
        
        # OpenCV 검사
        try:
            import cv2
        except ImportError:
            missing_deps.append("opencv-python")
        
        # Tesseract 검사
        try:
            import pytesseract
            # Tesseract 실행 파일 검사
            if not pytesseract.pytesseract.tesseract_cmd or not os.path.exists(pytesseract.pytesseract.tesseract_cmd):
                # Windows에서 기본 경로 시도
                possible_paths = [
                    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                    "tesseract"  # PATH에 있는 경우
                ]
                
                tesseract_found = False
                for path in possible_paths:
                    try:
                        pytesseract.pytesseract.tesseract_cmd = path
                        pytesseract.image_to_string("test")
                        tesseract_found = True
                        break
                    except:
                        continue
                
                if not tesseract_found:
                    missing_deps.append("tesseract-ocr (실행 파일)")
        except ImportError:
            missing_deps.append("pytesseract")
        
        # PyQt5 검사
        try:
            from PyQt5.QtWidgets import QApplication
        except ImportError:
            missing_deps.append("PyQt5")
        
        return missing_deps
    
    def setup_directories(self):
        """필요한 디렉토리 설정"""
        try:
            # config 디렉토리 생성
            FileUtils.ensure_directory_exists("config")
            
            # 기본 사용자 목록 파일 생성
            if not os.path.exists("config/user_list.txt"):
                default_users = ["김철수", "이영희", "박민수", "최은정", "관리자"]
                FileUtils.save_user_list(default_users)
            
            return True
            
        except Exception as e:
            print(f"디렉토리 설정 중 오류: {e}")
            return False
    
    def run(self):
        """애플리케이션 실행"""
        # 의존성 검사
        missing_deps = self.check_dependencies()
        if missing_deps:
            print("다음 의존성이 누락되었습니다:")
            for dep in missing_deps:
                print(f"  - {dep}")
            print("\n필요한 패키지를 설치해주세요:")
            print("pip install -r requirements.txt")
            if "tesseract-ocr (실행 파일)" in missing_deps:
                print("\nTesseract OCR 설치가 필요합니다:")
                print("Windows: https://github.com/UB-Mannheim/tesseract/wiki")
                print("Ubuntu: sudo apt install tesseract-ocr tesseract-ocr-kor")
                print("macOS: brew install tesseract tesseract-lang")
            return 1
        
        # PyQt5 애플리케이션 생성
        self.app = QApplication(sys.argv)
        self.app.setAttribute(Qt.AA_EnableHighDpiScaling)
        
        # 디렉토리 설정
        if not self.setup_directories():
            QMessageBox.critical(None, "오류", "디렉토리 설정에 실패했습니다.")
            return 1
        
        # 전략 객체들 초기화
        camera_strategy, ocr_strategy, storage_strategy, filename_strategy = self.initialize_strategies()
        
        if not all([camera_strategy, ocr_strategy, storage_strategy, filename_strategy]):
            QMessageBox.critical(None, "오류", "전략 객체 초기화에 실패했습니다.")
            return 1
        
        # UI 컨트롤러 생성 (의존성 주입)
        self.controller = UIController(
            camera_strategy=camera_strategy,
            ocr_strategy=ocr_strategy,
            storage_strategy=storage_strategy,
            filename_strategy=filename_strategy
        )
        
        # 카메라 연결 확인
        if not self.controller.is_camera_connected():
            reply = QMessageBox.question(
                None, "카메라 오류", 
                "카메라에 연결할 수 없습니다. 계속 진행하시겠습니까?\n"
                "(카메라 없이도 UI 테스트는 가능합니다)",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return 1
        
        # 메인 윈도우 생성 및 표시
        self.main_window = MainWindow(self.controller)
        self.main_window.show()
        
        # 애플리케이션 실행
        return self.app.exec_()


def main():
    """메인 함수"""
    app = PhotoCaptureApp()
    return app.run()


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n애플리케이션이 사용자에 의해 중단되었습니다.")
        sys.exit(0)
    except Exception as e:
        print(f"예상치 못한 오류가 발생했습니다: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
