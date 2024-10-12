from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QListWidget, QVBoxLayout, QFileDialog
from PyQt5.QtSql import QSqlDatabase, QSqlQuery
import pygame

class MusicPlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.create_database()
        self.load_songs()

    def init_ui(self):
        self.setWindowTitle('Music Player')
        
        self.layout = QVBoxLayout()
        self.song_list = QListWidget()
        self.add_song_button = QPushButton('Add Song')
        self.play_button = QPushButton('Play Song')

        self.layout.addWidget(self.song_list)
        self.layout.addWidget(self.add_song_button)
        self.layout.addWidget(self.play_button)

        self.setLayout(self.layout)

        self.add_song_button.clicked.connect(self.add_song)
        self.play_button.clicked.connect(self.play_selected_song)

    def create_database(self):
        db = QSqlDatabase.addDatabase('QSQLITE')
        db.setDatabaseName('music.db')
        if not db.open():
            print("无法打开数据库")
        else:
            query = QSqlQuery()
            query.exec_('''
                CREATE TABLE IF NOT EXISTS songs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    artist TEXT,
                    album TEXT,
                    filepath TEXT
                )
            ''')

    def add_song(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择歌曲文件", "", "Audio Files (*.mp3 *.wav *.flac)")
        print(file_path)
        if file_path:
            # 这里可以让用户输入歌曲的其他信息
            title = file_path.split('/')[-1]  # 获取文件名作为标题
            self.add_song_to_db(title, '', '', file_path)
            self.song_list.addItem(title)

    def add_song_to_db(self, title, artist, album, filepath):
        query = QSqlQuery()
        query.prepare('''
            INSERT INTO songs (title, artist, album, filepath) VALUES (?, ?, ?, ?)
        ''')
        query.addBindValue(title)
        query.addBindValue(artist)
        query.addBindValue(album)
        query.addBindValue(filepath)
        query.exec_()

    def load_songs(self):
        query = QSqlQuery("SELECT title FROM songs")
        while query.next():
            title = query.value(0)
            self.song_list.addItem(title)

    def play_selected_song(self):
        selected_item = self.song_list.currentItem()
        if selected_item:
            title = selected_item.text()
            query = QSqlQuery()
            query.prepare("SELECT filepath FROM songs WHERE title = ?")
            query.addBindValue(title)
            query.exec_()
            if query.next():
                filepath = query.value(0)
                self.play_song(filepath)

    def play_song(self, filepath):
        pygame.mixer.init()
        pygame.mixer.music.load(filepath)
        pygame.mixer.music.play()

if __name__ == '__main__':
    app = QApplication([])
    player = MusicPlayer()
    player.show()
    app.exec_()
