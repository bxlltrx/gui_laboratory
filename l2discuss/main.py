import sys

from PyQt5.QtWidgets import QApplication

from cl1 import Data
from cl2 import Some


def main():
    app = QApplication(sys.argv)
    window = Some()
    model = Data(window)

    window.usd.valueChanged.connect(model.set_usd)
    window.rub.valueChanged.connect(model.set_rub)
    window.eur.valueChanged.connect(model.set_eur)
    window.usd_rate.valueChanged.connect(model.set_usd_rate)
    window.eur_rate.valueChanged.connect(model.set_eur_rate)
    model.amounts_changed.connect(window.update_amounts)
    window.reset_button.clicked.connect(lambda: model.set_rub(0.0))

    model.publish()
    window.show()
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())