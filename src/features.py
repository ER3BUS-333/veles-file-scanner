from pathlib import Path

Rules = {".exe":30, ".dll":25, ".ps1":25, ".bat":15, ".cmd":20, ".vbs":22, ".js":25, ".scr":25, ".hta":25 }
def score_file(path: Path):
    score = 0
    ext = path.suffix.lower()
    if  ext in Rules:
        score = score + Rules[ext]

    return score

