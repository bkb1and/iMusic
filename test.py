import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QListWidget, 
                             QLineEdit, QScrollArea, QFrame, QGridLayout,
                             QProgressBar, QSlider)
from PyQt5.QtCore import Qt, QSize, QPoint
from PyQt5.QtGui import QIcon, QPixmap, QColor, QPalette

class CustomProgressBar(QProgressBar):
    def __init__(self):
        super().__init__()
        self.setTextVisible(False)
        self.setStyleSheet("""
            QProgressBar {
                border: none;
                background-color: #e1e1e1;
                height: 2px;
            }
            QProgressBar::chunk {
                background-color: #c62f2f;
            }
        """)

class TitleBar(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        
        # 标题
        self.title = QLabel("网易云音乐")
        self.title.setStyleSheet("""
            color: #333333;
            font-size: 14px;
            font-weight: bold;
            padding-left: 10px;
        """)
        
        # 窗口控制按钮
        self.minimize_button = QPushButton("—")
        self.maximize_button = QPushButton("□")
        self.close_button = QPushButton("×")
        
        # 设置按钮样式
        button_style = """
            QPushButton {
                background-color: transparent;
                border: none;
                font-family: Arial;
                font-size: 16px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: %s;
                color: white;
            }
        """
        self.minimize_button.setStyleSheet(button_style % "#505050")
        self.maximize_button.setStyleSheet(button_style % "#505050")
        self.close_button.setStyleSheet(button_style % "#c62f2f")
        
        # 连接按钮信号
        self.minimize_button.clicked.connect(self.parent.showMinimized)
        self.maximize_button.clicked.connect(self.maximize_restore)
        self.close_button.clicked.connect(self.parent.close)
        
        # 布局
        self.layout.addWidget(self.title)
        self.layout.addStretch()
        self.layout.addWidget(self.minimize_button)
        self.layout.addWidget(self.maximize_button)
        self.layout.addWidget(self.close_button)
        
        self.start = QPoint(0, 0)
        self.pressing = False
    
    def maximize_restore(self):
        if self.parent.isMaximized():
            self.parent.showNormal()
            self.maximize_button.setText("□")
        else:
            self.parent.showMaximized()
            self.maximize_button.setText("❐")
    
    # 实现窗口拖动
    def mousePressEvent(self, event):
        self.start = self.mapToGlobal(event.pos())
        self.pressing = True

    def mouseMoveEvent(self, event):
        if self.pressing and not self.parent.isMaximized():
            end = self.mapToGlobal(event.pos())
            movement = end - self.start
            self.parent.move(self.parent.pos() + movement)
            self.start = end

    def mouseReleaseEvent(self, event):
        self.pressing = False

    def mouseDoubleClickEvent(self, event):
        self.maximize_restore()

class NeteaseMusicClone(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMinimumSize(1200, 800)
        
        # 创建主窗口部件
        self.main_widget = QWidget()
        self.main_widget.setObjectName("mainWidget")
        self.main_widget.setStyleSheet("""
            QWidget#mainWidget {
                background-color: white;
                border-radius: 5px;
                border: 1px solid #cccccc;
            }
        """)
        
        # 主布局
        self.main_layout = QVBoxLayout(self.main_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # 添加自定义标题栏
        self.title_bar = TitleBar(self)
        self.main_layout.addWidget(self.title_bar)
        
        # 内容布局
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # 左侧边栏
        left_sidebar = QFrame()
        left_sidebar.setObjectName("leftSidebar")
        left_sidebar.setStyleSheet("""
            #leftSidebar {
                background-color: #f5f5f5;
                min-width: 200px;
                max-width: 200px;
                padding: 10px 0;
            }
        """)
        left_layout = QVBoxLayout(left_sidebar)
        left_layout.setContentsMargins(10, 0, 10, 0)
        left_layout.setSpacing(0)
        
        # 导航按钮
        nav_buttons = [
            ("发现音乐", "🎵"), ("播客", "🎙️"), ("视频", "🎬"), 
            ("关注", "👥"), ("直播", "📺"), ("私人FM", "📻")
        ]
        for button_text, icon in nav_buttons:
            button = QPushButton(f"{icon} {button_text}")
            button.setStyleSheet("""
                QPushButton {
                    font-size: 14px;
                    padding: 10px 5px;
                    margin: 2px 0;
                }
                QPushButton:hover {
                    background-color: #e6e6e6;
                    color: #c62f2f;
                }
            """)
            left_layout.addWidget(button)
        
        # 我的音乐
        my_music_label = QLabel("我的音乐")
        my_music_label.setStyleSheet("font-weight: bold; margin-top: 15px; color: #666666; padding: 10px 5px;")
        left_layout.addWidget(my_music_label)
        
        my_music_buttons = [
            ("我喜欢的音乐", "❤️"), ("我的收藏", "⭐"), ("本地与下载", "💾")
        ]
        for button_text, icon in my_music_buttons:
            button = QPushButton(f"{icon} {button_text}")
            button.setStyleSheet("""
                QPushButton {
                    font-size: 14px;
                    padding: 10px 5px;
                    margin: 2px 0;
                }
                QPushButton:hover {
                    background-color: #e6e6e6;
                    color: #c62f2f;
                }
            """)
            left_layout.addWidget(button)
        
        left_layout.addStretch()
        content_layout.addWidget(left_sidebar)
        
        # 中间内容区域
        center_area = QFrame()
        center_layout = QVBoxLayout(center_area)
        center_layout.setContentsMargins(20, 10, 20, 10)
        
        # 顶部操作栏
        top_bar = QHBoxLayout()
        
        # 后退前进按钮
        nav_buttons_layout = QHBoxLayout()
        for arrow in ["←", "→"]:
            nav_button = QPushButton(arrow)
            nav_button.setFixedSize(24, 24)
            nav_button.setStyleSheet("""
                QPushButton {
                    background-color: #e1e1e1;
                    border-radius: 12px;
                    font-size: 16px;
                    padding: 0;
                    text-align: center;
                }
                QPushButton:hover {
                    background-color: #d1d1d1;
                }
            """)
            nav_buttons_layout.addWidget(nav_button)
        
        top_bar.addLayout(nav_buttons_layout)
        
        # 搜索栏
        search_box = QLineEdit()
        search_box.setPlaceholderText("🔍 搜索音乐，歌手，歌词，用户")
        search_box.setFixedWidth(250)
        top_bar.addWidget(search_box)
        
        top_bar.addStretch()
        
        # 用户信息
        user_info = QPushButton("👤 用户名")
        user_info.setStyleSheet("""
            QPushButton {
                color: #333333;
                font-size: 14px;
            }
        """)
        top_bar.addWidget(user_info)
        
        center_layout.addLayout(top_bar)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # 轮播图
        banner = QLabel("热门推荐")
        banner.setStyleSheet("""
            background-color: #f5f5f5;
            min-height: 200px;
            border-radius: 10px;
            font-size: 24px;
            font-weight: bold;
            color: #c62f2f;
        """)
        banner.setAlignment(Qt.AlignCenter)
        scroll_layout.addWidget(banner)
        
        # 推荐歌单
        recommend_label = QLabel("热门推荐")
        recommend_label.setStyleSheet("font-size: 20px; font-weight: bold; margin: 20px 0 10px 0;")
        scroll_layout.addWidget(recommend_label)
        
        # 推荐歌单网格
        playlist_grid = QGridLayout()
        playlist_grid.setSpacing(20)
        
        for i in range(5):
            playlist_frame = QFrame()
            playlist_frame.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border-radius: 5px;
                }
                QFrame:hover {
                    background-color: #f5f5f5;
                }
            """)
            playlist_layout = QVBoxLayout(playlist_frame)
            
            cover = QLabel("封面")
            cover.setAlignment(Qt.AlignCenter)
            cover.setStyleSheet("""
                background-color: #e1e1e1;
                border-radius: 5px;
                color: white;
                font-size: 18px;
            """)
            cover.setFixedHeight(150)
            
            title = QLabel(f"推荐歌单 {i+1}")
            title.setStyleSheet("""
                font-size: 14px;
                color: #333333;
                margin-top: 5px;
            """)
            title.setWordWrap(True)
            
            playlist_layout.addWidget(cover)
            playlist_layout.addWidget(title)
            
            playlist_grid.addWidget(playlist_frame, i // 5, i % 5)
        
        scroll_layout.addLayout(playlist_grid)
        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_content)
        center_layout.addWidget(scroll_area)
        
        content_layout.addWidget(center_area)
        self.main_layout.addWidget(content_widget)
        
        # 底部播放控制栏
        player_control = QFrame()
        player_control.setStyleSheet("""
            QFrame {
                background-color: #f5f5f5;
                border-top: 1px solid #e1e1e1;
            }
        """)
        player_layout = QVBoxLayout(player_control)
        player_layout.setContentsMargins(10, 5, 10, 5)
        
        # 进度条
        progress_bar = CustomProgressBar()
        progress_bar.setValue(30)
        player_layout.addWidget(progress_bar)
        
        # 控制按钮和信息布局
        controls_layout = QHBoxLayout()
        
        # 播放控制按钮
        control_buttons = ["⏮️", "⏯️", "⏭️"]
        for button_text in control_buttons:
            button = QPushButton(button_text)
            button.setFixedSize(32, 32)
            button.setStyleSheet("""
                QPushButton {
                    font-size: 16px;
                    background-color: transparent;
                    border-radius: 16px;
                    padding: 0;
                    text-align: center;
                }
                QPushButton:hover {
                    background-color: #e1e1e1;
                }
            """)
            controls_layout.addWidget(button)
        
        # 当前播放信息
        song_info_layout = QVBoxLayout()
        song_title = QLabel("当前播放的歌曲")
        song_title.setStyleSheet("font-size: 14px; font-weight: bold;")
        artist_name = QLabel("歌手名称")
        artist_name.setStyleSheet("font-size: 12px; color: #666666;")
        song_info_layout.addWidget(song_title)
        song_info_layout.addWidget(artist_name)
        controls_layout.addLayout(song_info_layout)
        
        controls_layout.addStretch()
        
        # 音量控制
        volume_slider = QSlider(Qt.Horizontal)
        volume_slider.setFixedWidth(100)
        volume_slider.setValue(50)
        controls_layout.addWidget(QLabel("🔊"))
        controls_layout.addWidget(volume_slider)
        
        player_layout.addLayout(controls_layout)
        
        self.main_layout.addWidget(player_control)
        
        self.setCentralWidget(self.main_widget)

def main():
    app = QApplication(sys.argv)
    player = NeteaseMusicClone()
    player.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()