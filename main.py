import sys
import os
import pygame
import re
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
    QScrollArea,
    QFrame,
    QGridLayout,
    QSlider,
    QSizePolicy,
    QStackedWidget,
    QFileDialog,
    QMessageBox,
    QInputDialog
)
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlError
from PyQt5.QtGui import QIcon, QPixmap, QColor, QPalette

class iMusic(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = None
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
        self.play_lists = []

        self.lyrics_dict = {}
        self.labels = []


        self.stack = QStackedWidget(self)
        self.banner_timer = QTimer(self)
        self.progress_timer = QTimer(self)
        self.progress_bar = QSlider(Qt.Horizontal)
        self.lyric_timer = QTimer(self)

        pygame.mixer.init()

        self.create_db()
        self.init_ui()
        self.load_playlists_from_db()
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
            ("🎙️", "精选"),
            ("📻", "播客"),
            ("📺", "漫游"),
            ("👥", "动态")
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
            ("🎵", "最近播放"),
            ("🎵", "下载管理"),
            ("🎵", "本地音乐")
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
        search_box = QLineEdit()
        search_box.setPlaceholderText("🔍 搜索音乐，歌手，歌词，用户")
        search_box.setFixedWidth(250)
        top_bar_layout.addWidget(search_box)
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
        volume_slider = QSlider(Qt.Horizontal)
        volume_slider.setFixedWidth(100)
        volume_slider.setValue(50)
        controls_layout.addWidget(QLabel("🔊"))
        controls_layout.addWidget(volume_slider)
        
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
        banner.setAlignment(Qt.AlignCenter)
        banner.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        layout.addWidget(banner)

        self.images = ["icon/1.png", "icon/2.png", "icon/3.png", "icon/4.png", "icon/5.png"]
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

    """弹出QFileDialog来选中并导入本地存在的音频媒体文件"""
    def add_song(self, song_list, playlist_name):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择歌曲文件", "", "Audio Files (*.mp3 *.wav *.flac *.m4a)")
        print(file_path)
        if file_path:
            title = file_path.split('/')[-1]
            self.add_song_to_playlist(playlist_name, title, '', '', file_path)
            song_list.addItem(title)

    """把导入的歌的相关信息存到数据库中对应的歌单的表"""
    def add_song_to_playlist(self, playlist_name, title, artist, album, filepath):
        # 先从 playlists 表获取歌单对应的表名
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

        # 将歌曲信息插入到对应的歌单表中
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
        print(filepath)
        pygame.mixer.music.load(filepath)
        pygame.mixer.music.play()
        self.progress_timer.start(1000)
        self.is_playing = True
        self.song_duration = pygame.mixer.Sound(filepath).get_length()
        self.song_title.setText(self.current_song_title)
        self.artist_name.setText(self.current_song_artist)
        print("Music is playing...")

        current_lyric_path = self.current_filepath.rsplit('.', 1)[0] + '.lrc'
        self.parse_lrc(current_lyric_path)


        """先查找在lyrics数据表中是否已经存在创建过歌词界面的歌"""
        query = QSqlQuery(self.db)
        query.prepare("SELECT song_name FROM lyrics WHERE song_name = ?")
        query.addBindValue(self.current_song_title)
        query.exec_()
        if query.next():
            return
        
        query.prepare("INSERT INTO lyrics (song_name) VALUES (?)")
        query.addBindValue(self.current_song_title)
        query.exec_()


        new_lyric_page = QWidget()
        new_lyric_page.setObjectName(self.current_song_title)
        self.lyricUI(new_lyric_page)
        self.stack.addWidget(new_lyric_page)

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
        self.lyric_timer.start(10)
        self.lyric_timer.timeout.connect(self.update_lyrics)
        self.update_lyrics()
        self.display(self.stack.indexOf(self.findChild(QWidget, self.current_song_title)))



    """在创建新的歌单之后在左侧边栏添加一个新的按钮"""
    def add_playlist_button(self, playlist_name, new_playlist_page):
        if playlist_name == "精选歌单":
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
        # 获取当前图片路径
        image_path = self.images[self.current_image_index]
        # 加载图片并设置到 QLabel
        pixmap = QPixmap(image_path)
        banner.setPixmap(pixmap.scaled(banner.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        # 更新图片索引
        self.current_image_index = (self.current_image_index + 1) % len(self.images)

    """精选页面的布局"""
    def selectedUI(self):
        layout = QVBoxLayout(self.selected)
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
        playlist_title = QLabel('精选歌单')
        playlist_title.setStyleSheet("font-size: 24px; font-weight: bold;")
        info_layout.addWidget(playlist_title)
        
        """歌曲列表"""
        song_list = QListWidget()
        self.create_table_new_playlist('精选歌单')

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

            pattern = r'\[(\d{2}):(\d{2})\.(\d{2})\](.*)'
            matches = re.findall(pattern, lrc_content)
            
            for match in matches:
                minutes, seconds, milliseconds = map(int, match[0:3])
                timestamp = minutes * 60 + seconds + milliseconds / 100 - 1
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
        current_index = timestamps.index(current_timestamp)
        
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
    
    # """进度条控制"""
    # def update_progress(self):
    #     if self.is_playing and self.is_dragging == False:
    #         self.current_time = self.current_pos / 1000
    #         progress_percentage = (self.current_time / self.song_duration) * 1000
    #         self.progress_bar.setValue(int(progress_percentage))
    #         print(self.current_pos, self.current_time, self.song_duration)

    # def change_song_progress(self):
    #     new_value = self.progress_bar.value()
    #     self.current_time = (new_value / 1000) * self.song_duration
    #     self.current_pos = self.current_time * 1000
    #     pygame.mixer.music.set_pos(self.current_time)
    # def on_progress_bar_drag_start(self):
    #     self.is_dragging = True
    #     self.progress_timer.stop()
    # def on_progress_bar_drag_end(self):
    #     self.is_dragging = False
    #     self.change_song_progress()
    #     self.progress_timer.start(1000)
        """进度条控制"""
    
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
        print(self.current_pos)
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
            self.progress_timer.stop()
            print(f"播放暂停")
        else:
            pygame.mixer.music.unpause()
            self.is_playing = True
            self.progress_timer.start(100)
            print(f"播放继续")

    """音量控制"""
    def volumn_control(self):
        pass


if __name__ in "__main__":
    app = QApplication(sys.argv)
    main = iMusic()
    main.show()
    sys.exit(app.exec_())
