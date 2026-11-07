import sqlite3
from pathlib import Path


def create_database(path):
    path = Path(path)
    with path.open('xb'):
        pass
    connection = sqlite3.connect(path)
    try:
        with connection:
            connection.executescript('''
                CREATE TABLE students (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    group_name TEXT NOT NULL
                );
                CREATE TABLE grades (
                    id INTEGER PRIMARY KEY,
                    student_id INTEGER REFERENCES students(id),
                    subject TEXT NOT NULL,
                    grade INTEGER CHECK(grade BETWEEN 2 AND 5)
                );
            ''')
            connection.executemany('INSERT INTO students VALUES (?, ?, ?)', [
                (1, 'Иван Петров', 'ИС-21'),
                (2, 'Анна Смирнова', 'ИС-21'),
                (3, 'Олег Иванов', 'ИС-22'),
            ])
            connection.executemany('INSERT INTO grades VALUES (?, ?, ?, ?)', [
                (1, 1, 'Программирование', 5),
                (2, 2, 'Программирование', 4),
                (3, 3, 'Базы данных', 5),
            ])
    finally:
        connection.close()


if __name__ == '__main__':
    target = Path(__file__).with_name('demo.db')
    if target.exists():
        print('demo.db уже существует')
    else:
        create_database(target)
        print('Создана demo.db')