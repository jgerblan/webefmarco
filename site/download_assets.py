import re, os, urllib.request, time, sys

BASE = "https://web.archive.org"
with open("all_assets.txt") as f:
    urls = [l.strip() for l in f if l.strip()]

def local_path(u):
    # u like /web/20260515051336im_/https://www.efmarco.com/images/foo.png?t=0
    m = re.match(r"/web/\d+(?:im_|cs_|js_)?/https?://(?:www\.)?efmarco\.com/(.*)", u)
    if not m:
        return None
    rel = m.group(1)
    rel = rel.split("?")[0]
    if rel == "":
        rel = "index"
    return rel

ok, fail = 0, 0
for u in urls:
    rel = local_path(u)
    if rel is None:
        print("SKIP (no match):", u)
        continue
    dest = os.path.join(".", rel)
    os.makedirs(os.path.dirname(dest) or ".", exist_ok=True)
    if os.path.exists(dest):
        continue
    full_url = BASE + u
    req = urllib.request.Request(full_url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = r.read()
        with open(dest, "wb") as out:
            out.write(data)
        ok += 1
        print("OK", rel, len(data))
    except Exception as e:
        fail += 1
        print("FAIL", full_url, e)
    time.sleep(0.2)

print("done", ok, "ok,", fail, "failed")
