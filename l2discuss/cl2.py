from PyQt5.QtCore import Qt, QSignalBlocker, pyqtSlot
from PyQt5.QtWidgets import (
    QDoubleSpinBox, QFormLayout, QGroupBox, QLabel,
    QMainWindow, QPushButton, QVBoxLayout, QWidget,
)


class Some(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Converter")
        panel = QWidget()
        self.setCentralWidget(panel)
        layout = QVBoxLayout(panel)
        layout.setAlignment(Qt.AlignTop)
        layout.setSpacing(8)
        title = QLabel("Конвертер валют: доллар - рубль - евро")
        title.setWordWrap(True)
        layout.addWidget(title)

        amounts = QFormLayout()
        self.usd = self.make_field()
        self.rub = self.make_field()
        self.eur = self.make_field()
        amounts.addRow("Доллары (USD)", self.usd)
        amounts.addRow("Рубли (RUB)", self.rub)
        amounts.addRow("Евро (EUR)", self.eur)
        layout.addLayout(amounts)

        group = QGroupBox("курсы")
        rates = QFormLayout(group)
        self.usd_rate = self.make_field(rate=True)
        self.eur_rate = self.make_field(rate=True)
        self.usd_rate.setValue(82)
        self.eur_rate.setValue(92)
        rates.addRow("Рублей за 1 доллар", self.usd_rate)
        rates.addRow("Рублей за 1 евро", self.eur_rate)
        layout.addWidget(group)
        self.reset_button = QPushButton("Сбросить суммы")
        layout.addWidget(self.reset_button)
        self.resize(420, self.sizeHint().height())

    @staticmethod
    def make_field(rate=False):
        field = QDoubleSpinBox()
        field.setDecimals(4 if rate else 2)
        field.setRange(0.0001 if rate else 0, 1000000 if rate else 10**15)
        field.setSingleStep(1)
        field.setKeyboardTracking(False)
        field.setGroupSeparatorShown(True)
        return field

    @pyqtSlot(float, float, float)
    def update_amounts(self, usd, rub, eur):
        blockers = [QSignalBlocker(field) for field in (self.usd, self.rub, self.eur)]
        try:
            self.usd.setValue(usd)
            self.rub.setValue(rub)
            self.eur.setValue(eur)
        finally:
            for blocker in blockers:
                blocker.unblock()