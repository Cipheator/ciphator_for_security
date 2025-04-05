import os
import time
import subprocess
import shutil

class FileEncryptionMonitor:
    def __init__(self, files_list_path, encryption_executable):
        """
        Инициализация монитора файлов для шифрования
        
        :param files_list_path: Путь к файлу со списком файлов для шифрования
        :param encryption_executable: Путь к ELF-файлу шифрования
        """
        # Читаем список файлов
        with open(files_list_path, 'r') as f:
            self.files_to_encrypt = [line.strip() for line in f.readlines()]
        
        # Путь к исполняемому файлу шифрования
        self.encryption_executable = encryption_executable
        
        # Множество для отслеживания обработанных файлов
        self.processed_files = set()

    def encrypt_file(self, filename):
        # Создаем имена для зашифрованного файла и ключа
        encrypted_filename = f"{filename}.enc"
        key_filename = f"{filename}.bin"
        
        try:
            # Выполняем внешний ELF-файл шифрования
            result = subprocess.run([
                self.encryption_executable, 
                filename,       # Исходный файл 
                encrypted_filename,  # Зашифрованный файл
                key_filename    # Файл ключа
            ], capture_output=True, text=True)
            
            # Проверяем успешность выполнения
            if result.returncode == 0:
                # Удаляем исходный файл
                os.remove(filename)
                ############################# os.system(f"scp {filename}.enc client@192.168.1.3:/home/client")
                print(f"Файл {filename} успешно зашифрован. Создан {encrypted_filename} и {key_filename}")
                return encrypted_filename, key_filename
            else:
                print(f"Ошибка шифрования файла {filename}:")
                print(result.stderr)
                return None, None
        
        except Exception as e:
            print(f"Исключение при шифровании файла {filename}: {e}")
            return None, None

    def wait_and_encrypt_files(self):
        """
        Ожидание и шифрование файлов из списка
        """
        print("Ожидание файлов для шифрования...")
        cnt = 0
        while cnt < len(self.files_to_encrypt):
            for filename in self.files_to_encrypt:
                ## print("ciphyem", filename, self.processed_files, self.files_to_encrypt)
                ## print ("####", filename not in self.processed_files, os.path.exists(filename))
                if filename not in self.processed_files and os.path.exists(filename):
                    # Шифруем файл
                    cnt += 1
                    encrypted_file, key_file = self.encrypt_file(filename)
                    print(encrypted_file, key_file)
                    
                    # Если шифрование прошло успешно
                    if encrypted_file and key_file:
                        os.system(f"scp -i /home/worker/.ssh/id_rsa {filename}.enc client@192.168.1.31:/home/client")
                        os.remove(f"{filename}.enc")
                        self.processed_files.add(filename)
            
            # Небольшая пауза для снижения нагрузки на процессор
            time.sleep(1)
        
        print("Все файлы успешно зашифрованы.")

def main():
    # Путь к файлу со списком файлов
    FILES_LIST_PATH = 'files_to_crypt.txt'
    
    # Путь к ELF-файлу шифрования 
    ENCRYPTION_EXECUTABLE = './encoder'  # Замените на реальный путь к вашему ELF-файлу
    
    # Создаем экземпляр класса FileEncryptionMonitor
    encryptor = FileEncryptionMonitor(FILES_LIST_PATH, ENCRYPTION_EXECUTABLE)
    
    # Запускаем процесс ожидания и шифрования
    encryptor.wait_and_encrypt_files()

if __name__ == "__main__":
    main()
