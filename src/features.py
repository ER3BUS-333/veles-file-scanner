from pathlib import Path
Bait_exts = {".pdf" , ".doc", ".docx", ".xls", ".xlsx", ".pptx", ".jpg", ".png", ".txt", ".zip", ".rar"}
Rules = {".exe":30, ".dll":25, ".ps1":25, ".bat":15, ".cmd":20, ".vbs":22, ".js":25, ".scr":25, ".hta":25 }

def is_double_exts(path: Path):
    name = path.name.lower()
    parts = name.split(".")
    if len(parts) < 3:
        return False
    last = "." + parts[-1]
    prev = "." + parts[-2]

    if last in Rules and prev in Bait_exts:
        return True

    return False

       
def score_file(path: Path):
    score = 0
    ext = path.suffix.lower()
    if  ext in Rules:
        score = score + Rules[ext]
    if is_double_exts(path):
        score = score + 40

    return score


