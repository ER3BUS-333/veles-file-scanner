from pathlib import Path

Skip_Dirs = {".git", ".venv", "__pycache__", "node_modules"}

def iter_files(path: Path):
    try:
        for item in path.iterdir():
            if item.is_file():
                yield item
            elif item.is_dir():
                if item.name in Skip_Dirs:
                    continue
                yield from iter_files(item)

    except PermissionError:
        return
