#!/usr/bin/env python3
import os
import time
import shutil
import argparse

def wait_for_files(transfer_dir, mapping_file, timeout=3600):

    # Чтение маппинга файлов
    file_mapping = {}
    with open(mapping_file, 'r') as f:
        for line in f:
            file_name, dest_path = line.strip().split()
            file_mapping[file_name] = dest_path
    
    start_time = time.time()
    
    while file_mapping:
        # Проверка оставшегося времени
        if time.time() - start_time > timeout:
            raise TimeoutError(f"Не все файлы появились в течение {timeout} секунд. Оставшиеся файлы: {list(file_mapping.keys())}")
        
        # Список файлов в директории трансфера
        current_files = set(os.listdir(transfer_dir))
        
        # Поиск и удаление найденных файлов из маппинга
        for file_name in list(file_mapping.keys()):
            if file_name in current_files:
                del file_mapping[file_name]
        
        # Если все файлы найдены, выходим из цикла
        if not file_mapping:
            break
        
        # Небольшая пауза между проверками
        time.sleep(1)
    
    return file_mapping

def transfer_files(transfer_dir, mapping_file):
    try:
        # Ожидаем появления всех файлов
        wait_for_files(transfer_dir, mapping_file)
        
        # Чтение маппинга файлов
        with open("operation_mode.txt") as mod:
            for l in line:
                opmod = l.strip()
                if opmod == "Зашифровать":
                    gost_file = "encoder"
                else:
                    gost_file = "decoder"
        
        with open(mapping_file, 'r') as f:
            for line in f:
                file_name, dest_path = line.strip().split()
                
                # Полные пути к исходному и целевому файлам
                # src_path = os.path.join(transfer_dir, file_name)
                
                # Создаем директории, если они не существуют
                if gost_file == "decoder":
                    os.system(f'./{gost_file} {file_name} key.bin')
                else:  
                    os.system(f"./{gost_file} {file_name}")
                
                # Перемещаем файл
                # shutil.move(src_path, dest_path)
                print(f"Файл {file_name} преобразован {gost_file}")
        
        print("Все файлы успешно!")
    
    except TimeoutError as e:
        print(f"Ошибка: {e}")
    except Exception as e:
        print(f"Произошла непредвиденная ошибка: {e}")

def main():
    parser = argparse.ArgumentParser(description='Скрипт для ожидания и перемещения файлов')
    parser.add_argument('mapping_file', help='Путь к файлу с маппингом файлов')
    
    args = parser.parse_args()
    
    transfer_files("/home/worker/", args.mapping_file)

if __name__ == '__main__':
    main()