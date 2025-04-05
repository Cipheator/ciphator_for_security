#!/bin/python3

import os
import shutil
import sys
import traceback
import time
from hashlib import sha256
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QButtonGroup, 
                            QHBoxLayout, QLabel, QLineEdit, QPushButton, QDialog,
                            QMessageBox, QFileDialog, QTextEdit, QFormLayout, QRadioButton)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon

def wait_for_file(filename: str, directory: str = '.', timeout: int = 3600, check_interval: float = 1.0):
    # directory: str = '/dev/shm/transfer/'
    start_time = time.time()
    
    while True:
        # Проверка оставшегося времени
        if time.time() - start_time > timeout:
            print(f"Таймаут: файл {filename} не появился за {timeout} секунд")
            return ""
        
        # Полный путь к потенциальному файлу
        full_path = os.path.join(directory, filename)
        
        # Проверка существования файла
        if os.path.exists(full_path):
            print(f"Файл {filename} найден по пути {full_path}")
            return full_path
        
        # Пауза между проверками
        time.sleep(check_interval)
        
def exit_files():
    files = []
    for file in files:
        if os.path.exists(fil):
            os.remove(file)


class ChangeCredentialsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Настройка диалогового окна
        self.setWindowTitle("Изменение учетных данных")
        self.setFixedSize(300, 250)
        
        # Создание основного макета
        layout = QVBoxLayout()
        
        # Заголовок
        title_label = QLabel("Введите новые учетные данные")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        layout.addSpacing(20)
        
        # Логин
        login_layout = QHBoxLayout()
        login_label = QLabel("Новый логин:")
        self.login_input = QLineEdit()
        login_layout.addWidget(login_label)
        login_layout.addWidget(self.login_input)
        layout.addLayout(login_layout)
        
        # Пароль
        password_layout = QHBoxLayout()
        password_label = QLabel("Новый пароль:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        layout.addLayout(password_layout)
        
        # Подтверждение пароля
        confirm_layout = QHBoxLayout()
        confirm_label = QLabel("Подтвердите пароль:")
        self.confirm_input = QLineEdit()
        self.confirm_input.setEchoMode(QLineEdit.Password)
        confirm_layout.addWidget(confirm_label)
        confirm_layout.addWidget(self.confirm_input)
        layout.addLayout(confirm_layout)
        
        # Кнопки
        button_layout = QHBoxLayout()
        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(self.save_credentials)
        cancel_button = QPushButton("Отмена")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        
    def delete_files(self):
        exit_files()
        self.reject()
    
    def save_credentials(self):
        # Проверка заполненности полей
        login = self.login_input.text().strip()
        password = self.password_input.text()
        confirm_password = self.confirm_input.text()
        
        # Валидация данных
        if not login:
            QMessageBox.warning(self, "Ошибка", "Логин не может быть пустым")
            return
        
        if not password:
            QMessageBox.warning(self, "Ошибка", "Пароль не может быть пустым")
            return
        
        if password != confirm_password:
            QMessageBox.warning(self, "Ошибка", "Пароли не совпадают")
            return
        
        # Хеширование пароля
        login = self.login_input.text()
        password = self.password_input.text()
        hashed_password = sha256(password.encode('utf-8')).hexdigest()

        with open("new_authenticate.txt", "w", encoding="utf-8") as f:
            f.write(f"{login}\n")
            f.write(hashed_password)
    
            
        # Показ сообщения об успешном сохранении
        os.system(f'scp new_authenticate.txt worker@192.168.1.13:/home/worker/')
        QMessageBox.information(self, "Успех", "Учетные данные успешно сохранены")
        
        # Закрытие диалогового окна
        self.accept()


class AuthApp(QMainWindow):
    def __init__(self):  # initialisation
        super().__init__()
        self.setWindowTitle("Программно-аппаратный шифратор")
        self.setMinimumSize(500, 400)

        self.ram = "/dev/shm/transfer/"
        self.orange_pi = "worker"
        self.orange_path = f"/home/{self.orange_pi}/"
        
        self.auth_file_question = "authenticate.txt"
        self.auth_file_new = "new_authenticate.txt"
        self.selected_action_file = "operation.txt"
        self.auth_file_answer = "responce.txt"
        self.list_files = "selected_files.txt"
        self.names_files = "files_to_crypt.txt"

        self.ip_server = "192.168.1.13"
        self.ip_my = "192.168.1.18"
        
        # Список для хранения путей к выбранным файлам
        self.selected_files = []
        
        # Инициализация интерфейса
        self.initUI()
        
    def initUI(self):     #create first field for auth
        # Создание основного виджета и вертикального layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(40, 40, 40, 40)
        
        # Создание формы аутентификации
        self.create_auth_form(main_layout)
    
    def create_auth_form(self, layout):     #create auth form
        # Очистка layout, если в нем есть элементы
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Заголовок формы
        title_label = QLabel("Вход в систему")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Создание формы для полей ввода
        form_layout = QFormLayout()
        form_layout.setContentsMargins(60, 30, 60, 30)
        form_layout.setSpacing(15)
        
        # Поле для имени пользователя
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Введите имя пользователя")
        form_layout.addRow("Имя пользователя:", self.username_edit)
        
        # Поле для пароля
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Введите пароль")
        self.password_edit.setEchoMode(QLineEdit.Password)
        form_layout.addRow("Пароль:", self.password_edit)
        
        layout.addLayout(form_layout)
        
        # Контейнер для кнопки входа
        button_layout = QHBoxLayout()
        
        # Кнопка входа
        login_button = QPushButton("Войти")
        login_button.setFixedSize(150, 40)
        login_button.clicked.connect(self.authenticate)
        button_layout.addWidget(login_button, alignment=Qt.AlignCenter)
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        # Установка фокуса на поле имени пользователя
        self.username_edit.setFocus()
        
        # Привязка клавиши Enter к аутентификации
        self.username_edit.returnPressed.connect(self.authenticate)
        self.password_edit.returnPressed.connect(self.authenticate)
        
    def delete_files(self):
        exit_files()
        self.close()

    def authenticate(self):      #correct auth (send to opi and receive)
        username = self.username_edit.text()
        password = self.password_edit.text()
        password_hash = sha256(password.encode('utf-8')).hexdigest()

        with open(self.auth_file_question, "w", encoding="utf-8") as f:
            f.write(f"{username}\n")
            f.write(password_hash)
        
        os.system(f'scp {self.auth_file_question} {self.orange_pi}@{self.ip_server}:{self.orange_path}')
        os.remove(f'{self.auth_file_question}')
        self.check_auth()
    
    def check_auth(self):
        file = wait_for_file(self.auth_file_answer)
        print('get checking answer')

        with open(file, 'r', encoding="utf-8") as f:
            answer = f.readline().strip()
            os.remove(file)
            
        if answer == "1":
            self.show_success_screen()
        else:
            QMessageBox.critical(self, "Ошибка аутентификации", "Неверное имя пользователя или пароль")
            exit_files()
            # Закрываем приложение при неверных данных
            self.close()

    def show_success_screen(self):       # create main page with selection
        # Очистка макета центрального виджета
        new_central_widget = QWidget()
        new_central_widget.setLayout(QVBoxLayout())
        self.setCentralWidget(new_central_widget)
        layout = self.centralWidget().layout()
        
        # Заголовок об успешной авторизации
        success_label = QLabel("Добро пожаловать!")
        success_font = QFont()
        success_font.setPointSize(16)
        success_font.setBold(True)
        success_label.setFont(success_font)
        success_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(success_label)
        
        # Группа радиокнопок для выбора режима
        mode_group = QButtonGroup()
        mode_layout = QHBoxLayout()

        # Радиокнопка "Расшифровать"
        decrypt_radio = QRadioButton("Расшифровать")
        decrypt_radio.setChecked(True)  # По умолчанию выбрано шифрование
        mode_group.addButton(decrypt_radio)
        mode_layout.addWidget(decrypt_radio)
        
        # Радиокнопка "Зашифровать"
        encrypt_radio = QRadioButton("Зашифровать")
        mode_group.addButton(encrypt_radio)
        mode_layout.addWidget(encrypt_radio)
        
        
        # Добавление layout с радиокнопками в основной layout
        layout.addLayout(mode_layout)
        layout.addSpacing(10)
        
        # Кнопка выбора файлов
        select_button = QPushButton("Выбрать файлы")
        select_button.setFixedSize(200, 40)
        select_button.clicked.connect(self.select_files)
        layout.addWidget(select_button, alignment=Qt.AlignCenter)
        layout.addSpacing(20)
        
        # Область для отображения выбранных файлов
        self.files_text = QTextEdit()
        self.files_text.setReadOnly(True)
        self.files_text.setPlaceholderText("Выбранные файлы появятся здесь")
        layout.addWidget(self.files_text)
        
        # Кнопка "Обработать"
        process_button = QPushButton("Обработать")
        process_button.setFixedSize(200, 40)
        process_button.clicked.connect(lambda: self.process_files(
            "Расшифровать" if decrypt_radio.isChecked() else "Зашифровать"
        ))
        layout.addWidget(process_button, alignment=Qt.AlignCenter)
        layout.addSpacing(10)
        
        # Кнопка выхода
        exit_button = QPushButton("Выход")
        exit_button.setFixedSize(150, 40)
        exit_button.clicked.connect(self.delete_files)
        layout.addWidget(exit_button, alignment=Qt.AlignCenter)
        
    def process_files(self, mode):       # Создание файла с названием режима
        try:
            with open(self.selected_action_file, "w", encoding="utf-8") as f:
                f.write(mode)
            self.send_files()

        except Exception as e:
            self.delete_files()
            QMessageBox.warning(self, "Ошибка", f"Не удалось подготовить файлы")
        
    def select_files(self):              #choose files
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Выберите файлы",
            "",
            "Все файлы (*);;Текстовые файлы (*.txt);;Документы (*.docx *.pdf);;Изображения (*.jpg *.png *.gif)"
        )
        
        if files:
            self.selected_files = files
            
            # Отображение выбранных файлов
            files_text = "Выбранные файлы:\n\n"
            for i, file_path in enumerate(self.selected_files):
                files_text += f"{i+1}. {file_path}\n"
            
            self.files_text.setText(files_text)
            
            # Сохранение путей в файл
            
    def send_files(self):                #send files to opi
        try:
            # Проверяем, есть ли выбранные файлы перед сохранением
            if not self.selected_files:
                QMessageBox.warning(self, "Предупреждение", "Нет выбранных файлов")
                return

            save_path = os.path.join(os.path.expanduser('~'), self.list_files)
            os.system(f"scp {self.selected_action_file} {self.orange_pi}@{self.ip_server}:{self.orange_path}") #отправляем файл с режимом сначала
            os.remove(f'{self.selected_action_file}')
            
            file_with_names = open(self.names_files, "w", encoding="utf-8")
            
            with open(save_path, "w", encoding="utf-8") as f:
                for file_path in self.selected_files:
                    if os.path.exists(file_path):
                        name = file_path.split("/")[-1]
                        f.write(f"{name} {file_path}\n")
                        file_with_names.write(f'{name}\n')
                
                file_with_names.close()
                os.system(f"scp {self.names_files} {self.orange_pi}@{self.ip_server}:{self.orange_path}")   #передаем files_to_crypt
                #os.remove(self.names_files)
                os.system(f"scp {self.list_files} {self.orange_pi}@{self.ip_server}:{self.orange_path}")
                #os.remove(f'{self.list_files}')

                for file_path in self.selected_files:
                    if os.path.exists(file_path):
                        os.system(f"scp {file_path} {self.orange_pi}@{self.ip_server}:{self.orange_path}")
                        os.remove(f'{file_path}')
                        print("send: ", file_path)
                    else:
                        print(f"Файл не найден: {file_path}")

            self.move_specific_files(self.ram, self.list_files)

        except Exception as e:
            QMessageBox.warning(self, "Предупреждение", f"Не удалось сохранить пути к файлам: {str(e)}")
            print(traceback.format_exc())
    
    def parse_file_mapping(self, file_path): #parsim fail name i path

        file_map = {}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    
                    if not line or line.startswith('#'):
                        continue
                    
                    if ' ' in line:
                        parts = line.split(' ', 1)
                        file_name = parts[0].strip()
                        file_path = parts[1].strip()
                    
                    else:
                        print(f"Не удалось распознать строку: {line}")
                        continue
                    
                    # Добавляем в словарь
                    file_map[file_name] = file_path
        
        except FileNotFoundError:
            QMessageBox.warning(self, "Предупреждение", f"Файл не найден: {file_path}")
        except Exception as e:
            QMessageBox.warning(self, "Предупреждение", f"Ошибка при чтении файла: {str(e)}")
        
        return file_map
    
    def move_specific_files(self, watch_directory, selected_files_path):
        ### os.system(f"python3 gather_files.py {self.list_files}")
        self.show_change_credentials_dialog()
    
    def show_change_credentials_dialog(self):
        dialog = ChangeCredentialsDialog()
        dialog.exec_()  # Модальный диалог
        self.close()


def main():
    app = QApplication(sys.argv)
    
    # Установка стиля приложения
    app.setStyle("Fusion")
    #os.mkdir("/dev/shm/transfer/", exist_ok=True)
    
    # Создание и отображение окна приложения
    window = AuthApp()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

