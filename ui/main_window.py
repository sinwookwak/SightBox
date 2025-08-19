# ui/main_window.py
"""
PyQt5 기반 메인 윈도우 UI
"""
import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QComboBox, QTextEdit, QGroupBox,
                            QGridLayout, QMessageBox, QListWidget, QSplitter,
                            QFrame, QApplication)
from PyQt5.QtCore import QTimer, Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage, QFont
import cv2
import numpy as np
from typing import List, Optional

from controllers.ui_controller import UIController
from strategies.base.ocr_strategy import OCRResult


class CameraWidget(QLabel):
    """카메라 뷰를 표시하는 위젯"""
    
    def __init__(self):
        super().__init__()
        self.setMinimumSize(640, 480)
        self.setStyleSheet("border: 2px solid gray; background-color: black;")
        self.setAlignment(Qt.AlignCenter)
        self.setText("카메라 연결 중...")
        self.setScaledContents(True)
    
    def update_frame(self, frame: np.ndarray):
        """카메라 프레임 업데이트"""
        if frame is not None:
            # BGR to RGB 변환
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            
            # QImage 생성
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            
            # QPixmap으로 변환하여 표시
            pixmap = QPixmap.fromImage(qt_image)
            self.setPixmap(pixmap)
    
    def show_captured_image(self, image: np.ndarray):
        """촬영된 이미지 표시"""
        self.update_frame(image)


