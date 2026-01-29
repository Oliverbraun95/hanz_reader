import pathlib

DATA_DIR = pathlib.Path(__file__).parent.parent / "app" / "data" / "hsk_levels"

def add_headers():
    for level in range(1, 7):
        file_path = DATA_DIR / f"hsk{level}.csv"
        if file_path.exists():
            content = file_path.read_text(encoding="utf-8")
            if not content.startswith("word,pinyin,meaning"):
                print(f"Adding header to {file_path}")
                new_content = "word,pinyin,meaning\n" + content
                file_path.write_text(new_content, encoding="utf-8")
            else:
                print(f"Header already exists in {file_path}")

if __name__ == "__main__":
    add_headers()
