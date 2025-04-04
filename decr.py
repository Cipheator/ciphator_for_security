import os
import time
import subprocess

class FileDecryptionMonitor:
    def __init__(self, encrypted_files_list_path, decryption_executable):

        # Читаем список зашифрованных файлов
        with open(encrypted_files_list_path, 'r') as f:
            self.files_to_decrypt = [line.strip() for line in f.readlines()]
        
        # Путь к исполняемому файлу расшифрования
        self.decryption_executable = decryption_executable
        
        # Множество для отслеживания обработанных файлов
        self.processed_files = set()

    def decrypt_file(self, encrypted_filename):

        # Формируем имя файла ключа
        key_filename = f"{encrypted_filename.replace('.enc', '')}.bin"
        
        # Формируем имя расшифрованного файла (убираем .enc)
        decrypted_filename = encrypted_filename.replace('.enc', '')
        
        try:
            # Выполняем внешний ELF-файл расшифрования
            result = subprocess.run([
                self.decryption_executable, 
                encrypted_filename,    # Зашифрованный файл
                decrypted_filename,    # Файл после расшифрования 
                key_filename           # Файл ключа
            ], capture_output=True, text=True)
            
            # Проверяем успешность выполнения
            if result.returncode == 0:
                # Удаляем зашифрованный файл и файл ключа
                os.remove(encrypted_filename)
                os.remove(key_filename)
                
                print(f"Файл {encrypted_filename} успешно расшифрован в {decrypted_filename}")
                return decrypted_filename
            else:
                print(f"Ошибка расшифрования файла {encrypted_filename}:")
                print(result.stderr)
                return None
        
        except Exception as e:
            print(f"Исключение при расшифровании файла {encrypted_filename}: {e}")
            return None

    def wait_and_decrypt_files(self):
        """
        Ожидание и расшифрование файлов из списка
        """
        print("Ожидание файлов для расшифрования...")
        
        while len(self.processed_files) < len(self.files_to_decrypt):
            for encrypted_filename in self.files_to_decrypt:
                # Проверяем наличие зашифрованного файла и файла ключа
                key_filename = f"{encrypted_filename.replace('.enc', '')}.bin"
                
                if (encrypted_filename not in self.processed_files and 
                    os.path.exists(encrypted_filename) and 
                    os.path.exists(key_filename)):
                    
                    # Расшифруем файл
                    decrypted_file = self.decrypt_file(encrypted_filename)
                    
                    # Если расшифрование прошло успешно
                    if decrypted_file:
                        ########### os.system(f"scp {encrypted_filename.replace('.enc', '')} client@192.168.1.3:/dev/shm/transfer/")
                        self.processed_files.add(encrypted_filename)
            
            # Небольшая пауза для снижения нагрузки на процессор
            time.sleep(1)
        
        print("Все файлы успешно расшифрованы.")

def main():
    # Путь к файлу со списком зашифрованных файлов
    ENCRYPTED_FILES_LIST_PATH = 'files_to_crypt.txt'
    
    # Путь к ELF-файлу расшифрования 
    DECRYPTION_EXECUTABLE = './gost_decrypter'  # Замените на реальный путь к вашему ELF-файлу
    
    # Создаем экземпляр класса FileDecryptionMonitor
    decryptor = FileDecryptionMonitor(ENCRYPTED_FILES_LIST_PATH, DECRYPTION_EXECUTABLE)
    
    # Запускаем процесс ожидания и расшифрования
    decryptor.wait_and_decrypt_files()

if __name__ == "__main__":
    main()
