import sys
import sqlite3
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QPushButton,
    QLineEdit, QLabel, QWidget, QMessageBox, QDateEdit, QTableWidget, QTableWidgetItem
)
from PyQt6.QtCore import QDate

# Вспомогательная функция для выполнения SQL-запросов
def execute_query(query, params=(), fetch=False):
    conn = sqlite3.connect("hotel.db")
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        if fetch:
            result = cursor.fetchall()
        else:
            conn.commit()
            result = None
    except sqlite3.Error as e:
        QMessageBox.critical(None, "Ошибка", f"Ошибка базы данных: {e}")
        result = None
    finally:
        conn.close()
    return result


# Функция для создания базы данных при первом запуске
def create_database():
    execute_query("""
    CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT NOT NULL
    )
    """)
    execute_query("""
    CREATE TABLE IF NOT EXISTS rooms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        room_number TEXT NOT NULL,
        room_type TEXT NOT NULL
    )
    """)
    execute_query("""
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER NOT NULL,
        room_id INTEGER NOT NULL,
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        FOREIGN KEY(client_id) REFERENCES clients(id),
        FOREIGN KEY(room_id) REFERENCES rooms(id)
    )
    """)
    # Таблица для хранения логинов и паролей
    execute_query("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL
    )
    """)

# Вставка тестового пользователя
def insert_test_user():
    execute_query("INSERT INTO users (username, password) VALUES (?, ?)", ('student', 'password24#%'))

# Окно для авторизации
class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Авторизация")
        self.setGeometry(200, 200, 300, 150)

        self.layout = QVBoxLayout()

        self.username_label = QLabel("Логин:")
        self.username_input = QLineEdit()
        self.layout.addWidget(self.username_label)
        self.layout.addWidget(self.username_input)

        self.password_label = QLabel("Пароль:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.layout.addWidget(self.password_label)
        self.layout.addWidget(self.password_input)

        self.login_button = QPushButton("Войти")
        self.login_button.clicked.connect(self.check_login)
        self.layout.addWidget(self.login_button)

        self.setLayout(self.layout)

    def check_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        # Проверяем логин и пароль в базе данных
        result = execute_query("SELECT * FROM users WHERE username=? AND password=?", (username, password), fetch=True)
        if result:
            QMessageBox.information(self, "Успех", "Авторизация успешна!")
            self.accept_login()
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль!")

    def accept_login(self):
        # Если авторизация прошла успешно, закрываем окно авторизации и открываем главное окно
        self.close()
        self.main_window = MainWindow()
        self.main_window.show()


# Окно для отображения списка с базой данных
class TableWindow(QWidget):
    def __init__(self, title, query, headers):
        super().__init__()
        self.setWindowTitle(title)
        self.setGeometry(300, 300, 600, 400)

        self.layout = QVBoxLayout()
        self.table = QTableWidget()
        self.layout.addWidget(self.table)

        self.setLayout(self.layout)
        self.load_data(query, headers)

    def load_data(self, query, headers):
        data = execute_query(query, fetch=True)
        if data:
            self.table.setRowCount(len(data))
            self.table.setColumnCount(len(data[0]))
            self.table.setHorizontalHeaderLabels(headers)

            for row_idx, row in enumerate(data):
                for col_idx, value in enumerate(row):
                    self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
        else:
            QMessageBox.information(self, "Информация", "Данные отсутствуют.")


# Окно для добавления клиентов
class AddClientWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Добавить клиента")
        self.setGeometry(200, 200, 400, 200)

        self.layout = QVBoxLayout()

        self.name_label = QLabel("Имя клиента:")
        self.name_input = QLineEdit()
        self.layout.addWidget(self.name_label)
        self.layout.addWidget(self.name_input)

        self.phone_label = QLabel("Телефон:")
        self.phone_input = QLineEdit()
        self.layout.addWidget(self.phone_label)
        self.layout.addWidget(self.phone_input)

        self.add_button = QPushButton("Добавить клиента")
        self.add_button.clicked.connect(self.add_client)
        self.layout.addWidget(self.add_button)

        self.setLayout(self.layout)

    def add_client(self):
        name = self.name_input.text()
        phone = self.phone_input.text()

        if name and phone:
            execute_query("INSERT INTO clients (name, phone) VALUES (?, ?)", (name, phone))
            QMessageBox.information(self, "Успех", "Клиент добавлен!")
        else:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля!")


# Окно для добавления номера
class AddRoomWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Добавить номер")
        self.setGeometry(200, 200, 400, 200)

        self.layout = QVBoxLayout()

        self.room_number_label = QLabel("Номер комнаты:")
        self.room_number_input = QLineEdit()
        self.layout.addWidget(self.room_number_label)
        self.layout.addWidget(self.room_number_input)

        self.room_type_label = QLabel("Тип комнаты:")
        self.room_type_input = QLineEdit()
        self.layout.addWidget(self.room_type_label)
        self.layout.addWidget(self.room_type_input)

        self.add_button = QPushButton("Добавить номер")
        self.add_button.clicked.connect(self.add_room)
        self.layout.addWidget(self.add_button)

        self.setLayout(self.layout)

    def add_room(self):
        room_number = self.room_number_input.text()
        room_type = self.room_type_input.text()
        if room_number and room_type:
            execute_query("INSERT INTO rooms (room_number, room_type) VALUES (?, ?)", (room_number, room_type))
            QMessageBox.information(self, "Успех", "Номер добавлен!")
        else:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля!")


# Окно для добавления бронирования
class AddBookingWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Добавить бронирование")
        self.setGeometry(200, 200, 400, 300)

        self.layout = QVBoxLayout()

        self.client_id_label = QLabel("ID клиента:")
        self.client_id_input = QLineEdit()
        self.layout.addWidget(self.client_id_label)
        self.layout.addWidget(self.client_id_input)

        self.room_id_label = QLabel("ID номера:")
        self.room_id_input = QLineEdit()
        self.layout.addWidget(self.room_id_label)
        self.layout.addWidget(self.room_id_input)

        self.start_date_label = QLabel("Дата начала:")
        self.start_date_input = QDateEdit()
        self.start_date_input.setDate(QDate.currentDate())
        self.layout.addWidget(self.start_date_label)
        self.layout.addWidget(self.start_date_input)

        self.end_date_label = QLabel("Дата окончания:")
        self.end_date_input = QDateEdit()
        self.end_date_input.setDate(QDate.currentDate())
        self.layout.addWidget(self.end_date_label)
        self.layout.addWidget(self.end_date_input)

        self.add_button = QPushButton("Добавить бронирование")
        self.add_button.clicked.connect(self.add_booking)
        self.layout.addWidget(self.add_button)

        self.setLayout(self.layout)

    def add_booking(self):
        client_id = self.client_id_input.text()
        room_id = self.room_id_input.text()
        start_date = self.start_date_input.date().toString("yyyy-MM-dd")
        end_date = self.end_date_input.date().toString("yyyy-MM-dd")

        if client_id and room_id and start_date and end_date:
            execute_query(
                "INSERT INTO bookings (client_id, room_id, start_date, end_date) VALUES (?, ?, ?, ?)",
                (client_id, room_id, start_date, end_date)
            )
            QMessageBox.information(self, "Успех", "Бронирование добавлено!")
        else:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля!")


# Главное окно
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Система Клиент Отеля")
        self.setGeometry(100, 100, 400, 400)

        self.layout = QVBoxLayout()

        self.clients_button = QPushButton("Добавить клиента")
        self.clients_button.clicked.connect(self.open_add_client_window)
        self.layout.addWidget(self.clients_button)

        self.rooms_button = QPushButton("Добавить номер")
        self.rooms_button.clicked.connect(self.open_add_room_window)
        self.layout.addWidget(self.rooms_button)

        self.bookings_button = QPushButton("Добавить бронирование")
        self.bookings_button.clicked.connect(self.open_add_booking_window)
        self.layout.addWidget(self.bookings_button)

        self.view_clients_button = QPushButton("Просмотреть клиентов")
        self.view_clients_button.clicked.connect(self.view_clients)
        self.layout.addWidget(self.view_clients_button)

        self.view_rooms_button = QPushButton("Просмотреть номера")
        self.view_rooms_button.clicked.connect(self.view_rooms)
        self.layout.addWidget(self.view_rooms_button)

        self.view_bookings_button = QPushButton("Просмотреть бронирования")
        self.view_bookings_button.clicked.connect(self.view_bookings)
        self.layout.addWidget(self.view_bookings_button)

        central_widget = QWidget()
        central_widget.setLayout(self.layout)
        self.setCentralWidget(central_widget)

    def open_add_client_window(self):
        self.add_client_window = AddClientWindow()
        self.add_client_window.show()

    def open_add_room_window(self):
        self.add_room_window = AddRoomWindow()
        self.add_room_window.show()

    def open_add_booking_window(self):
        self.add_booking_window = AddBookingWindow()
        self.add_booking_window.show()

    def view_clients(self):
        self.clients_table = TableWindow("Клиенты", "SELECT * FROM clients", ["ID", "Имя", "Телефон"])
        self.clients_table.show()

    def view_rooms(self):
        self.rooms_table = TableWindow("Номера", "SELECT * FROM rooms", ["ID", "Номер", "Тип"])
        self.rooms_table.show()

    def view_bookings(self):
        self.bookings_table = TableWindow(
            "Бронирования",
            "SELECT * FROM bookings",
            ["ID", "ID клиента", "ID номера", "Дата начала", "Дата окончания"]
        )
        self.bookings_table.show()


# Главная точка входа в программу
if __name__ == "__main__":
    # Создаем базу данных при первом запуске
    create_database()

    # Добавляем тестового пользователя (это можно вызвать один раз для добавления теста)
    insert_test_user()

    # Запускаем приложение
    app = QApplication(sys.argv)

    # Окно авторизации
    login_window = LoginWindow()
    login_window.show()

    sys.exit(app.exec())
