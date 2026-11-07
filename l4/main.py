import sys
from pathlib import Path

from PyQt5.QtCore import QUrl, QObject, QTimer, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QApplication
from PyQt5.QtQml import QQmlApplicationEngine


class Interface(QObject):
    saveRequested = pyqtSignal(str, arguments=['path'])
    statusChanged = pyqtSignal(str, arguments=['message'])

    def __init__(self, output_path=None, interval_ms=5000):
        super().__init__()
        self.output_path = Path(output_path or Path(__file__).with_name('autosave.png')).resolve()
        self.timer = QTimer(self)
        self.timer.setInterval(interval_ms)
        self.timer.timeout.connect(self.save_canvas)

    @pyqtSlot()
    def start(self):
        self.timer.start()

    @pyqtSlot()
    def save_canvas(self):
        self.saveRequested.emit(str(self.output_path))

    @pyqtSlot(bool)
    def save_finished(self, success):
        if success:
            self.statusChanged.emit('Сохранено: ' + str(self.output_path))
        else:
            self.statusChanged.emit('Ошибка сохранения: ' + str(self.output_path))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    interface = Interface()
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty('_backend', interface)
    engine.load(QUrl.fromLocalFile(str(Path(__file__).with_name('mainWindow.qml').resolve())))
    if not engine.rootObjects():
        print('Ошибка: не удалось загрузить QML файл!')
        sys.exit(1)
    interface.start()
    app.aboutToQuit.connect(interface.timer.stop)
    sys.exit(app.exec_())
