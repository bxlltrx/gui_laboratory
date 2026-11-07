import sqlite3
import sys
from pathlib import Path

from PyQt5.QtCore import Qt, QAbstractTableModel
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QGridLayout,
    QPushButton, QComboBox, QTabWidget, QTableView, QFileDialog,
    QMessageBox, QLabel, QHeaderView,
)


class QueryModel(QAbstractTableModel):
    def __init__(self, headers=(), rows=(), parent=None):
        super().__init__(parent)
        self.headers = headers
        self.rows = rows

    def rowCount(self, parent=None):
        return 0 if parent is not None and parent.isValid() else len(self.rows)

    def columnCount(self, parent=None):
        return 0 if parent is not None and parent.isValid() else len(self.headers)

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid() and role == Qt.DisplayRole:
            value = self.rows[index.row()][index.column()]
            if value is None:
                return 'NULL'
            if isinstance(value, bytes):
                return value.hex()
            return str(value)
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.headers[section] if 0 <= section < len(self.headers) else None
            return str(section + 1) if 0 <= section < len(self.rows) else None
        return None


def quote_identifier(name):
    return '"' + name.replace('"', '""') + '"'


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.connection = None
        self.setWindowTitle('SQLite Viewer')
        self.resize(850, 480)
        menu = self.menuBar().addMenu('Menu')
        menu.addAction('Set connection', self.open_database)
        menu.addAction('Close connection', self.close_connection)

        panel = QWidget()
        self.setCentralWidget(panel)
        layout = QVBoxLayout(panel)
        controls = QGridLayout()
        self.bt1 = QPushButton('bt1 — SELECT name')
        self.columns = QComboBox()
        self.columns.setPlaceholderText('Выберите столбец sqlite_master')
        self.bt2 = QPushButton('bt2 — Показать таблицу')
        self.bt3 = QPushButton('bt3 — Сведения о столбцах')
        self.tables = QComboBox()
        self.tables.setPlaceholderText('Выберите таблицу')
        controls.addWidget(self.bt1, 0, 0)
        controls.addWidget(self.columns, 0, 1)
        controls.addWidget(QLabel('Таблица для bt2 и bt3'), 1, 0)
        controls.addWidget(self.tables, 1, 1)
        controls.addWidget(self.bt2, 2, 0)
        controls.addWidget(self.bt3, 2, 1)
        layout.addLayout(controls)
        self.tabs = QTabWidget()
        self.views = []
        for i in range(5):
            view = QTableView()
            view.setAlternatingRowColors(True)
            view.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
            view.horizontalHeader().setStretchLastSection(True)
            self.views.append(view)
            self.tabs.addTab(view, f'Tab{i + 1}')
        layout.addWidget(self.tabs)
        self.bt1.clicked.connect(lambda: self.query('SELECT name FROM sqlite_master', 1))
        self.columns.currentTextChanged.connect(self.show_column)
        self.bt2.clicked.connect(self.show_table)
        self.bt3.clicked.connect(self.show_structure)
        self.set_connected(False)
        self.statusBar().showMessage('Выберите Menu → Set connection')

    def set_connected(self, connected):
        for control in (self.bt1, self.columns, self.tables):
            control.setEnabled(connected)
        has_tables = connected and self.tables.count() > 0
        self.bt2.setEnabled(has_tables)
        self.bt3.setEnabled(has_tables)

    def open_database(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, 'Выберите базу SQLite', str(Path(__file__).parent),
            'SQLite (*.db *.sqlite *.sqlite3);;Все файлы (*)',
        )
        if not filename:
            return
        candidate = None
        try:
            candidate = sqlite3.connect(Path(filename).resolve().as_uri() + '?mode=ro', uri=True)
            cursor = candidate.execute('SELECT * FROM sqlite_master')
            headers = [item[0] for item in cursor.description]
            rows = cursor.fetchall()
            tables = [row[0] for row in candidate.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            )]
        except sqlite3.Error as error:
            if candidate is not None:
                candidate.close()
            QMessageBox.warning(self, 'Ошибка соединения', str(error))
            return
        self.close_connection()
        self.connection = candidate
        self.display(0, headers, rows)
        self.columns.blockSignals(True)
        self.columns.addItems(headers)
        self.columns.setCurrentIndex(-1)
        self.columns.blockSignals(False)
        self.tables.addItems(tables)
        self.set_connected(True)
        self.statusBar().showMessage(str(filename))

    def display(self, tab, headers, rows):
        view = self.views[tab]
        previous = view.model()
        view.setModel(QueryModel(headers, rows, view))
        if previous is not None:
            previous.deleteLater()
        view.resizeColumnsToContents()
        self.tabs.setCurrentIndex(tab)

    def query(self, sql, tab):
        if self.connection is None:
            return
        try:
            cursor = self.connection.execute(sql)
            self.display(tab, [item[0] for item in cursor.description], cursor.fetchall())
        except sqlite3.Error as error:
            QMessageBox.warning(self, 'Ошибка SQL', str(error))

    def show_column(self, name):
        if name:
            self.query(f'SELECT {quote_identifier(name)} FROM sqlite_master', 2)

    def show_table(self):
        name = self.tables.currentText()
        if name:
            self.query(f'SELECT * FROM {quote_identifier(name)}', 3)

    def show_structure(self):
        name = self.tables.currentText()
        if name:
            self.query(f'PRAGMA table_info({quote_identifier(name)})', 4)

    def close_connection(self):
        if self.connection is not None:
            self.connection.close()
            self.connection = None
        self.columns.blockSignals(True)
        self.columns.clear()
        self.columns.blockSignals(False)
        self.tables.clear()
        for i in range(5):
            self.display(i, (), ())
        self.tabs.setCurrentIndex(0)
        self.set_connected(False)
        self.statusBar().showMessage('Соединение закрыто')

    def closeEvent(self, event):
        self.close_connection()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    demo = Path(__file__).with_name('demo.db')
    if not demo.exists():
        try:
            from create_demo import create_database
            create_database(demo)
        except (OSError, sqlite3.Error) as error:
            QMessageBox.warning(
                None, 'Не удалось создать demo.db', str(error)
            )

    window = Window()
    window.show()
    sys.exit(app.exec_())