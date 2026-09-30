# Builds static/js/search-index.js from the post pages, for the blog search (search.html).
# Run from the repository root after a post is added or changed:  python tools/build_search_index.py
import glob, html, json, os, re, sys
from urllib.parse import quote

sys.stdout.reconfigure(encoding="utf-8")
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
posts = []

for path in sorted(glob.glob(os.path.join(root, "post", "*", "index.htm"))):
    page = open(path, encoding="utf-8-sig").read()
    main = re.search(r'<div class="col-xs-9">(.*?)<div class="col-xs-3">', page, re.S)
    if not main:
        continue
    main = main.group(1)
    title = re.search(r"<h3>(.*?)</h3>", main, re.S)
    meta = re.search(r"מאת\s*(.*?)\s*<span[^>]*glyphicon-time[^>]*></span>\s*פורסם ב-(\d{1,2})\.(\d{1,2})\.(\d{4})", main, re.S)
    body = main.split("<hr>", 1)[-1]
    body = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", body, flags=re.S)
    body = re.sub(r"<[^>]+>", " ", body)
    body = re.sub(r"\s+", " ", html.unescape(body)).strip()
    author = meta.group(1).strip() if meta else ""
    posts.append({
        "t": re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", title.group(1)))).strip() if title else "",
        "u": "post/" + quote(os.path.basename(os.path.dirname(path))) + "/index.htm",
        "a": "" if author in ("None", "") else author,
        "d": "%s-%s-%s" % (meta.group(4), meta.group(3).zfill(2), meta.group(2).zfill(2)) if meta else "",
        "x": body,
    })

out = os.path.join(root, "static", "js", "search-index.js")
with open(out, "w", encoding="utf-8") as f:
    f.write("var SEARCH_INDEX = " + json.dumps(posts, ensure_ascii=False) + ";\n")
print(len(posts), "posts,", round(os.path.getsize(out) / 1024), "KB ->", out)
