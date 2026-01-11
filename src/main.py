from pathlib import Path 
from scanner import scan_dir

def main():
    
    print("Veles запущен")
    user_inpt = input("Введите путь к папке с файлами:  ")
    print("Вы ввели: ",user_inpt)

    p = Path(user_inpt)
    if not p.exists():
        print("Ошибка!: путь не существует")
        return
    if not p.is_dir():
        print("Ошибка!: это не папка")
        return
    
    print("Всё ок папка существует и это папка")
    
    print("Файлы в папке: ")

    print("сканер")
    for item in p.iterdir():
        if item.is_file():
            print(item)
        

    scan_dir(p)


if __name__ == "__main__":
    main()