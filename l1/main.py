import sys
from pathlib import Path
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Текст и изображение')
        self.setFixedSize(400, 480)
        self.image_visible = False
        self.picture = QPixmap(str(Path(__file__).with_name('image.jpg')))
        self.label = QLabel('Нажмите кнопку, чтобы увидеть изображение')
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setWordWrap(True)
        self.label.setMinimumSize(360, 390)
        self.button = QPushButton('Показать изображение')
        self.button.clicked.connect(self.toggle_content)
        layout = QVBoxLayout(self)
        layout.addWidget(self.label, 1)
        layout.addWidget(self.button)

    def toggle_content(self):
        if not self.image_visible:
            if self.picture.isNull():
                self.label.setText('Не найден файл image.jpg рядом с main.py')
                return
            self.label.setPixmap(self.picture.scaled(
                self.label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.button.setText('Вернуть надпись')
            self.image_visible = True
        else:
            self.label.setText('Нажмите кнопку, чтобы увидеть изображение')
            self.button.setText('Показать изображение')
            self.image_visible = False


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
