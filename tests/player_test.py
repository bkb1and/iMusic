import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, 
                           QVBoxLayout, QHBoxLayout, QFileDialog, 
                           QWidget, QLabel, QSlider)
from PyQt5.QtCore import Qt
import pygame
import os

class MusicPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("音乐播放测试")
        self.setGeometry(100, 100, 400, 200)
        
        pygame.mixer.init()
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        layout = QVBoxLayout()
        
        self.current_file_label = QLabel("未选择文件")
        layout.addWidget(self.current_file_label)
        
        button_layout = QHBoxLayout()
        
        self.select_button = QPushButton("选择文件")
        self.play_button = QPushButton("播放")
        self.pause_button = QPushButton("暂停")
        
        button_layout.addWidget(self.select_button)
        button_layout.addWidget(self.play_button)
        button_layout.addWidget(self.pause_button)
        
        layout.addLayout(button_layout)
        
        volume_layout = QHBoxLayout()
        volume_label = QLabel("音量:")
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(50)
        volume_layout.addWidget(volume_label)
        volume_layout.addWidget(self.volume_slider)
        
        layout.addLayout(volume_layout)
        
        self.central_widget.setLayout(layout)
        
        self.select_button.clicked.connect(self.select_file)
        self.play_button.clicked.connect(self.play_music)
        self.pause_button.clicked.connect(self.pause_music)
        self.volume_slider.valueChanged.connect(self.change_volume)
        
        self.current_file = None
        self.is_paused = False
        
    def select_file(self):
        """选择音乐文件"""
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "选择音乐文件",
            "",
            "音频文件 (*.mp3 *.wav *.ogg)"
        )
        if file_name:
            self.current_file = file_name
            self.current_file_label.setText(os.path.basename(file_name))
            
    def play_music(self):
        """播放音乐"""
        if self.current_file:
            if self.is_paused:
                pygame.mixer.music.unpause()
                self.is_paused = False
            else:
                pygame.mixer.music.load(self.current_file)
                pygame.mixer.music.play()
                
    def pause_music(self):
        """暂停音乐"""
        if pygame.mixer.music.get_busy() and not self.is_paused:
            pygame.mixer.music.pause()
            self.is_paused = True
        
    def change_volume(self, value):
        """改变音量"""
        volume = value / 100
        pygame.mixer.music.set_volume(volume)
        
    def closeEvent(self, event):
        """关闭窗口时清理pygame"""
        pygame.mixer.quit()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = MusicPlayer()
    player.show()
    sys.exit(app.exec_())