#!/bin/python3

import os
import sys
import traceback
import time
import watchdog.observers
import watchdog.events
from hashlib import sha256
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                            QMessageBox, QFileDialog, QTextEdit, QFormLayout)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon

class AuthApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Система аутентификации")
        self.setMinimumSize(500, 400)
        
        # Корректные учетные данные (в реальном приложении используйте безопасное хранение)
        self.correct_username = "admin"
        self.correct_password = "password123"

        self.ip_server = "192.168.1.30"
        self.ip_my = "192.168.1.20"
        
        # Список для хранения путей к выбранным файлам
        self.selected_files = []
        
        # Инициализация интерфейса
        self.initUI()
        
    def initUI(self):
        # Создание основного виджета и вертикального layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(40, 40, 40, 40)
        
        # Создание формы аутентификации
        self.create_auth_form(main_layout)
        
    def create_auth_form(self, layout):
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
    
    def start_watching(self):
        """
        Запуск наблюдения за директорией
        """
        class Handler(watchdog.events.FileSystemEventHandler):
            def __init__(self, checker):
                self.checker = checker
            
            def on_created(self, event):
                if not event.is_directory:
                    print(f"Обнаружен новый файл: {event.src_path}")
                    time.sleep(1)  # Небольшая задержка для полной записи файла
                    self.checker.process_file(event.src_path)
        
        # Создаем обработчик событий
        event_handler = Handler(self)
        
        # Создаем наблюдателя
        observer = watchdog.observers.Observer()
        observer.schedule(event_handler, self.watch_directory, recursive=False)
        # Запускаем наблюдение
        observer.start()
        
        try:
            print(f"Наблюдение за директорией {self.watch_directory}...")
            print("Ожидание файлов...")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        
        observer.join()

    def authenticate(self):
        username = self.username_edit.text()
        password = self.password_edit.text()
        password_hash = sha256(password.encode('utf-8')).hexdigest()

        with open("authenticate.txt", "w", encoding="utf-8") as f:
            f.write(f"{username}\n")
            f.write(password_hash)
        
        os.system(f'scp authenticate.txt user@{self.ip_server}:/target/path/')
        self.start_watching()

        with open("response.txt", 'r', encoding="utf-8") as f:
            answer = f.readline().strip()
            os.system(f"rm {f}")
            
        if answer == "1":
            self.show_success_screen()
        else:
            QMessageBox.critical(self, "Ошибка аутентификации", 
                                "Неверное имя пользователя или пароль")
            # Закрываем приложение при неверных данных
            self.close()

    
    def show_success_screen(self):
        # Очистка макета центрального виджета
        new_central_widget = QWidget()
        new_central_widget.setLayout(QVBoxLayout())
        self.setCentralWidget(new_central_widget)
        layout = self.centralWidget().layout()
        '''
        layout = self.centralWidget().layout()
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        '''
        # Заголовок об успешной авторизации
        success_label = QLabel("Успешная авторизация")
        success_font = QFont()

        
        success_font.setPointSize(16)
        success_font.setBold(True)
        success_label.setFont(success_font)
        success_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(success_label)
        
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
        
        # Кнопка выхода
        exit_button = QPushButton("Выход")
        exit_button.setFixedSize(150, 40)
        exit_button.clicked.connect(self.close)
        layout.addWidget(exit_button, alignment=Qt.AlignCenter)
        
    def select_files(self):
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
            self.save_file_paths()
    
    def save_file_paths(self):
        try:
            # Проверяем, есть ли выбранные файлы перед сохранением
            if not self.selected_files:
                QMessageBox.warning(self, "Предупреждение", "Нет выбранных файлов для сохранения")
                return

            # Используем абсолютный путь для надежности
            save_path = os.path.join(os.path.expanduser('~'), 'selected_files.txt')
            
            with open(save_path, "w", encoding="utf-8") as f:
                for file_path in self.selected_files:
                    # Проверяем существование файла перед записью
                    if os.path.exists(file_path):
                        os.system(f"scp {file_path.split("/")[-1]} user@{self.ip_server}:/target/path/{file_path}")
                        f.write(f"{file_path}\n")
                    else:
                        print(f"Файл не найден: {file_path}")
            
            QMessageBox.information(self, "Информация", 
                                f"Пути к файлам сохранены в {save_path}")

        
        except Exception as e:
            QMessageBox.warning(self, "Предупреждение", f"Не удалось сохранить пути к файлам: {str(e)}")
            # Логирование ошибки для отладки
            print(traceback.format_exc())

