from pathlib import Path
Bait_exts = {".pdf" , ".doc", ".docx", 
             ".xls", ".xlsx", ".pptx", 
             ".jpg", ".png", ".txt", 
             ".zip", ".rar"}
Rules = {".exe":30, ".dll":25, ".ps1":25, 
         ".bat":15, ".cmd":20, ".vbs":22, 
         ".js":25, ".scr":25, ".hta":25 }
Path_rules = {
    "\\appdata\\local\\temp\\": 30,
    "\\appdata\\roaming\\": 25,
    "\\programdata\\": 20,
}

Archive_exts = {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz"}

Archive_rules = {
    ".zip": 8,
    ".rar": 10,
    ".7z": 10,
    ".tar": 6,
    ".gz": 6,
    ".bz2": 6,
    ".xz": 6,
}

def is_double_exts(path: Path):
    name = path.name.lower()
    parts = name.split(".")
    if len(parts) < 3:
        return None
    last = "." + parts[-1]
    prev = "." + parts[-2]

    if last in Rules and prev in Bait_exts:
        return prev, last

    return None

def get_motw_zone(path: Path):
    ads_path = str(path) + ":Zone.Identifier"
    try:
        with open(ads_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except (FileNotFoundError, PermissionError):
        return None

    for line in content.splitlines():
        if line.startswith("ZoneId="):
            try:
                return int(line.split("=", 1)[1])
            except ValueError:
                return None

    return None

    
       
def score_file(path: Path):
    score = 0
    reasons = []
    ext = path.suffix.lower()
    zone = get_motw_zone(path)

    if ext in Archive_exts:
        pts = Archive_rules.get(ext, 6)
        score += pts
        reasons.append(f"АРХИВ: {ext} (+{pts})")


    if zone == 3:
        motw_pts = 35 if ext in Rules else 15
        score += motw_pts
        reasons.append(f"MOTW = 3 ({'инет + опасное расширение' if ext in Rules else 'файл из интернета'}) (+{motw_pts})")

    elif zone == 4:
        motw_pts = 45 if ext in Rules else 30
        score += motw_pts
        reasons.append(f"MOTW = 4 ({'подозрительный + опасное расширение' if ext in Rules else 'подозрительный источник'}) (+{motw_pts})")

    if  ext in Rules:
        score = score + Rules[ext]
        reasons.append(f"Расширение: {ext} (+{Rules[ext]})")
    info = is_double_exts(path)
    if info:
        prev, last = info
        score = score + 40
        reasons.append(f"ДВОЙНОЕ РАСШИРЕНИЕ! ФЕЙК {prev} -> РЕАЛЬНОЕ {last} (+40)")
    path_str = str(path).lower()

    for risky_path, points in Path_rules.items():
        if risky_path in path_str:
            score += points
            reasons.append(f"Опасное расположение: {risky_path} (+{points})")


    return score, reasons


