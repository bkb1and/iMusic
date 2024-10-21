import sys
import os
import pygame
import re
import requests
from musicapi import MusicApi_wyy
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QListWidget,
    QLineEdit,
    QFrame,
    QGridLayout,
    QSlider,
    QSizePolicy,
    QStackedWidget,
    QFileDialog,
    QMessageBox,
    QInputDialog,
    QSpacerItem
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtSql import QSqlDatabase, QSqlQuery
from PyQt5.QtGui import QPixmap

class ClickableLabel(QLabel):
    clicked = pyqtSignal()  # 自定义信号
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

class iMusic(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = None
        self.current_volumn = 50
        self.current_table_name = None
        self.current_filepath = None
        self.current_song_title = None
        self.current_song_artist = None
        self.current_song_album = None
        self.song_duration = 0
        self.current_time = 0
        self.current_pos = 0
        self.current_page = None
        self.previous_filepath = None
        self.next_filepath = None
        self.is_playing = False
        self.is_dragging = False
        self.is_connected = False
        self.play_lists = []
        self.recommends = ["An Evening With Silk Sonic", 
                           "Kind Of Blue", "La La Land", "梦想家", "APT"]

        self.save_dir = "music"
        self.MusicApi = None

        self.lyrics_dict = {}
        self.labels = []


        self.stack = QStackedWidget(self)
        self.banner_timer = QTimer(self)
        self.progress_timer = QTimer(self)
        self.progress_bar = QSlider(Qt.Horizontal)
        self.lyric_timer = QTimer(self)

        self.lyric_page = QWidget()
        self.lyricUI(self.lyric_page)
        self.lyric_page.setObjectName("lyric_page")
        self.stack.addWidget(self.lyric_page)

        pygame.mixer.init()

        self.create_db()
        self.init_ui()
        self.load_playlists_from_db()
        self.init_recommends_pages()
        self.load_lyrics_pages_from_db()
    
    """初始化ui"""
    def init_ui(self):
        """全局样式"""
        self.setWindowTitle("iMusic")
        self.setMinimumSize(1600, 900)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
                color: #333333;
            }
            QPushButton {
                border: none;
                padding: 8px 15px;
                color: #333333;
                text-align: left;
            }
            QPushButton:hover {
                color: #c62f2f;
            }
            QLineEdit {
                border: none;
                background-color: #f5f5f5;
                padding: 8px 15px 8px 35px;
                border-radius: 15px;
                font-size: 13px;
            }
            QLabel {
                color: #333333;
            }
            QListWidget {
                border: none;
                background-color: transparent;
            }
            QScrollArea {
                border: none;
            }
            QSlider::groove:horizontal {
                border: none;
                background: #e1e1e1;
                height: 4px;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #c62f2f;
                border: none;
                width: 12px;
                height: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }
            QSlider::sub-page:horizontal {
                background: #c62f2f;
            }
        """)
        
        """中心控件"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        master_master_layout = QVBoxLayout(central_widget)
        master_master_layout.setSpacing(0)
        master_master_layout.setContentsMargins(0, 0, 0, 0)


        master_layout = QHBoxLayout()
        master_layout.setSpacing(0)
        master_layout.setContentsMargins(0, 0, 0, 0)





        """左侧边栏"""
        left_sidebar = QFrame()
        left_sidebar.setObjectName("leftSidebar")
        left_sidebar.setStyleSheet("""
            #leftSidebar {
                background-color: #f5f5f5;
                padding: 10px 0;
            }
        """)
        left_layout = QVBoxLayout(left_sidebar)
        left_layout.setContentsMargins(10, 0, 10, 0)
        left_layout.setSpacing(0)

        """logo"""
        logo_label = QLabel("iMusic")
        logo_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #c62f2f;
            padding: 15px 0;
        """)
        logo_layout = QHBoxLayout()
        logo_layout.addWidget(logo_label)
        left_layout.addLayout(logo_layout)

        """导航按钮"""
        nav_buttons = [
            ("🎵", "推荐"),
            ("🎙️", "精选")
        ]
        nav_layout = QVBoxLayout()
        for icon, button_text in nav_buttons:
            button = QPushButton(f"{icon} {button_text}")
            button.setStyleSheet("""
                QPushButton {
                    font-size: 16px;
                    padding: 12px 5px;
                    margin: 2px 0;
                }
                QPushButton:hover {
                    background-color: #e6e6e6;
                }
            """)
            if button_text == "推荐":
                button.clicked.connect(lambda: self.display(self.stack.indexOf(self.homepage)))
            elif button_text == "精选":
                button.clicked.connect(lambda: self.display(self.stack.indexOf(self.selected)))
            nav_layout.addWidget(button)
        left_layout.addLayout(nav_layout)

        """我的"""
        my_music_label = QLabel("我的")
        my_music_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            margin-top: 20px;
            color: #666666;
            padding: 12px 5px;
        """)
        my_music_layout = QVBoxLayout()
        my_music_layout.addWidget(my_music_label)
        my_music_buttons = [
            ("🎵", "我的收藏"),
            ("🎵", "最近播放")
        ]
        for icon, button_text in my_music_buttons:
            button = QPushButton(f"{icon} {button_text}")
            button.setStyleSheet("""
                QPushButton {
                    font-size: 16px;
                    padding: 12px 5px;
                    margin: 2px 0;
                }
                QPushButton:hover {
                    background-color: #e6e6e6;
                }
            """)
            my_music_layout.addWidget(button)
            if button_text == "最近播放":
                button.clicked.connect(lambda: self.display(self.stack.indexOf(self.recently_played)))
        left_layout.addLayout(my_music_layout)

        """创建的歌单"""
        play_list_label = QLabel("创建的歌单")
        play_list_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            margin-top: 20px;
            color: #666666;
            padding: 12px 5px;
        """)
        new_play_list_btn = QPushButton("+")
        new_play_list_btn.clicked.connect(self.create_new_play_list)
        create_row = QHBoxLayout()
        create_row.addWidget(play_list_label)
        create_row.addWidget(new_play_list_btn)

        left_layout.addLayout(create_row)
        play_list_layout = QVBoxLayout()
        play_list_layout.setObjectName("play_list_layout")
        left_layout.addLayout(play_list_layout)
        left_layout.addStretch(1)
        master_layout.addWidget(left_sidebar, 2)





        """右侧内容区域"""
        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(20, 10, 20, 10)

        """顶部操作栏"""
        top_bar_layout = QHBoxLayout()
        # 搜索栏
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍输入id后单击左侧“↓”下载")
        self.search_box.setFixedWidth(250)

        download_btn = QPushButton("↓")
        download_btn.clicked.connect(self.download_music_and_lyrics)

        top_bar_layout.addWidget(self.search_box)
        top_bar_layout.addWidget(download_btn)
        top_bar_layout.addStretch()

        content_layout.addLayout((top_bar_layout))

        """页面管理"""
        content_layout.addWidget(self.stack)

        """推荐/主页"""
        self.homepage = QWidget()
        self.homepageUI()
        self.stack.addWidget(self.homepage)

        """精选"""
        self.selected = QWidget()
        self.selectedUI()
        self.stack.addWidget(self.selected)

        self.stack.setCurrentWidget(self.homepage)
        master_layout.addWidget(content_area, 8)

        """最近播放"""
        self.recently_played = QWidget()
        self.recently_playedUI()
        self.stack.addWidget(self.recently_played)




    
        """底部区域"""
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
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                background-color: #e1e1e1;
                height: 2px;
            }
            QProgressBar::chunk {
                background-color: #c62f2f;
            }
        """)
        self.progress_bar.setRange(0, 1000)
        self.progress_bar.setValue(0)
        self.progress_bar.sliderPressed.connect(self.on_progress_bar_drag_start)
        self.progress_bar.sliderReleased.connect(self.on_progress_bar_drag_end)
        self.progress_timer.timeout.connect(self.update_progress)
        player_layout.addWidget(self.progress_bar)
        
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
            if(button_text == "⏮️"):
                button.clicked.connect(lambda: self.play_prev_song())
            elif(button_text == "⏯️"):
                button.clicked.connect(lambda: self.play_pause_song())
            else:
                button.clicked.connect(lambda: self.play_next_song())
        
        # 当前播放信息
        info_layout = QHBoxLayout()
        self.lyric_btn = QPushButton("-")
        self.lyric_btn.clicked.connect(self.display_lyric_page)

        song_info_layout = QVBoxLayout()
        self.song_title = QLabel()
        self.song_title.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.artist_name = QLabel()
        self.artist_name.setStyleSheet("font-size: 12px; color: #666666;")
        if self.is_playing == False:
            self.song_title.setText("当前无播放单曲")
            self.artist_name.setText("")

        song_info_layout.addWidget(self.song_title)
        song_info_layout.addWidget(self.artist_name)

        info_layout.addWidget(self.lyric_btn)
        info_layout.addLayout(song_info_layout)

        controls_layout.addLayout(info_layout)
        controls_layout.addStretch()
        
        # 音量控制
        self.volumn_slider = QSlider(Qt.Horizontal)
        self.volumn_slider.setRange(0, 1000)
        self.volumn_slider.setFixedWidth(100)
        self.volumn_slider.setValue(500)
        self.volumn_slider.sliderPressed.connect(self.on_volumn_slider_drag_start)
        self.volumn_slider.sliderReleased.connect(self.on_volumn_slider_drag_end)
        controls_layout.addWidget(QLabel("🔊"))
        controls_layout.addWidget(self.volumn_slider)
        
        player_layout.addLayout(controls_layout)

        master_master_layout.addLayout(master_layout)
        master_master_layout.addWidget(player_control)

    """主页和推荐页面的布局"""
    def homepageUI(self):
        layout = QVBoxLayout(self.homepage)

        """轮播图"""
        banner = QLabel()
        banner.setStyleSheet(
        """
        background-color: #f5f5f5;
        min-height: 200px;
        border-radius: 10px;
        font-size: 24px;
        font-weight: bold;
        color: #c62f2f;
        """
        )
        banner.setFixedSize(1000, 900)
        banner.setAlignment(Qt.AlignCenter)
        banner.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        layout.addWidget(banner, alignment=Qt.AlignCenter)

        self.images = ["imgs/banners/0.jpg", "imgs/banners/1.jpg", "imgs/banners/2.jpg", "imgs/banners/3.jpg", "imgs/banners/4.jpg"]
        self.current_image_index = 0

        self.show_next_image(banner)
        self.banner_timer.timeout.connect(lambda: self.show_next_image(banner))
        self.banner_timer.start(3000)

        """推荐歌单"""
        recommend_label = QLabel("热门推荐")
        recommend_label.setStyleSheet(
            "font-size: 20px; font-weight: bold; margin: 20px 0 10px 0;"
        )
        layout.addWidget(recommend_label)
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

            cover = ClickableLabel()
            cover.setAlignment(Qt.AlignCenter)
            cover.setStyleSheet("""
                background-color: #e1e1e1;
                border-radius: 5px;
                color: white;
                font-size: 18px;
            """)
            cover.setFixedHeight(150)
            cover.setFixedWidth(150)
            cover.setScaledContents(True)
            cover.setPixmap(QPixmap(f"imgs/recommends/{i}.jpg"))
            cover.setEnabled(True)
            cover.setCursor(Qt.PointingHandCursor)
            cover.setMouseTracking(True)
            cover.clicked.connect(lambda i=i: self.display(self.stack.indexOf(self.findChild(QWidget, self.recommends[i]))))

            title = QLabel(self.recommends[i])
            title.setStyleSheet("""
                font-size: 14px;
                color: #333333;
                margin-top: 5px;
            """)
            title.setWordWrap(True)

            playlist_layout.addWidget(cover)
            playlist_layout.addWidget(title)
            playlist_grid.addWidget(playlist_frame, i // 5, i % 5)

        layout.addLayout(playlist_grid)

    """所有新创建的歌单的模板布局"""
    def playlistUI_template(self, playlist_name, playlist_widget):
        layout = QVBoxLayout(playlist_widget)
        header_layout = QHBoxLayout()
        
        """歌单封面"""
        cover_label = QLabel()
        cover_label.setFixedSize(150, 150)
        cover_label.setStyleSheet("""
            background-color: #e1e1e1;
            border-radius: 10px;
        """)
        header_layout.addWidget(cover_label)
        
        info_layout = QVBoxLayout()
        
        """歌单标题"""
        playlist_title = QLabel(playlist_name)
        playlist_title.setStyleSheet("font-size: 24px; font-weight: bold;")
        info_layout.addWidget(playlist_title)
        
        """歌曲列表"""
        song_list = QListWidget()
        self.create_table_new_playlist(playlist_name)

        """按钮"""
        import_button = QPushButton("导入歌曲")
        import_button.setStyleSheet("""
            QPushButton {
                background-color: #c62f2f;
                color: white;
                padding: 6px 12px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #a62828;
            }
        """)

        play_button = QPushButton("播放歌曲")
        play_button.setStyleSheet("""
            QPushButton {
                background-color: #e1e1e1;
                color: #333;
                padding: 6px 12px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c6c6c6;
            }
        """)

        delete_button = QPushButton("移除歌曲")
        delete_button.setStyleSheet("""
            QPushButton {
                background-color: #e1e1e1;
                color: #333;
                padding: 6px 12px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c6c6c6;
            }
        """)

        delete_playlist_button = QPushButton("移除歌单")
        delete_playlist_button.setStyleSheet("""
            QPushButton {
                background-color: #e1e1e1;
                color: #333;
                padding: 6px 12px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c6c6c6;
            }
        """)

        info_layout.addWidget(import_button)
        info_layout.addWidget(play_button)
        info_layout.addWidget(delete_button)
        info_layout.addWidget(delete_playlist_button)
        
        import_button.clicked.connect(lambda: self.add_song(song_list, playlist_name))
        play_button.clicked.connect(lambda: self.play_selected_song(song_list, playlist_name))
        delete_button.clicked.connect(lambda: self.delete_song_in_playlist(song_list, playlist_name))
        delete_playlist_button.clicked.connect(lambda: self.delete_playlist(playlist_name))

        header_layout.addLayout(info_layout)
        layout.addLayout(header_layout)

        """分割线"""
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        layout.addWidget(song_list)
        self.load_songs_from_playlist(playlist_name, song_list)
        
    """在点击按钮后将内容区域的页面切换到对应的部件"""
    def display(self, i):
        self.stack.setCurrentIndex(i)

    """在第一次启动客户端时建立数据库，后面启动时打开数据库"""
    def create_db(self):
        """建立数据库"""
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        db_path = os.path.join(os.getcwd(), "iMusic.db")
        self.db.setDatabaseName(db_path)
        if not self.db.open():
            QMessageBox.critical(None, "Error", "Could not open your Database")
            sys.exit(1)

        query = QSqlQuery(self.db)
        query.exec_("""
            CREATE TABLE IF NOT EXISTS playlists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                table_name TEXT
            )
        """)

        query.exec_("""
            CREATE TABLE IF NOT EXISTS lyrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                song_name TEXT
            )
        """)

        # query.exec_("""
        #     CREATE TABLE IF NOT EXISTS recently_played (
        #         id INTEGER PRIMARY KEY AUTOINCREMENT,
        #         song_name TEXT
        #     )
        # """)

    """弹出QFileDialog来选中并导入本地存在的音频媒体文件"""
    def add_song(self, song_list, playlist_name):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择歌曲文件", "", "Audio Files (*.mp3 *.wav *.flac *.m4a)")
        if file_path:
            title = file_path.split('/')[-1]
            self.add_song_to_playlist(playlist_name, title, '', '', file_path)
            song_list.addItem(title)

    """把导入的歌的相关信息存到数据库中对应的歌单的表"""
    def add_song_to_playlist(self, playlist_name, title, artist, album, filepath):
        query = QSqlQuery(self.db)
        query.prepare("SELECT table_name FROM playlists WHERE name = ?")
        query.addBindValue(playlist_name)
        
        if not query.exec_():
            print("Failed to execute query:", query.lastError().text())
            return

        # 检查是否有记录返回
        if query.next():
            table_name = query.value(0)
        else:
            print("No table found for playlist:", playlist_name)
            return

        query.prepare(f"""
            INSERT INTO {table_name} (title, artist, album, filepath)
            VALUES (?, ?, ?, ?)
        """)
        query.addBindValue(title)
        query.addBindValue(artist)
        query.addBindValue(album)
        query.addBindValue(filepath)

        if query.exec_():
            print("Inserted:", title, "with path:", filepath)
        else:
            print("Insert failed:", query.lastError().text())

    """在选中某个歌单后从数据库表中加载对应歌单中已经存在的歌"""
    def load_songs_from_playlist(self, playlist_name, song_list):
        # 从 playlists 表中获取歌单对应的表名
        query = QSqlQuery(self.db)
        query.prepare("SELECT table_name FROM playlists WHERE name = ?")
        query.addBindValue(playlist_name)
        
        if not query.exec_():  # 确保执行查询并检查是否成功
            print("Query execution failed:", query.lastError().text())
            return

        if query.next():  # 仅在存在记录时获取值
            table_name = query.value(0)

            # 查询对应歌单表中的歌曲
            query.exec_(f"SELECT title FROM {table_name}")
            
            song_list.clear()
            while query.next():
                title = query.value(0)
                song_list.addItem(title)
        else:
            print(f"No table found for playlist: {playlist_name}")

    """播放歌单中被选中的歌"""
    def play_selected_song(self, song_list, current_playlist_name):
        selected_item = song_list.currentItem()
        if selected_item:
            title = selected_item.text()
            print(title)
            
            """获取当前播放列表的表名"""
            query = QSqlQuery(self.db)
            query.prepare("SELECT table_name FROM playlists WHERE name = ?")
            query.addBindValue(current_playlist_name)
            query.exec_()
            
            if query.next():
                table_name = query.value(0)
                self.current_table_name = table_name
                # 根据当前歌单表名查询歌曲的文件路径
                query.prepare(f"SELECT id, filepath FROM {table_name} WHERE title = ?")
                query.addBindValue(title)
                query.exec_()
                if query.next():
                    current_id = query.value(0)
                    # 获取前一首歌曲的路径 (id - 1)
                    query.prepare(f"SELECT filepath FROM {table_name} WHERE id = ?")
                    query.addBindValue(current_id - 1)
                    query.exec_()
                    self.previous_filepath = query.value(0) if query.next() else None

                    # 获取后一首歌曲的路径 (id + 1)
                    query.prepare(f"SELECT filepath FROM {table_name} WHERE id = ?")
                    query.addBindValue(current_id + 1)
                    query.exec_()
                    self.next_filepath = query.value(0) if query.next() else None

                    # 打印调试输出
                    print("Playing:", title)
                    print("Previous file path:", self.previous_filepath)
                    print("Next file path:", self.next_filepath)

                    # 播放当前选中歌曲
                    query.prepare(f"SELECT filepath, title, artist, album FROM {table_name} WHERE title = ?")
                    query.addBindValue(title)
                    query.exec_()
                    if query.next():
                        self.current_filepath = query.value(0)
                        self.current_song_title = query.value(1)
                        self.current_song_artist = query.value(2)
                        self.current_song_album = query.value(3)
                        self.play_song(self.current_filepath)
                    else:
                        print("No file path found for:", title)
                else:
                    print(f"No ID found for title: {title}")
            else:
                print(f"No table found for playlist: {current_playlist_name}")

    """利用pygame模块中的方法播放音频媒体文件"""
    def play_song(self, filepath):
        pygame.mixer.music.load(filepath)
        pygame.mixer.music.play()

        table_name = "playlist_最近播放"
        query = QSqlQuery(self.db)

        check_query = QSqlQuery(self.db)
        check_query.prepare(f"""
            SELECT COUNT(*) FROM {table_name} 
            WHERE filepath = ?
        """)
        check_query.addBindValue(self.current_filepath)
        check_query.exec_()

        if check_query.next():
            count = check_query.value(0)         
            if count == 0:
                query.prepare(f""" 
                    INSERT INTO {table_name} (title, artist, album, filepath) 
                    VALUES (?, ?, ?, ?) 
                """)
                query.addBindValue(self.current_song_title)
                query.addBindValue("")
                query.addBindValue("")
                query.addBindValue(self.current_filepath)
                query.exec_()
                self.recent_song_list.addItem(self.current_song_title)

        self.progress_timer.start(1000)
        self.is_playing = True
        self.song_duration = pygame.mixer.Sound(filepath).get_length()
        self.song_title.setText(self.current_song_title)
        self.artist_name.setText(self.current_song_artist)
        self.current_time = 0
        self.current_pos = 0
        
        if self.is_connected:
            self.lyric_timer.disconnect()
            self.is_connected = False

        base_title, _ = os.path.splitext(self.current_song_title)
        current_lyric_path = f"lyrics/{base_title}.lrc"
        self.parse_lrc(current_lyric_path)

    """创建新的歌单后在数据库内创建对应的新的歌单的数据表"""
    def create_table_new_playlist(self, playlist_name):
        """创建歌单时动态生成数据表"""
        table_name = f"playlist_{playlist_name.replace(' ', '_')}"
        
        """将歌单信息存储到 playlists 主表"""
        query = QSqlQuery(self.db)

        """在客户端启动载入已有歌单时，增加检查逻辑，如果数据库中已经存在同样名字的表，那么不创建新的表直接返回"""
        query.exec_(f"SELECT name FROM playlists WHERE name='{playlist_name}';")
        if query.next():
            return

        query.prepare("INSERT INTO playlists (name, table_name) VALUES (?, ?)")
        query.addBindValue(playlist_name)
        query.addBindValue(table_name)

        if not query.exec_():
            print("Failed to create playlist:", query.lastError().text())
            return

        """动态创建一个新表用于存储该歌单的歌曲"""
        query.exec_(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                artist TEXT,
                album TEXT,
                filepath TEXT
            )
        """)

    """再点击'+'后弹出窗口来创建新的歌单"""
    def create_new_play_list(self):
        text, ok = QInputDialog.getText(self, '新歌单', '请输入歌单名称:')
        query = QSqlQuery(self.db)
        query.prepare("SELECT table_name FROM playlists WHERE name = ?")
        query.addBindValue(text)
        query.exec_()
        if query.next():
            QMessageBox.warning(self, '歌单已存在', f'歌单 "{text}" 已存在，请使用其他名称。')
        else:
            if ok and text:
                self.play_lists.append(text)
                new_playlist_page = QWidget()
                new_playlist_page.setObjectName(text)
                self.playlistUI_template(text, new_playlist_page)
                self.stack.addWidget(new_playlist_page)
                self.add_playlist_button(text, new_playlist_page)

    """创建新的歌词页面"""
    def display_lyric_page(self):
        if not self.is_connected:
            self.lyric_timer.start(10)
            self.lyric_timer.timeout.connect(self.update_lyrics)
            self.is_connected = True
        self.display(self.stack.indexOf(self.findChild(QWidget, "lyric_page")))

    """在创建新的歌单之后在左侧边栏添加一个新的按钮"""
    def add_playlist_button(self, playlist_name, new_playlist_page):
        if playlist_name == "精选歌单" or playlist_name in self.recommends:
            return
        button = QPushButton(f"🎵 {playlist_name}")
        button.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                padding: 12px 5px;
                margin: 2px 0;
            }
            QPushButton:hover {
                background-color: #e6e6e6;
            }
        """)
        button.clicked.connect(lambda: self.display(self.stack.indexOf(new_playlist_page)))
        play_list_layout = self.findChild(QVBoxLayout, "play_list_layout")
        play_list_layout.addWidget(button)

    """在客户端启动时自动加载数据库中原先已创建的歌单"""
    def load_playlists_from_db(self):
        query = QSqlQuery(self.db)
        query.exec_("SELECT name FROM playlists")
        
        while query.next():
            playlist_name = query.value(0)
            if playlist_name in self.recommends or playlist_name == "最近播放":
                continue
            new_playlist_page = QWidget()
            new_playlist_page.setObjectName(playlist_name)
            self.playlistUI_template(playlist_name, new_playlist_page)
            self.stack.addWidget(new_playlist_page)
            self.add_playlist_button(playlist_name, new_playlist_page)

    """在客户端启动时自动创建数据表中记录的本应有的歌词界面控件"""
    def load_lyrics_pages_from_db(self):
        query = QSqlQuery(self.db)
        query.exec_("SELECT song_name FROM lyrics")
        
        while query.next():
            song_name = query.value(0)
            new_lyric_page = QWidget()
            new_lyric_page.setObjectName(song_name)
            self.lyricUI(new_lyric_page)
            self.stack.addWidget(new_lyric_page)

    """删除从歌单选中的歌曲并更新到数据库表"""
    def delete_song_in_playlist(self, song_list, current_playlist_name):
        selected_item = song_list.currentItem()
        if selected_item:
            title = selected_item.text()

            """获取当前播放列表的表名"""
            query = QSqlQuery(self.db)
            query.prepare("SELECT table_name FROM playlists WHERE name = ?")
            query.addBindValue(current_playlist_name)
            query.exec_()

            if query.next():
                table_name = query.value(0)
                query.prepare(f"DELETE FROM {table_name} WHERE title = ?")
                query.addBindValue(title)
                if query.exec_():
                    print(f"Removed: {title} from playlist: {current_playlist_name}")
                    # 更新列表视图
                    song_list.takeItem(song_list.currentRow())
                else:
                    print(f"Failed to remove: {title} from playlist: {current_playlist_name}")
            else:
                print(f"No table found for playlist: {current_playlist_name}")
                
    """切换下一张图片"""
    def show_next_image(self, banner):
        pixmap = QPixmap(self.images[self.current_image_index])
        banner.setPixmap(pixmap.scaled(banner.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.current_image_index = (self.current_image_index + 1) % len(self.images)

    """精选页面的布局"""
    def selectedUI(self):
        layout = QVBoxLayout(self.selected)
        header_layout = QHBoxLayout()
        
        """歌单封面"""
        cover_label = QLabel()
        cover_label.setFixedSize(150, 150)
        cover_label.setScaledContents(True)
        cover_label.setPixmap(QPixmap("imgs/selected.jpg"))
        cover_label.setStyleSheet("""
            background-color: #e1e1e1;
            border-radius: 10px;
        """)
        header_layout.addWidget(cover_label)
        
        info_layout = QVBoxLayout()
        
        """歌单标题"""
        playlist_title = QLabel('精选歌单')
        playlist_title.setStyleSheet("font-size: 24px; font-weight: bold;")
        info_layout.addWidget(playlist_title)
        
        """歌曲列表"""
        song_list = QListWidget()
        self.create_table_new_playlist('精选歌单')
        table_name = "playlist_精选歌单"
        query = QSqlQuery(self.db)
        query.prepare(f"INSERT INTO {table_name} (title, artist, album, filepath) VALUES (?, ?, ?, ?)")
        file_path = f"D:/C/iMusic/musics/selected/"            
        for filename in os.listdir(file_path):
            if filename.endswith(('.mp3', '.wav', '.flac')):
                filepath = os.path.join(file_path, filename)

                check_query = QSqlQuery(self.db)
                check_query.prepare(f"SELECT COUNT(*) FROM {table_name} WHERE title = ? AND filepath = ?")
                check_query.addBindValue(filename)
                check_query.addBindValue(filepath)
                check_query.exec_()
                check_query.next()
                count = check_query.value(0)

                if count == 0:
                    query.addBindValue(filename)
                    query.addBindValue("")
                    query.addBindValue("")
                    query.addBindValue(filepath)
                    query.exec_()

        """按钮"""
        play_button = QPushButton("播放歌曲")
        play_button.setStyleSheet("""
            QPushButton {
                background-color: #e1e1e1;
                color: #333;
                padding: 6px 12px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c6c6c6;
            }
        """)

        info_layout.addWidget(play_button)
        
        play_button.clicked.connect(lambda: self.play_selected_song(song_list, '精选歌单'))

        header_layout.addLayout(info_layout)
        layout.addLayout(header_layout)

        """分割线"""
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        layout.addWidget(song_list)
        self.load_songs_from_playlist('精选歌单', song_list)
    
    """精选页面的布局"""
    def recently_playedUI(self):
        layout = QVBoxLayout(self.recently_played)
        header_layout = QHBoxLayout()
        
        """歌单封面"""
        cover_label = QLabel()
        cover_label.setFixedSize(150, 150)
        cover_label.setStyleSheet("""
            background-color: #e1e1e1;
            border-radius: 10px;
        """)
        header_layout.addWidget(cover_label)
        
        info_layout = QVBoxLayout()
        
        """歌单标题"""
        playlist_title = QLabel('最近播放')
        playlist_title.setStyleSheet("font-size: 24px; font-weight: bold;")
        info_layout.addWidget(playlist_title)
        
        """歌曲列表"""
        self.recent_song_list = QListWidget()
        self.create_table_new_playlist('最近播放')

        """按钮"""
        play_button = QPushButton("播放歌曲")
        play_button.setStyleSheet("""
            QPushButton {
                background-color: #e1e1e1;
                color: #333;
                padding: 6px 12px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c6c6c6;
            }
        """)

        info_layout.addWidget(play_button)
        
        play_button.clicked.connect(lambda: self.play_selected_song(self.recent_song_list, '最近播放'))

        header_layout.addLayout(info_layout)
        layout.addLayout(header_layout)

        """分割线"""
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        layout.addWidget(self.recent_song_list)
        self.load_songs_from_playlist('最近播放', self.recent_song_list)
    
    """五个推荐专辑的布局"""
    def recommendUI(self, rec_widget, i):
        layout = QVBoxLayout(rec_widget)
        header_layout = QHBoxLayout()
        
        """歌单封面"""
        cover_label = QLabel()
        cover_label.setFixedSize(150, 150)
        cover_label.setStyleSheet("""
            background-color: #e1e1e1;
            border-radius: 10px;
        """)
        cover_label.setScaledContents(True)
        cover_label.setPixmap(QPixmap(f"imgs/recommends/{i}.jpg"))
        header_layout.addWidget(cover_label)
        
        info_layout = QVBoxLayout()
        
        """歌单标题"""
        playlist_title = QLabel(self.recommends[i])
        playlist_title.setStyleSheet("font-size: 24px; font-weight: bold;")
        info_layout.addWidget(playlist_title)
        
        """歌曲列表"""
        song_list = QListWidget()
        self.create_table_new_playlist(self.recommends[i])
        table_name = f"playlist_{self.recommends[i].replace(' ', '_')}"
        query = QSqlQuery(self.db)
        query.prepare(f"INSERT INTO {table_name} (title, artist, album, filepath) VALUES (?, ?, ?, ?)")
        file_path = f"D:/C/iMusic/musics/recommends/{self.recommends[i]}/"            
        for filename in os.listdir(file_path):
            if filename.endswith(('.mp3', '.wav', '.flac')):
                filepath = os.path.join(file_path, filename)

                check_query = QSqlQuery(self.db)
                check_query.prepare(f"SELECT COUNT(*) FROM {table_name} WHERE title = ? AND filepath = ?")
                check_query.addBindValue(filename)
                check_query.addBindValue(filepath)
                check_query.exec_()
                check_query.next()
                count = check_query.value(0)

                if count == 0:
                    query.addBindValue(filename)
                    query.addBindValue("")
                    query.addBindValue("")
                    query.addBindValue(filepath)
                    query.exec_()



        """按钮"""
        play_button = QPushButton("播放歌曲")
        play_button.setStyleSheet("""
            QPushButton {
                background-color: #e1e1e1;
                color: #333;
                padding: 6px 12px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c6c6c6;
            }
        """)

        info_layout.addWidget(play_button)
        
        play_button.clicked.connect(lambda: self.play_selected_song(song_list, self.recommends[i]))

        header_layout.addLayout(info_layout)
        layout.addLayout(header_layout)

        """分割线"""
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        layout.addWidget(song_list)
        self.load_songs_from_playlist(self.recommends[i], song_list)
    
    """歌词滚动界面布局"""
    def lyricUI(self, lyric_widget):
        lyric_layout = QVBoxLayout(lyric_widget)
        
        for _ in range(7):
            label = QLabel()
            label.setAlignment(Qt.AlignCenter)
            self.labels.append(label)
            lyric_layout.addWidget(label)

        self.labels[3].setStyleSheet("color: #FF4081; font-size: 16px;")
    def parse_lrc(self, lrc_path):
        self.lyrics_dict.clear()
        try:
            with open(lrc_path, 'r', encoding='utf-8') as f:
                lrc_content = f.read()

            pattern = r'\[(\d{2}):(\d{2})\.(\d{2,3})\](.*)'
            matches = re.findall(pattern, lrc_content)
            
            for match in matches:
                minutes, seconds, milliseconds = map(int, match[0:3])
                timestamp = minutes * 60 + seconds + milliseconds / 1000 - 1
                lyrics = match[3].strip()
                if lyrics:
                    self.lyrics_dict[timestamp] = lyrics
            
            self.lyrics_dict = dict(sorted(self.lyrics_dict.items()))
        except Exception as e:
            print(f"解析歌词文件出错: {str(e)}")
    def update_lyrics(self):
        if not self.lyrics_dict:
            return
        
        current_timestamp = None
        for timestamp in self.lyrics_dict.keys():
            if timestamp > self.current_time:
                break
            current_timestamp = timestamp
        if current_timestamp is None:
            return
        
        timestamps = list(self.lyrics_dict.keys())
        current_index = timestamps.index(current_timestamp);
        
        for i in range(7):
            index = current_index - 3 + i
            if 0 <= index < len(timestamps):
                self.labels[i].setText(self.lyrics_dict[timestamps[index]])
            else:
                self.labels[i].setText("")

    """删除从歌单选中的歌曲并更新到数据库表"""
    def delete_song_in_playlist(self, song_list, current_playlist_name):
        selected_item = song_list.currentItem()
        if selected_item:
            title = selected_item.text()

            """获取当前播放列表的表名"""
            query = QSqlQuery(self.db)
            query.prepare("SELECT table_name FROM playlists WHERE name = ?")
            query.addBindValue(current_playlist_name)
            query.exec_()

            if query.next():
                table_name = query.value(0)
                query.prepare(f"DELETE FROM {table_name} WHERE title = ?")
                query.addBindValue(title)
                if query.exec_():
                    print(f"Removed: {title} from playlist: {current_playlist_name}")
                    # 更新列表视图
                    song_list.takeItem(song_list.currentRow())
                else:
                    print(f"Failed to remove: {title} from playlist: {current_playlist_name}")
            else:
                print(f"No table found for playlist: {current_playlist_name}")
       
    """删除歌单并更新到数据库表"""
    def delete_playlist(self, playlist_name):
        """删除指定名字的歌单，并移除对应的按钮"""
        if playlist_name == "精选歌单":
            print("精选歌单无法删除")
            return
        
        # 获取表名
        table_name = f"playlist_{playlist_name.replace(' ', '_')}"
        
        # 检查歌单是否存在于 playlists 主表中
        query = QSqlQuery(self.db)
        query.exec_(f"SELECT name FROM playlists WHERE name='{playlist_name}';")
        
        if not query.next():
            print("歌单不存在")
            return

        # 删除 playlists 主表中的对应记录
        query.prepare("DELETE FROM playlists WHERE name = ?")
        query.addBindValue(playlist_name)

        if not query.exec_():
            print("Failed to delete playlist from playlists:", query.lastError().text())
            return

        # 删除动态生成的歌单数据表
        query.exec_(f"DROP TABLE IF EXISTS {table_name}")
        if query.lastError().isValid():
            print("Failed to delete playlist table:", query.lastError().text())
            return

        # 删除对应的按钮
        play_list_layout = self.findChild(QVBoxLayout, "play_list_layout")
        for i in range(play_list_layout.count()):
            widget = play_list_layout.itemAt(i).widget()
            if isinstance(widget, QPushButton) and widget.text() == f"🎵 {playlist_name}":
                # 从布局中移除并删除按钮
                play_list_layout.removeWidget(widget)
                widget.deleteLater()
                print(f"按钮 '{playlist_name}' 删除成功")
                break

        print(f"歌单 '{playlist_name}' 删除成功")
        self.display(self.stack.indexOf(self.homepage))
        
    """歌曲播放时更新进度条以及拖动进度条可控制歌曲播放进度"""
    def update_progress(self):
        if self.is_playing and self.is_dragging == False:
            self.current_time = self.current_pos / 1000
            progress_percentage = (self.current_time / self.song_duration) * 1000
            self.progress_bar.setValue(int(progress_percentage))
            self.current_pos += 1000
    def change_song_progress(self):
        new_value = self.progress_bar.value()
        self.current_time = (new_value / 1000) * self.song_duration

        if pygame.mixer.music.get_busy():
            pygame.mixer.music.set_pos(self.current_time)
        else:
            print("音乐不在播放状态，重新开始播放")
            pygame.mixer.music.play(start=self.current_time)

        self.current_pos = self.current_time * 1000
    def on_progress_bar_drag_start(self):
        self.is_dragging = True
        self.progress_timer.stop()
    def on_progress_bar_drag_end(self):
        self.is_dragging = False
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.play(start=self.current_time)
        else:
            self.change_song_progress()
        self.progress_timer.start(1000)


    """上一首/下一首/播放暂停 控制"""
    def play_prev_song(self):
        if(self.previous_filepath == None):
            print(f"没有上一首歌")
        else:
            query = QSqlQuery(self.db)
            query.prepare(f"SELECT id, title, artist, album FROM {self.current_table_name} WHERE filepath = ?")
            query.addBindValue(self.previous_filepath)
            query.exec_()
            if query.next():
                self.current_song_title = query.value(1)
                self.current_song_artist = query.value(2)
                self.current_song_album = query.value(3)
                self.current_filepath = self.previous_filepath
                self.play_song(self.previous_filepath)

            query.prepare(f"SELECT id FROM {self.current_table_name} WHERE filepath = ?")
            query.addBindValue(self.previous_filepath)
            query.exec_()
            if query.next():
                current_id = query.value(0)

                # 获取前一首歌曲的路径 (id - 1)
                query.prepare(f"SELECT filepath FROM {self.current_table_name} WHERE id = ?")
                query.addBindValue(current_id - 1)
                query.exec_()
                self.previous_filepath = query.value(0) if query.next() else None

                # 获取后一首歌曲的路径 (id + 1)
                query.prepare(f"SELECT filepath FROM {self.current_table_name} WHERE id = ?")
                query.addBindValue(current_id + 1)
                query.exec_()
                self.next_filepath = query.value(0) if query.next() else None

                print("Previous file path:", self.previous_filepath)
                print("Next file path:", self.next_filepath)
    def play_next_song(self):
        if(self.next_filepath == None):
            print(f"没有下一首歌")
        else:
            query = QSqlQuery(self.db)
            query.prepare(f"SELECT id, title, artist, album FROM {self.current_table_name} WHERE filepath = ?")
            query.addBindValue(self.next_filepath)
            query.exec_()
            if query.next():
                self.current_song_title = query.value(1)
                self.current_song_artist = query.value(2)
                self.current_song_album = query.value(3)
                self.current_filepath = self.next_filepath
                self.play_song(self.next_filepath)
            query = QSqlQuery(self.db)
            query.prepare(f"SELECT id FROM {self.current_table_name} WHERE filepath = ?")
            query.addBindValue(self.next_filepath)
            query.exec_()
            if query.next():
                current_id = query.value(0)
                
                # 获取前一首歌曲的路径 (id - 1)
                query.prepare(f"SELECT filepath FROM {self.current_table_name} WHERE id = ?")
                query.addBindValue(current_id - 1)
                query.exec_()
                self.previous_filepath = query.value(0) if query.next() else None

                # 获取后一首歌曲的路径 (id + 1)
                query.prepare(f"SELECT filepath FROM {self.current_table_name} WHERE id = ?")
                query.addBindValue(current_id + 1)
                query.exec_()
                self.next_filepath = query.value(0) if query.next() else None

                print("Previous file path:", self.previous_filepath)
                print("Next file path:", self.next_filepath)
    def play_pause_song(self):
        if(self.is_playing):
            pygame.mixer.music.pause()
            self.is_playing = False
            # self.progress_timer.stop()
            print(f"播放暂停")
        else:
            pygame.mixer.music.unpause()
            self.is_playing = True
            # self.progress_timer.start(100)
            print(f"播放继续")

    """音量控制"""
    def volumn_control(self):
        if not self.is_dragging:
            volumn_percentage = self.volumn_slider.value() / 1000
            self.current_volumn = volumn_percentage * 1
            pygame.mixer.music.set_volume(self.current_volumn)
    def on_volumn_slider_drag_start(self):
        self.is_dragging = True
    def on_volumn_slider_drag_end(self):
        self.is_dragging = False
        self.volumn_control()

    """实现通过id将网易云音源下载到本地"""
    def download_music_and_lyrics(self):
        song_id = self.search_box.text()
        self.MusicApi = MusicApi_wyy(song_id)
        music_url, title = self.MusicApi.get_wyy_url(song_id)[0], self.MusicApi.get_wyy_url(song_id)[1]
        with open(f"musics/{title}.mp3", 'wb') as f:
            f.write(requests.get(music_url, stream=True).content)

        lyric_content = self.MusicApi.get_wyy_lrc(song_id)
        with open(f"lyrics/{title}.lrc", 'w', encoding='utf-8') as f:
            f.write(lyric_content)
    
    """实现点击推荐专辑跳转至对应歌单"""
    def init_recommends_pages(self):
        for i in range(5):
            rec_page = QWidget()
            rec_page.setObjectName(self.recommends[i])
            self.recommendUI(rec_page, i)
            self.stack.addWidget(rec_page)

if __name__ in "__main__":
    app = QApplication(sys.argv)
    main = iMusic()
    main.show()
    sys.exit(app.exec_())
