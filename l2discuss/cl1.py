from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot


class Data(QObject):
    amounts_changed = pyqtSignal(float, float, float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.usd_rate = 82.0
        self.eur_rate = 92.0
        self.rubles = 0.0

    def publish(self):
        self.amounts_changed.emit(
            self.rubles / self.usd_rate,
            self.rubles,
            self.rubles / self.eur_rate,
        )

    @pyqtSlot(float)
    def set_usd(self, value):
        self.rubles = value * self.usd_rate
        self.publish()

    @pyqtSlot(float)
    def set_rub(self, value):
        self.rubles = value
        self.publish()

    @pyqtSlot(float)
    def set_eur(self, value):
        self.rubles = value * self.eur_rate
        self.publish()

    @pyqtSlot(float)
    def set_usd_rate(self, value):
        if value > 0:
            self.usd_rate = value
            self.publish()

    @pyqtSlot(float)
    def set_eur_rate(self, value):
        if value > 0:
            self.eur_rate = value
            self.publish()