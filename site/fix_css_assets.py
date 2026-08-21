#!/usr/bin/env python3
"""Find wayback-relative asset URLs embedded in CSS files (url(...) references
that were never touched by build.py since it only rewrites .html files),
download any missing local assets from Wayback Machine, and rewrite the CSS
url(...) references to plain local relative paths.

Applies to both the site-root source CSS copies and their dist/ mirrors.
"""
import re
import os
import subprocess
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
BASE = "https://web.archive.org"

CSS_FILES = [
    "templates/ja_medicare/css/template.css",
    "templates/ja_medicare/local/css/mod_jaslideshowlite.css",
    "templates/system/css/system.css",
    "templates/ja_medicare/fonts/font-awesome/css/font-awesome.min.css",
    "templates/ja_medicare/local/css/bootstrap.css",
    "plugins/system/t3/base-bs3/fonts/font-awesome/css/font-awesome.min.css",
]

# Matches: optional "https://web.archive.org" prefix + "/web/TIMESTAMP[im_|cs_|js_]/"
# + the real efmarco.com URL, capturing the path+query+fragment after the domain.
WAYBACK_ASSET_RE = re.compile(
    r'(?:https?://web\.archive\.org)?/web/\d+(?:im_|cs_|js_)?/https?://(?:www\.)?efmarco\.com/([^"\'\)\s]*)'
)


def remote_and_local(rel_path_with_query):
    """Given the path portion after efmarco.com/, return (remote_url_path, local_fs_path)."""
    # Strip query string and fragment for the local file path, but keep full
    # thing for downloading (some CDNs care about ?v=... but here content is
    # static so plain path is fine).
    clean = rel_path_with_query.split("?")[0].split("#")[0]
    return clean


def main():
    # 1) Collect every distinct wayback-wrapped asset reference across the CSS files.
    all_matches = {}  # local_clean_path -> one example full match (for download)
    for rel in CSS_FILES:
        path = os.path.join(ROOT, rel)
        with open(path, encoding="utf-8", errors="ignore") as f:
            content = f.read()
        for m in WAYBACK_ASSET_RE.finditer(content):
            full_match = m.group(0)
            captured = m.group(1)
            clean = remote_and_local(captured)
            if clean not in all_matches:
                all_matches[clean] = full_match

    print(f"Found {len(all_matches)} distinct assets referenced from CSS")

    # 2) Download any that don't already exist locally.
    ok, fail, skipped = 0, 0, 0
    for clean, full_match in sorted(all_matches.items()):
        dest = os.path.join(ROOT, clean)
        if os.path.exists(dest):
            skipped += 1
            continue
        os.makedirs(os.path.dirname(dest) or ROOT, exist_ok=True)
        # Reconstruct the wayback URL for downloading.
        if full_match.startswith("http"):
            full_url = full_match
        else:
            full_url = BASE + full_match
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
            print("OK  ", clean)
        else:
            fail += 1
            if os.path.exists(dest) and os.path.getsize(dest) == 0:
                os.remove(dest)
            print("FAIL", clean, "http", code, full_url)

    print(f"Downloaded: {ok} ok, {fail} failed, {skipped} already present")

    # 3) Rewrite the CSS files (source) to use local relative paths, then
    #    copy the fixed content into the dist/ mirror as well.
    for rel in CSS_FILES:
        src_path = os.path.join(ROOT, rel)
        with open(src_path, encoding="utf-8", errors="ignore") as f:
            content = f.read()

        css_dir = os.path.dirname(rel)  # e.g. templates/ja_medicare/css

        def repl(m):
            captured = m.group(1)
            clean = remote_and_local(captured)
            # Preserve any query/fragment suffix that followed the clean path.
            suffix = captured[len(clean):]
            target_abs = clean  # root-relative path, e.g. templates/ja_medicare/images/x.png
            rel_path = os.path.relpath(target_abs, css_dir)
            return rel_path + suffix

        new_content, n = WAYBACK_ASSET_RE.subn(repl, content)
        with open(src_path, "w", encoding="utf-8") as f:
            f.write(new_content)

        dist_path = os.path.join(ROOT, "dist", rel)
        os.makedirs(os.path.dirname(dist_path), exist_ok=True)
        with open(dist_path, "w", encoding="utf-8") as f:
            f.write(new_content)

        print(f"Rewrote {n} references in {rel}")


if __name__ == "__main__":
    main()
