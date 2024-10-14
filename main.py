import sys
import os
import pygame
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
    QProgressBar,
    QSlider,
    QSizePolicy,
    QStackedWidget,
    QListWidgetItem,
    QFileDialog,
    QMessageBox,
    QInputDialog
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlError
from PyQt5.QtGui import QIcon, QPixmap, QColor, QPalette

class iMusic(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = None
        self.create_db()
        self.play_lists = []
        self.stack = QStackedWidget(self)
        self.init_ui()
        self.load_playlists_from_db()
    
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
        master_layout = QHBoxLayout(central_widget)
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

        play_list_layout = QVBoxLayout()
        play_list_layout.setObjectName("play_list_layout")
        play_list_layout.addLayout(create_row)
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
        # self.selected = QWidget()
        # self.selectedUI()
        # self.stack.addWidget(self.selected)

        """歌单"""
        # self.playlist = QWidget()
        # self.playlistUI_template("list 1")
        # self.stack.addWidget(self.playlist)

        self.stack.setCurrentWidget(self.homepage)
        master_layout.addWidget(content_area, 8)
    
    """主页和推荐页面的布局"""
    def homepageUI(self):
        layout = QVBoxLayout(self.homepage)

        """轮播图"""
        banner = QLabel("热门推荐")
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

        info_layout.addWidget(import_button)
        info_layout.addWidget(play_button)
        info_layout.addWidget(delete_button)
        
        import_button.clicked.connect(lambda: self.add_song(song_list, playlist_name))
        play_button.clicked.connect(lambda: self.play_selected_song(song_list, playlist_name))
        delete_button.clicked.connect(lambda: self.delete_song_in_playlist(song_list, playlist_name))

        header_layout.addLayout(info_layout)
        layout.addLayout(header_layout)

        """分割线"""
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        layout.addWidget(song_list)
        self.load_songs_from_playlist(playlist_name, song_list)
        
    """再点击按钮后将内容区域的页面切换到对应的部件"""
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
                # 根据当前歌单表名查询歌曲的文件路径
                query.prepare(f"SELECT filepath FROM {table_name} WHERE title = ?")
                query.addBindValue(title)
                query.exec_()
                if query.next():
                    filepath = query.value(0)
                    print("Playing:", filepath)  # 添加调试输出
                    self.play_song(filepath)
                else:
                    print("No file path found for:", title)  # 添加调试输出
            else:
                print(f"No table found for playlist: {current_playlist_name}")

    """利用pygame模块中的方法播放音频媒体文件"""
    def play_song(self, filepath):
        try:
            pygame.mixer.init()
            pygame.mixer.music.load(filepath)
            pygame.mixer.music.play()
            print("Music is playing...")  # 添加调试输出
        except Exception as e:
            print("Error playing song:", e)  # 捕捉播放错误

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
        if ok and text:
            self.play_lists.append(text)
            new_playlist_page = QWidget()
            new_playlist_page.setObjectName(text)
            self.playlistUI_template(text, new_playlist_page)
            self.stack.addWidget(new_playlist_page)
            self.add_playlist_button(text, new_playlist_page)

    """在创建新的歌单之后在左侧边栏添加一个新的按钮"""
    def add_playlist_button(self, playlist_name, new_playlist_page):
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
                

if __name__ in "__main__":
    app = QApplication(sys.argv)
    main = iMusic()
    main.show()
    sys.exit(app.exec_())
