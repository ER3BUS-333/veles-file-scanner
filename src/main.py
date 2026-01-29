from pathlib import Path 
from scanner import iter_files
from features import score_file
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
    for item in iter_files(p):
        score = score_file(item)
        if score > 0:
            print(score, item)
        

    iter_files(p)


if __name__ == "__main__":
    main()