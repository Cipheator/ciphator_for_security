import os
import time
import hashlib

def wait_for_file(filename: str, directory: str = '/home/worker/', timeout: int = 3600, check_interval: float = 1.0):

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

class LoginHashChecker:
    def __init__(self, watch_directory, results_directory):
        self.watch_directory = watch_directory
        self.results_directory = results_directory
        
        self.ram = "/dev/shm/transfer/"

        self.orange_pi = "worker"
        self.orange_path = f"/home/{self.orange_pi}/"

        self.pc_name = "client"
        self.pc_path = f"/home/{self.pc_name}/"
        
        self.auth_file_question = "authenticate.txt"
        self.auth_file_new = "new_authenticate.txt"
        self.selected_action_file = "operation.txt"
        self.auth_file_answer = "responce.txt"
        self.list_files = "selected_files.txt"

        self.ip_server = "192.168.1.2"
        self.ip_my = "192.168.1.3"


        # Создаем директории, если они не существуют
        os.makedirs(watch_directory, exist_ok=True)
        os.makedirs(results_directory, exist_ok=True)

        with open("new_authenticate.txt", 'r', encoding="utf-8") as f:
            self.login = f.readline().strip()
            self.password = f.readline().strip()
        #######os.remove("new_authenticate.txt")
        
        '''
        self.known_credentials = {
            'admin': '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8',  # пароль: password
            'user1': '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92',  # пароль: 123456
            # Добавьте другие логины и их хэши по необходимости
        }'
        '''
    
    
    def check_credentials(self, login, password_hash):
        if login == self.login:
            return self.password == password_hash
        return False
    
    def process_file(self, file_path):  #check auth
        try:
            '''
            if wait_for_file(self.auth_file_answer):
                with open(file_path, 'r', encoding='utf-8') as f:
                    login = f.readline().strip()
                    password_hash = f.readline().strip()

                is_valid = self.check_credentials(login, password_hash)
                result_message = f"{'1' if is_valid else '0'}"
                self.save_result(result_message)
            '''
            with open(file_path, 'r', encoding='utf-8') as f:
                login = f.readline().strip()
                password_hash = f.readline().strip()

            is_valid = self.check_credentials(login, password_hash)
            result_message = f"{'1' if is_valid else '0'}"
            self.save_result(result_message)
        
        except Exception as e:
            print(f"Ошибка обработки: {str(e)}")
    
    def save_result(self, result_message):   #save auth
        result_filename = self.auth_file_answer
        result_path = os.path.join(self.results_directory, result_filename)
        
        with open(result_path, 'w', encoding='utf-8') as f:
            f.write(result_message)
        
        print(f"Результат сохранен в {result_path}")
        
        os.system(f'scp {self.auth_file_answer} {self.pc_name}@{self.ip_my}:{self.pc_path}')
        self.performance()
    
    def parse_file_mapping(self, file_path): #parsim fail name i path

        file_map = {}
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
        return file_map

    def performance(self):
        #if wait_for_file(self.selected_action_file):
        #    list_files = wait_for_file(self.list_files)
        list_files = self.list_files

        os.system(f"python3 cipher.py {list_files}")

        with open(list_files, 'r') as f:
            for line in f:
                file_name, dest_path = line.strip().split()
                os.system(f"scp {file_name} {self.pc_name}@{self.ip_my}:{self.pc_path}")
                os.remove(file_name)

        self.new_cred()

    def new_cred(self):
        #### file = wait_for_file(self.auth_file_new)
        os.remove(self.auth_file_question)
    

def main():
    # Настройки директорий
    WATCH_DIR = './'  # Директория для входящих файлов
    RESULTS_DIR = './'  # Директория для результатов
    
    # Создаем экземпляр класса и запускаем наблюдение
    checker = LoginHashChecker(WATCH_DIR, RESULTS_DIR)
    print('now step - wait for auth.txt')
    checker.process_file("authenticate.txt")

if __name__ == "__main__":
    main()
