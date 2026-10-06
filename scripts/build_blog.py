"""Rebuild the blog and homepage writing cards using Python 3 (no dependencies)."""
import html
import json
import re
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
POSTS = sorted(json.loads((ROOT / 'posts.json').read_text()), key=lambda p: p['date'], reverse=True)
esc = html.escape

def excerpt(post, limit=92):
    text = re.sub(r'<[^>]+>', ' ', post['content'])
    text = ' '.join(html.unescape(text).split())
    return text[:limit] + ('…' if len(text) > limit else '')

def header():
    return '''<a class="skip" href="#content">Skip to content</a>
<header class="site-header wrap"><a class="brand" href="/"><span class="brand-symbol" aria-hidden="true">cz.</span><span>Chengzhi Zhao</span><span class="brand-en">AI × BIOLOGY</span></a><nav aria-label="Main navigation"><a href="/#journey">Journey</a><a href="/#research">Research</a><a href="/#about">About</a><a class="nav-current" aria-current="page" href="/blog/">Writing</a></nav></header>'''

def page(title, description, url, body):
    return f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{esc(title)} · Chengzhi Zhao</title><meta name="description" content="{esc(description, quote=True)}"><meta name="theme-color" content="#194b40"><link rel="canonical" href="https://zczali4403.github.io{url}"><link rel="icon" href="/favicon.ico"><link rel="stylesheet" href="/styles.css"></head>
<body class="writing-page">{header()}{body}<footer class="wrap"><a href="/">Chengzhi Zhao · AI for Biology</a><span>已识乾坤大，犹怜草木青</span><a href="#">Back to top ↑</a></footer></body></html>\n'''

def write(url, content):
    path = ROOT / unquote(url.lstrip('/')) / 'index.html'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)

def cards(posts):
    return '\n'.join(f'''<article class="writing-card"><time datetime="{p['date']}">{p['date'].replace('-', ' / ')}</time><h3><a href="{p['url']}">{esc(p['title'])}</a></h3><p>{esc(excerpt(p))}</p><a class="writing-read" href="{p['url']}" aria-label="阅读：{esc(p['title'], quote=True)}">Read story <span aria-hidden="true">↗</span></a></article>''' for p in posts)

def listing(url, posts, label='All entries', pager=''):
    months = sorted({p['date'][:7] for p in POSTS}, reverse=True)
    filters = [('All entries', '/blog/')] + [(m.replace('-', ' / '), '/archives/' + m.replace('-', '/') + '/') for m in months]
    links = ''.join(f'<a {"aria-current=page" if url == href else ""} href="{href}">{name}</a>' for name, href in filters)
    body = f'''<main class="wrap writing-main" id="content"><div class="writing-heading"><p class="eyebrow">NOTES ALONG THE WAY</p><h1>Thoughts, field notes,<br><em>and everything between.</em></h1><p class="writing-intro">关于科研、阅读与生活，留一些沿途的记录。</p></div><div class="writing-toolbar"><nav aria-label="按月份浏览文章">{links}</nav><span>{len(posts):02d} entries · {esc(label)}</span></div><div class="writing-grid">{cards(posts)}</div>{pager}</main>'''
    write(url, page('Writing' if label == 'All entries' else label, 'Chengzhi Zhao 的科研笔记、阅读与生活随笔。', url, body))

for i, post in enumerate(POSTS):
    adjacent = ''
    for j, label in [(i-1, 'NEWER ENTRY'), (i+1, 'OLDER ENTRY')]:
        if 0 <= j < len(POSTS):
            p = POSTS[j]
            adjacent += f'<a href="{p["url"]}"><span>{label}</span><strong>{esc(p["title"])}</strong></a>'
    body = f'''<main class="article-main wrap" id="content"><a class="back-to-writing" href="/blog/">← All writing</a><header class="article-heading"><p class="eyebrow">WRITING / <time datetime="{post['date']}">{post['date'].replace('-', ' / ')}</time></p><h1>{esc(post['title'])}</h1><p>Chengzhi Zhao</p></header><article class="article-body">{post['content']}</article><nav class="article-pagination" aria-label="相邻文章">{adjacent}</nav><a class="back-to-writing" href="/blog/">← All writing</a></main>'''
    write(post['url'], page(post['title'], excerpt(post, 150), post['url'], body))

listing('/blog/', POSTS)
# Keep every previously published archive and pagination URL usable.
for p in sorted((ROOT/'archives').rglob('index.html')):
    url = '/' + str(p.parent.relative_to(ROOT)) + '/'
    parts = p.parent.relative_to(ROOT/'archives').parts
    date_parts = parts[:parts.index('page')] if 'page' in parts else parts
    prefix = '-'.join(date_parts)
    selected = [post for post in POSTS if post['date'].startswith(prefix)]
    number = int(parts[-1]) if 'page' in parts else 1
    base = '/archives/' + ('/'.join(date_parts) + '/' if date_parts else '')
    pager = ''
    if len(selected) > 10:
        pager = f'<nav class="writing-pagination" aria-label="文章分页"><a href="{base}" {"aria-current=page" if number == 1 else ""}>01</a><a href="{base}page/2/" {"aria-current=page" if number == 2 else ""}>02</a></nav>'
    listing(url, selected[(number-1)*10:number*10], prefix or 'Archive', pager)
listing('/page/2/', POSTS[10:], 'Earlier entries', '<nav class="writing-pagination"><a href="/blog/">← All entries</a></nav>')

home = ROOT/'index.html'
s = home.read_text()
section = f'''<!-- WRITING START -->
<section class="writing-section wrap" id="writing" aria-labelledby="writing-title"><div class="section-heading"><div><p class="eyebrow">NOTES ALONG THE WAY</p><h2 id="writing-title">A life beyond the lab.</h2></div><a class="text-link" href="/blog/">Explore all writing ↗</a></div><div class="writing-grid">{cards(POSTS[:3])}</div></section>
<!-- WRITING END -->'''
s = re.sub(r'<!-- WRITING START -->.*?<!-- WRITING END -->', lambda _: section, s, flags=re.S)
home.write_text(s)
print(f'Built {len(POSTS)} articles, blog, existing archive URLs, and homepage writing cards.')