def main():
    app = QApplication(sys.argv)
    
    # Установка стиля приложения
    app.setStyle("Fusion")
    
    # Создание и отображение окна приложения
    window = AuthApp()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

    
'''
import tkinter as tk
from tkinter import messagebox, filedialog

class AuthApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Система аутентификации")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        # Корректные учетные данные (в реальном приложении используйте безопасное хранение)
        self.correct_username = "admin"
        self.correct_password = "password123"
        
        # Создание формы аутентификации
        self.create_auth_form()
        
        # Переменная для хранения путей к выбранным файлам
        self.selected_files = []

    def create_auth_form(self):
        # Очистка окна
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Создание фрейма для формы
        auth_frame = tk.Frame(self.root, padx=20, pady=20)
        auth_frame.pack(expand=True)
        
        # Заголовок
        tk.Label(auth_frame, text="Вход в систему", font=("Arial", 16, "bold")).grid(
            row=0, column=0, columnspan=2, pady=(0, 20)
        )
        
        # Поле для имени пользователя
        tk.Label(auth_frame, text="Имя пользователя:").grid(
            row=1, column=0, sticky="w", pady=(0, 10)
        )
        self.username_entry = tk.Entry(auth_frame, width=25)
        self.username_entry.grid(row=1, column=1, pady=(0, 10))
        
        # Поле для пароля
        tk.Label(auth_frame, text="Пароль:").grid(
            row=2, column=0, sticky="w", pady=(0, 20)
        )
        self.password_entry = tk.Entry(auth_frame, width=25, show="*")
        self.password_entry.grid(row=2, column=1, pady=(0, 20))
        
        # Кнопка входа
        login_button = tk.Button(
            auth_frame, text="Войти", command=self.authenticate, width=10
        )
        login_button.grid(row=3, column=0, columnspan=2)
        
        # Привязка клавиши Enter к функции аутентификации
        self.root.bind('<Return>', lambda event: self.authenticate())

    def authenticate(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if username == self.correct_username and password == self.correct_password:
            # Очистка окна
            for widget in self.root.winfo_children():
                widget.destroy()
                
            # Создание экрана успешной авторизации
            success_frame = tk.Frame(self.root, padx=20, pady=20)
            success_frame.pack(expand=True)
            
            # Сообщение об успешной авторизации
            tk.Label(
                success_frame, 
                text="Успешная авторизация", 
                font=("Arial", 16, "bold")
            ).pack(pady=(0, 20))
            
            # Кнопка выбора файлов
            select_button = tk.Button(
                success_frame, 
                text="Выбрать файлы", 
                command=self.select_files,
                width=15
            )
            select_button.pack(pady=10)
            
            # Область для отображения выбранных файлов
            self.files_label = tk.Label(
                success_frame, 
                text="Выбранные файлы появятся здесь",
                wraplength=350,
                justify="left"
            )
            self.files_label.pack(pady=10, fill="both")
            
            # Кнопка выхода
            exit_button = tk.Button(
                success_frame, 
                text="Выход", 
                command=self.root.destroy,
                width=15
            )
            exit_button.pack(pady=10)
        else:
            messagebox.showerror("Ошибка", "Неверное имя пользователя или пароль")
            self.root.destroy()  # Закрытие программы при неверных данных

    def select_files(self):
        files = filedialog.askopenfilenames(
            title="Выберите файлы",
            filetypes=[
                ("Все файлы", "*.*"),
                ("Текстовые файлы", "*.txt"),
                ("Документы", "*.docx;*.pdf"),
                ("Изображения", "*.jpg;*.png;*.gif")
            ]
        )
        
        if files:  # Если файлы были выбраны
            self.selected_files = list(files)
            
            # Отображение первых нескольких файлов
            display_text = "Выбранные файлы:\n"
            for i, file in enumerate(self.selected_files[:3]):
                display_text += f"{i+1}. {file}\n"
                
            if len(self.selected_files) > 3:
                display_text += f"...и еще {len(self.selected_files) - 3} файл(ов)"
                
            self.files_label.config(text=display_text)
            
            # Сохранение путей в файл (опционально)
            self.save_file_paths()

    def save_file_paths(self):
        try:
            with open("selected_files.txt", "w", encoding="utf-8") as f:
                for file_path in self.selected_files:
                    f.write(f"{file_path}\n")
            messagebox.showinfo("Информация", "Пути к файлам сохранены в selected_files.txt")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить пути: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AuthApp(root)
    root.mainloop()
'''