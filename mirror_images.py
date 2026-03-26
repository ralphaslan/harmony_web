import hashlib
import re
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent
HTML_FILES = sorted(ROOT.glob("*.html"))
ASSET_DIR = ROOT / "assets" / "mirror"
ASSET_DIR.mkdir(parents=True, exist_ok=True)

URL_PATTERN = re.compile(r"https?://[^\s\"'<>())]+", re.IGNORECASE)
IMAGE_HINT_PATTERN = re.compile(r"\.(?:png|jpe?g|webp|gif|svg|avif)(?:$|[/?#])", re.IGNORECASE)
EXT_PATTERN = re.compile(r"\.(png|jpe?g|webp|gif|svg|avif)(?:$|[/?#])", re.IGNORECASE)


def is_image_like(url: str) -> bool:
    lower = url.lower()
    if IMAGE_HINT_PATTERN.search(lower):
        return True
    return "/media/" in lower and ("wixstatic.com" in lower or "harmonydesign.me" in lower)


def local_name(url: str) -> str:
    ext_match = EXT_PATTERN.search(url)
    ext = f".{ext_match.group(1).lower()}" if ext_match else ".bin"
    digest = hashlib.sha1(url.encode("utf-8")).hexdigest()
    return f"{digest}{ext}"


def download(url: str, out_path: Path) -> bool:
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urlopen(req, timeout=20) as response:
            data = response.read()
        out_path.write_bytes(data)
        return True
    except Exception:
        return False


all_urls = set()
for html_file in HTML_FILES:
    text = html_file.read_text(encoding="utf-8", errors="ignore")
    for raw in URL_PATTERN.findall(text):
        url = raw.rstrip('.,;"\'')
        if is_image_like(url):
            all_urls.add(url)

url_to_local = {}
for url in sorted(all_urls):
    filename = local_name(url)
    out_path = ASSET_DIR / filename
    if not out_path.exists():
        ok = download(url, out_path)
        if not ok:
            continue
    url_to_local[url] = f"assets/mirror/{filename}"

for html_file in HTML_FILES:
    text = html_file.read_text(encoding="utf-8", errors="ignore")
    original = text
    for remote, local in url_to_local.items():
        if remote in text:
            text = text.replace(remote, local)
    if text != original:
        html_file.write_text(text, encoding="utf-8")

print(f"HTML files scanned: {len(HTML_FILES)}")
print(f"Image-like URLs found: {len(all_urls)}")
print(f"Downloaded/mapped URLs: {len(url_to_local)}")
print(f"Assets dir: {ASSET_DIR}")
