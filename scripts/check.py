from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
html = (root / "index.html").read_text(encoding="utf-8")

refs = re.findall(r'(?:src|href)=["\']([^"\']+)', html)
missing = [
    ref for ref in refs
    if not ref.startswith(("http", "#", "tel:", "mailto:", "data:"))
    and not (root / ref).exists()
]

class IDs(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key == "id":
                self.ids.append(value)

parser = IDs()
parser.feed(html)
duplicates = [key for key, count in Counter(parser.ids).items() if count > 1]

print(f"Ссылок проверено: {len(refs)}")
print(f"Отсутствуют файлы: {missing or 'нет'}")
print(f"Повторяющиеся id: {duplicates or 'нет'}")
