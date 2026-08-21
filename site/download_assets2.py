import re, os, time, urllib.request

BASE = "https://web.archive.org"
FILES = []
for root, dirs, files in os.walk("."):
    for fn in files:
        if fn.startswith("raw_") and fn.endswith(".html"):
            FILES.append(os.path.join(root, fn))
FILES.append("index_raw.html")

pattern = re.compile(r'(?:src|href)="(/web/\d+(?:im_|cs_|js_)/[^"]*)"')
url_pattern = re.compile(r"url\((/web/\d+im_/[^)\s]*)\)")

urls = set()
for fn in FILES:
    try:
        with open(fn, encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except FileNotFoundError:
        continue
    for m in pattern.finditer(content):
        urls.add(m.group(1))
    for m in url_pattern.finditer(content):
        u = m.group(1).strip("'\"")
        urls.add(u)

def local_path(u):
    m = re.match(r"/web/\d+(?:im_|cs_|js_)?/https?://(?:www\.)?efmarco\.com/(.*)", u)
    if not m:
        return None
    rel = m.group(1).split("?")[0]
    if rel == "":
        rel = "index"
    return rel

tasks = []
for u in sorted(urls):
    rel = local_path(u)
    if rel is None:
        continue
    dest = os.path.join(".", rel)
    if os.path.exists(dest):
        continue
    tasks.append((u, dest))

print(f"{len(tasks)} assets to download (of {len(urls)} referenced)")

def fetch(item):
    u, dest = item
    os.makedirs(os.path.dirname(dest) or ".", exist_ok=True)
    full_url = BASE + u
    req = urllib.request.Request(full_url, headers={"User-Agent": "Mozilla/5.0"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                data = r.read()
            with open(dest, "wb") as out:
                out.write(data)
            return ("OK", dest, len(data))
        except Exception as e:
            last_err = str(e)
            time.sleep(2 * (attempt + 1))
    return ("FAIL", dest, last_err)

ok, fail = 0, 0
for t in tasks:
    status, dest, info = fetch(t)
    if status == "OK":
        ok += 1
    else:
        fail += 1
        print("FAIL", dest, info)
    time.sleep(0.3)
print("done", ok, "ok,", fail, "failed")

