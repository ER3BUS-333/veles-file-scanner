
from __future__ import annotations

import json
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from scanner import iter_files
from features import score_file


VELES_A = r"""
   \\          //
    \\        //
     \\======//
      \\    //
       \\  //
        \\//  
"""


@dataclass
class ScanResult:
    path: str
    score: int
    reasons: list[str]

    def to_dict(self) -> dict:
        return {"path": self.path, "score": self.score, "reasons": self.reasons}


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def veles_intro() -> None:
    clear_screen()
    print("VELES запускается", end="", flush=True)
    for _ in range(6):
        time.sleep(0.25)
        print(".", end="", flush=True)
    time.sleep(0.25)

    clear_screen()
    for line in VELES_A.splitlines():
        print(line)
        time.sleep(0.05)

    print("\nVELES ON THE Line\n")
    time.sleep(0.35)


def windows_known_folders() -> dict[str, Path]:
    """
    Возвращает основные папки Windows, если мы на Windows.
    На других ОС отдаёт только домашнюю папку.
    """
    home = Path.home()

    if os.name != "nt":
        return {
            "HOME": home,
        }

    userprofile = Path(os.environ.get("USERPROFILE", str(home)))
    windir = Path(os.environ.get("WINDIR", r"C:\Windows"))

    return {
        "DESKTOP": userprofile / "Desktop",
        "DOWNLOADS": userprofile / "Downloads",
        "DOCUMENTS": userprofile / "Documents",
        "TEMP": userprofile / r"AppData\Local\Temp",
        "PROGRAM_FILES": Path(os.environ.get("ProgramFiles", r"C:\Program Files")),
        "PROGRAM_FILES_X86": Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")),
        "HOME": home,
        "WINDIR": windir,
    }


def pick_scan_root() -> Path | None:
    folders = windows_known_folders()

    while True:
        print("Выберите что сканировать:")
        print(" 1) Рабочий стол")
        print(" 2) Загрузки")
        print(" 3) Документы")
        print(" 4) Temp (AppData\\Local\\Temp)")
        print(" 5) Program Files")
        print(" 6) Program Files (x86)")
        print(" 7) Ввести свой путь")
        print(" 0) Выход")

        choice = input("\n> ").strip()

        mapping = {
            "1": folders.get("DESKTOP"),
            "2": folders.get("DOWNLOADS"),
            "3": folders.get("DOCUMENTS"),
            "4": folders.get("TEMP"),
            "5": folders.get("PROGRAM_FILES"),
            "6": folders.get("PROGRAM_FILES_X86"),
        }

        if choice == "0":
            return None

        if choice in mapping:
            p = mapping[choice]
            if p and p.exists() and p.is_dir():
                print(f"\nОк, сканируем: {p}\n")
                return p
            print("\nОшибка: папка недоступна/не существует.\n")
            continue

        if choice == "7":
            user_inpt = input("Введите путь к папке:\n> ").strip().strip('"')
            if not user_inpt:
                print("\nОшибка: путь пустой.\n")
                continue

            p = Path(user_inpt)
            if not p.exists():
                print("\nОшибка: путь не существует.\n")
                continue
            if not p.is_dir():
                print("\nОшибка: это не папка.\n")
                continue

            print(f"\nОк, сканируем: {p}\n")
            return p

        print("\nНе понял выбор. Введите цифру из меню.\n")


def ensure_reports_dir(base: Path) -> Path:
    reports_dir = base / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    return reports_dir


def build_report_name(scan_root: Path) -> str:
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    safe_root = str(scan_root).replace("\\", "_").replace(":", "")
   
    safe_root = safe_root[-60:]
    return f"veles_report_{ts}_{safe_root}.json"


def save_json_report(reports_dir: Path, report_name: str, payload: dict) -> Path:
    out_path = reports_dir / report_name
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return out_path


def print_results_table(results: list[ScanResult], limit: int | None = None) -> None:
    if not results:
        print("Подозрительных файлов не найдено (по текущему порогу).")
        return

    if limit is not None:
        results = results[:limit]

    for r in results:
        print(f"{r.score} {r.path}")
        for reason in r.reasons:
            print(f"  - {reason}")
        print()


def main() -> None:
    veles_intro()

    scan_root = pick_scan_root()
    if scan_root is None:
        input("\nНажмите Enter для выхода...")
        return

    # настройки (можешь менять)
    THRESHOLD = 30  # печатаем/пишем в отчет только если score > THRESHOLD
    TOP_LIMIT = None  # например 50, если хочешь выводить только топ-50

    print("Файлы в папке:")
    print("сканер\n")

    results: list[ScanResult] = []
    scanned = 0
    shown = 0

    for item in iter_files(scan_root):
        scanned += 1
        score, reasons = score_file(item)

        if score > THRESHOLD:
            shown += 1
            results.append(ScanResult(path=str(item), score=score, reasons=reasons))

    # сортировка: сначала по score (убывание), потом по пути (для стабильности)
    results.sort(key=lambda x: (-x.score, x.path.lower()))

    # печать
    print_results_table(results, limit=TOP_LIMIT)

    # JSON отчёт
    reports_dir = ensure_reports_dir(Path.cwd())
    report_name = build_report_name(scan_root)

    payload = {
        "tool": "Veles",
        "version": "v0.3",
        "scanned_root": str(scan_root),
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "threshold": THRESHOLD,
        "stats": {
            "files_scanned": scanned,
            "suspicious_found": shown,
        },
        "results": [r.to_dict() for r in results],
    }

    out_path = save_json_report(reports_dir, report_name, payload)

    print("Готово.")
    print(f"Просканировано файлов: {scanned}")
    print(f"Подозрительных (>{THRESHOLD}): {shown}")
    print(f"JSON отчёт сохранён: {out_path}")

    # чтобы .exe не закрывался сразу
    input("\nНажмите Enter для выхода...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nОстановлено пользователем.")
        input("Нажмите Enter для выхода...")
        sys.exit(1)
    except Exception as e:
        print("\nКритическая ошибка:", repr(e))
        input("Нажмите Enter для выхода...")
        sys.exit(2)
