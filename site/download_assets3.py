import re, os, subprocess, time

BASE = "https://web.archive.org"
FILES = []
for root, dirs, files in os.walk("."):
    for fn in files:
        if fn.startswith("raw_") and fn.endswith(".html"):
            FILES.append(os.path.join(root, fn))
FILES.append("index_raw.html")

pattern = re.compile(r'(?:src|href)="(?:https?://web\.archive\.org)?(/web/\d+(?:im_|cs_|js_)/[^"]*)"')
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

ok, fail = 0, 0
for u, dest in tasks:
    os.makedirs(os.path.dirname(dest) or ".", exist_ok=True)
    full_url = BASE + u
    code = "000"
    for attempt in range(3):
        try:
            result = subprocess.run(
                ["curl", "-sL", "--retry", "2", "--retry-delay", "2",
                 "-o", dest, "-w", "%{http_code}", full_url],
                capture_output=True, text=True, timeout=90
            )
            code = result.stdout.strip()
        except subprocess.TimeoutExpired:
            code = "000"
        if code == "200" and os.path.exists(dest) and os.path.getsize(dest) > 0:
            break
        time.sleep(1.5)
    if code == "200" and os.path.exists(dest) and os.path.getsize(dest) > 0:
        ok += 1
    else:
        fail += 1
        if os.path.exists(dest):
            os.remove(dest)
        print("FAIL", dest, "http", code)
        if os.path.exists(dest) and os.path.getsize(dest) == 0:
            os.remove(dest)

print("done", ok, "ok,", fail, "failed")
