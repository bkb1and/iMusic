import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLabel, QStackedWidget)
from PyQt5.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("页面跳转测试")
        self.setGeometry(100, 100, 600, 400)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QHBoxLayout(central_widget)
        
        nav_widget = QWidget()
        nav_layout = QVBoxLayout(nav_widget)
        
        self.btn_page1 = QPushButton("页面 1")
        self.btn_page2 = QPushButton("页面 2")
        self.btn_page3 = QPushButton("页面 3")
        
        nav_layout.addWidget(self.btn_page1)
        nav_layout.addWidget(self.btn_page2)
        nav_layout.addWidget(self.btn_page3)
        nav_layout.addStretch()
        
        self.stack = QStackedWidget()
        
        self.page1 = self.create_page("这是第一个页面")
        self.page2 = self.create_page("这是第二个页面")
        self.page3 = self.create_page("这是第三个页面")
        
        self.stack.addWidget(self.page1)
        self.stack.addWidget(self.page2)
        self.stack.addWidget(self.page3)
        
        self.btn_page1.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.btn_page2.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        self.btn_page3.clicked.connect(lambda: self.stack.setCurrentIndex(2))
        
        layout.addWidget(nav_widget)
        layout.addWidget(self.stack)
        
        layout.setStretch(0, 1)
        layout.setStretch(1, 4)

    def create_page(self, text):
        """创建示例页面"""
        page = QWidget()
        layout = QVBoxLayout(page)
        
        label = QLabel(text)
        label.setAlignment(Qt.AlignCenter)
        
        content = QWidget()
        
        layout.addWidget(label)
        layout.addWidget(content)
        layout.addStretch()
        
        return page

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())