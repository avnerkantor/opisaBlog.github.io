# Search engine optimisation for the blog (https://blog.opisa.org/)
# Gives every page its own title, description, canonical link, social tags and structured data,
# and writes sitemap.xml, robots.txt and CNAME. Safe to run again. Run from the repository root:
#   python tools/build_seo.py
import glob, html, json, os, re, sys
from urllib.parse import quote

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://blog.opisa.org/"
SITE = "https://opisa.org/"
BRAND = "פיזה פתוח"
START, END = "<!--seo-->", "<!--/seo-->"

index = json.loads(re.sub(r"^var SEARCH_INDEX = |;\s*$", "", open(os.path.join(ROOT, "static/js/search-index.js"), encoding="utf-8").read()))
by_url = {p["u"]: p for p in index}


def short(text, n=155):
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= n:
        return text
    return text[:n].rsplit(" ", 1)[0].rstrip(",.;:-") + "…"


def attr(s):
    return html.escape(s, quote=True)


def head_block(title, desc, url, kind="website", date=None, author=None, noindex=False):
    tags = [
        START,
        '<meta name="robots" content="%s">' % ("noindex, follow" if noindex else "index, follow"),
        '<link rel="canonical" href="%s">' % attr(url),
        '<meta property="og:site_name" content="%s">' % BRAND,
        '<meta property="og:locale" content="he_IL">',
        '<meta property="og:type" content="%s">' % kind,
        '<meta property="og:title" content="%s">' % attr(title),
        '<meta property="og:description" content="%s">' % attr(desc),
        '<meta property="og:url" content="%s">' % attr(url),
        '<meta property="og:image" content="%sstatic/img/bag-512.png">' % BASE,
        '<meta name="twitter:card" content="summary">',
    ]
    if kind == "article":
        data = {
            "@context": "https://schema.org", "@type": "BlogPosting", "headline": title.split(" | ")[0],
            "description": desc, "inLanguage": "he", "url": url, "mainEntityOfPage": url,
            "image": BASE + "static/img/bag-512.png",
            "author": {"@type": "Person", "name": author} if author else {"@type": "Organization", "name": BRAND},
            "publisher": {"@type": "Organization", "name": BRAND, "url": SITE},
        }
        if date:
            data["datePublished"] = date
        tags.append('<script type="application/ld+json">%s</script>' % json.dumps(data, ensure_ascii=False))
    else:
        data = {"@context": "https://schema.org", "@type": "Blog", "name": BRAND + " | בלוג", "url": BASE,
                "inLanguage": "he", "publisher": {"@type": "Organization", "name": BRAND, "url": SITE}}
        tags.append('<script type="application/ld+json">%s</script>' % json.dumps(data, ensure_ascii=False))
    tags.append(END)
    return "\n".join(tags) + "\n"


def apply(path, title, desc, url, **kw):
    t = open(path, "rb").read().decode("utf-8")
    nl = "\r\n" if "\r\n" in t else "\n"
    t = re.sub(r"<title>.*?</title>", lambda m: "<title>%s</title>" % html.escape(title, quote=False), t, count=1, flags=re.S)
    desc_tag = '<meta name="description" content="%s">' % attr(desc)
    t = re.sub(r"<meta name=\"description\" content=(['\"]).*?\1>", lambda m: desc_tag, t, count=1, flags=re.S)
    t = re.sub(r"\s*%s.*?%s\n?" % (re.escape(START), re.escape(END)), "", t, flags=re.S)
    t = t.replace('rel="short/cut icon"', 'rel="shortcut icon"')
    t = t.replace('href="http://opisa.org"', 'href="https://opisa.org/he.html"').replace('href="https://opisa.org/"', 'href="https://opisa.org/he.html"')
    block = head_block(title, desc, url, **kw).replace("\n", nl)
    t = t.replace("</head>", block + "</head>", 1)
    open(path, "wb").write(t.encode("utf-8"))


urls = []
posts = 0
for path in sorted(glob.glob(os.path.join(ROOT, "post", "*", "index.htm"))):
    rel = "post/" + quote(os.path.basename(os.path.dirname(path))) + "/index.htm"
    p = by_url[rel]
    title = "%s | בלוג %s" % (p["t"], BRAND)
    desc = short(p["x"]) or "רשומה בבלוג %s" % BRAND
    url = BASE + rel[: -len("index.htm")]
    apply(path, title, desc, url, kind="article", date=p["d"] or None, author=p["a"] or None)
    urls.append((url, p["d"]))
    posts += 1

home_desc = "הבלוג של פיזה פתוח: כתבות, ניתוחים ועבודות מחקר על נתוני מבחני פיזה והחינוך בישראל."
for n, name in enumerate(["index.htm"] + ["index-%d.htm" % i for i in range(1, 6)], start=1):
    path = os.path.join(ROOT, name)
    if not os.path.exists(path):
        continue
    page = 1 if name == "index.htm" else int(re.search(r"\d+", name).group())
    title = "בלוג %s" % BRAND if name == "index.htm" else "בלוג %s | עמוד %d" % (BRAND, page)
    url = BASE if name == "index.htm" else BASE + name
    apply(path, title, home_desc, url)
    urls.append((url, None))

apply(os.path.join(ROOT, "about.html"), "אודות | בלוג %s" % BRAND,
      "על פיזה פתוח: יוזמה משותפת של קרן טראמפ והמרכז לחקר האינטרנט באוניברסיטת חיפה להנגשת נתוני מבחן פיזה.",
      BASE + "about.html")
urls.append((BASE + "about.html", None))
apply(os.path.join(ROOT, "search.html"), "חיפוש | בלוג %s" % BRAND, home_desc, BASE + "search.html", noindex=True)

with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8", newline="\n") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
    for u, d in urls:
        f.write("  <url><loc>%s</loc>%s</url>\n" % (html.escape(u), "<lastmod>%s</lastmod>" % d if d else ""))
    f.write("</urlset>\n")
with open(os.path.join(ROOT, "robots.txt"), "w", newline="\n") as f:
    f.write("User-agent: *\nAllow: /\nDisallow: /search.html\n\nSitemap: %ssitemap.xml\n" % BASE)
with open(os.path.join(ROOT, "CNAME"), "w", newline="\n") as f:
    f.write("blog.opisa.org\n")
print(posts, "posts,", len(urls), "urls in sitemap")