class OCRResultWidget(QWidget):
    """OCR 결과를 표시하는 위젯"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # OCR 결과 목록
        self.result_list = QListWidget()
        self.result_list.setMaximumHeight(150)
        
        # 선택된 텍스트 편집
        self.text_edit = QTextEdit()
        self.text_edit.setMaximumHeight(100)
        self.text_edit.setPlaceholderText("OCR 결과를 선택하거나 직접 입력하세요...")
        
        layout.addWidget(QLabel("OCR 결과 후보:"))
        layout.addWidget(self.result_list)
        layout.addWidget(QLabel("선택된 텍스트:"))
        layout.addWidget(self.text_edit)
        
        self.setLayout(layout)
        
        # 이벤트 연결
        self.result_list.itemClicked.connect(self.on_result_selected)
    
    def update_results(self, results: List[OCRResult]):
        """OCR 결과 업데이트"""
        self.result_list.clear()
        
        for i, result in enumerate(results):
            display_text = f"[{result.confidence:.1f}%] {result.text}"
            self.result_list.addItem(display_text)
            
            # 첫 번째 결과를 자동 선택
            if i == 0:
                self.text_edit.setText(result.text)
    
    def on_result_selected(self, item):
        """OCR 결과 선택 시"""
        text = item.text()
        # 신뢰도 부분 제거하고 실제 텍스트만 추출
        if "] " in text:
            actual_text = text.split("] ", 1)[1]
            self.text_edit.setText(actual_text)
    
    def get_selected_text(self) -> str:
        """선택된 텍스트 반환"""
        return self.text_edit.toPlainText().strip()


class MainWindow(QMainWindow):
    """메인 윈도우"""
    
    def __init__(self, controller: UIController):
        super().__init__()
        self.controller = controller
        self.timer = QTimer()
        self.init_ui()
        self.setup_timer()
    
    def init_ui(self):
        """UI 초기화"""
        self.setWindowTitle("사진 촬영 및 OCR 애플리케이션")
        self.setGeometry(100, 100, 1200, 800)
        
        # 중앙 위젯
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 메인 레이아웃
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        # 스플리터로 좌우 분할
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # 좌측 패널 (카메라)
        left_panel = self.create_camera_panel()
        splitter.addWidget(left_panel)
        
        # 우측 패널 (컨트롤)
        right_panel = self.create_control_panel()
        splitter.addWidget(right_panel)
        
        # 스플리터 비율 설정
        splitter.setSizes([700, 500])
    
    def create_camera_panel(self) -> QWidget:
        """카메라 패널 생성"""
        panel = QWidget()
        layout = QVBoxLayout()
        
        # 카메라 그룹
        camera_group = QGroupBox("카메라 뷰")
        camera_layout = QVBoxLayout()
        
        self.camera_widget = CameraWidget()
        camera_layout.addWidget(self.camera_widget)
        
        camera_group.setLayout(camera_layout)
        layout.addWidget(camera_group)
        
        panel.setLayout(layout)
        return panel
    
    def create_control_panel(self) -> QWidget:
        """컨트롤 패널 생성"""
        panel = QWidget()
        layout = QVBoxLayout()
        
        # 사용자 선택 그룹
        user_group = QGroupBox("사용자 선택")
        user_layout = QHBoxLayout()
        
        user_layout.addWidget(QLabel("사용자:"))
        self.user_combo = QComboBox()
        self.user_combo.addItems(self.controller.get_users())
        user_layout.addWidget(self.user_combo)
        
        user_group.setLayout(user_layout)
        layout.addWidget(user_group)
        
        # 촬영 버튼
        self.capture_button = QPushButton("사진 촬영")
        self.capture_button.setMinimumHeight(50)
        self.capture_button.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.capture_button.clicked.connect(self.capture_photo)
        layout.addWidget(self.capture_button)
        
        # OCR 결과 그룹
        ocr_group = QGroupBox("OCR 결과")
        ocr_layout = QVBoxLayout()
        
        self.ocr_widget = OCRResultWidget()
        ocr_layout.addWidget(self.ocr_widget)
        
        ocr_group.setLayout(ocr_layout)
        layout.addWidget(ocr_group)
        
        # 저장 버튼
        self.save_button = QPushButton("사진 저장")
        self.save_button.setMinimumHeight(40)
        self.save_button.setStyleSheet("font-size: 14px; background-color: #4CAF50; color: white;")
        self.save_button.setEnabled(False)
        self.save_button.clicked.connect(self.save_photo)
        layout.addWidget(self.save_button)
        
        # 상태 표시
        self.status_label = QLabel("카메라 준비 중...")
        self.status_label.setStyleSheet("color: blue; font-weight: bold;")
        layout.addWidget(self.status_label)
        
        panel.setLayout(layout)
        return panel
    
    def setup_timer(self):
        """타이머 설정"""
        self.timer.timeout.connect(self.update_camera)
        self.timer.start(30)  # 30ms마다 업데이트 (약 33 FPS)
    
    def update_camera(self):
        """카메라 화면 업데이트"""
        frame = self.controller.get_camera_frame()
        if frame is not None:
            self.camera_widget.update_frame(frame)
            if self.status_label.text() == "카메라 준비 중...":
                self.status_label.setText("카메라 연결됨")
                self.status_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            if self.controller.is_camera_connected():
                self.status_label.setText("카메라 오류")
                self.status_label.setStyleSheet("color: red; font-weight: bold;")
    
    def capture_photo(self):
        """사진 촬영"""
        if self.controller.capture_photo():
            # 촬영된 이미지 표시
            captured_image = self.controller.get_current_image()
            if captured_image is not None:
                self.camera_widget.show_captured_image(captured_image)
                
                # OCR 수행
                self.status_label.setText("OCR 분석 중...")
                self.status_label.setStyleSheet("color: orange; font-weight: bold;")
                
                # UI 업데이트를 위해 잠시 대기
                QApplication.processEvents()
                
                ocr_results = self.controller.analyze_image_ocr()
                self.ocr_widget.update_results(ocr_results)
                
                self.save_button.setEnabled(True)
                self.status_label.setText("촬영 완료 - 저장 가능")
                self.status_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            QMessageBox.warning(self, "오류", "사진 촬영에 실패했습니다.")
    
    def save_photo(self):
        """사진 저장"""
        user = self.user_combo.currentText()
        ocr_content = self.ocr_widget.get_selected_text()
        
        if not user:
            QMessageBox.warning(self, "오류", "사용자를 선택해주세요.")
            return
        
        if not ocr_content:
            reply = QMessageBox.question(self, "확인", 
                                       "OCR 내용이 비어있습니다. 계속 저장하시겠습니까?",
                                       QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.No:
                return
            ocr_content = "NoText"
        
        self.status_label.setText("저장 중...")
        self.status_label.setStyleSheet("color: orange; font-weight: bold;")
        
        if self.controller.save_photo(user, ocr_content):
            QMessageBox.information(self, "성공", "사진이 성공적으로 저장되었습니다.")
            self.status_label.setText("저장 완료")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            
            # 저장 후 초기화
            self.save_button.setEnabled(False)
            self.ocr_widget.result_list.clear()
            self.ocr_widget.text_edit.clear()
        else:
            QMessageBox.critical(self, "오류", "사진 저장에 실패했습니다.")
            self.status_label.setText("저장 실패")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
    
    def closeEvent(self, event):
        """윈도우 종료 시"""
        self.timer.stop()
        self.controller.release_resources()
        event.accept()
