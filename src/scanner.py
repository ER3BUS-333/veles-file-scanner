from pathlib import Path
Skip_Dirs = {".git", ".venv", "__pycache__", "node_modules"}
def scan_dir(path: Path):
    for item in path.iterdir():
        if item.is_file():
            print(item)
        elif item.is_dir():
            if item.name in Skip_Dirs:
                continue                
              
            scan_dir(item)
