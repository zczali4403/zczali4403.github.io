"""Build the public site from Pages CMS articles, using only Python 3."""
import argparse
import datetime
import html
import math
import shutil
import json
import re
from pathlib import Path
from urllib.parse import unquote, quote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / '_site'
POSTS = []
esc = html.escape

def excerpt(post, limit=92):
    text = re.sub(r'<[^>]+>', ' ', post['content'])
    text = ' '.join(html.unescape(text).split())
    return text[:limit] + ('…' if len(text) > limit else '')

def header():
    return '''<a class="skip" href="#content">Skip to content</a>
<header class="site-header wrap"><a class="brand" href="/"><span class="brand-symbol" aria-hidden="true">cz.</span><span>Chengzhi Zhao</span><span class="brand-en">AI × BIOLOGY</span></a><nav aria-label="Main navigation"><a href="/#journey">Journey</a><a href="/#education">Education</a><a href="/#research">Research</a><a href="/#about">About</a><a class="nav-current" aria-current="page" href="/blog/">Writing</a></nav></header>'''

def page(title, description, url, body):
    return f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{esc(title)} · Chengzhi Zhao</title><meta name="description" content="{esc(description, quote=True)}"><meta name="theme-color" content="#194b40"><link rel="canonical" href="https://zczali4403.github.io{url}"><link rel="icon" href="/favicon.ico"><link rel="stylesheet" href="/styles.css"></head>
<body class="writing-page">{header()}{body}<footer class="wrap"><a href="/">Chengzhi Zhao · AI for Biology</a><span>已识乾坤大，犹怜草木青 · <a href="/admin/">写作后台</a></span><a href="#">Back to top ↑</a></footer></body></html>\n'''

def write(url, content):
    path = OUTPUT / unquote(url.lstrip('/')) / 'index.html'
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

def load_posts(root):
    posts = []
    urls = set()
    for source in sorted((root / 'content/posts').glob('*.json')):
        post = json.loads(source.read_text())
        for field in ('title', 'date', 'content'):
            if not isinstance(post.get(field), str) or not post[field].strip():
                raise ValueError(f'{source.name}: {field} must not be empty')
        date = datetime.date.fromisoformat(post['date'])
        if date.isoformat() != post['date']:
            raise ValueError(f'{source.name}: date must use YYYY-MM-DD')
        # New entries keep their filename-based URL even when the title/date changes.
        url = post.get('url') or '/diary/' + quote(source.stem, safe='-') + '/'
        parsed = urlsplit(url)
        decoded = unquote(url)
        parts = decoded.strip('/').split('/')
        if (parsed.scheme or parsed.netloc or parsed.query or parsed.fragment
                or not url.startswith('/') or not url.endswith('/')
                or any(part in ('', '.', '..') for part in parts)
                or any(c in decoded for c in ('\\', '\x00', '"', "'", '<', '>'))
                or not (parts[0] == 'diary' or re.fullmatch(r'\d{4}', parts[0]))):
            raise ValueError(f'{source.name}: invalid article URL: {url}')
        if decoded in urls:
            raise ValueError(f'{source.name}: duplicate article URL: {url}')
        urls.add(decoded)
        post['url'] = url
        posts.append(post)
    return sorted(posts, key=lambda p: (p['date'], p['url']), reverse=True)


def build(root=ROOT, output=None):
    global ROOT, OUTPUT, POSTS
    ROOT = Path(root).resolve()
    OUTPUT = Path(output or ROOT / '_site').resolve()
    if ROOT not in OUTPUT.parents:
        raise ValueError('Output must be a dedicated directory inside the source repository')
    POSTS = load_posts(ROOT)
    marker = OUTPUT / '.site-output'
    if OUTPUT.exists() and any(OUTPUT.iterdir()) and not marker.exists():
        raise ValueError('Refusing to replace a non-build directory: ' + str(OUTPUT))
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir(parents=True)
    marker.touch()
    # Copy only public assets, never CMS sources, tests or workflow files.
    for name in ('assets', 'images', 'css', 'dist', 'js', 'admin',
                 'styles.css', 'script.js', 'profile.js', 'favicon.ico', '.nojekyll'):
        source = ROOT / name
        if source.is_dir():
            shutil.copytree(source, OUTPUT / name)
        elif source.exists():
            shutil.copy2(source, OUTPUT / name)
    for i, post in enumerate(POSTS):
        adjacent = ''
        for j, label in [(i-1, 'NEWER ENTRY'), (i+1, 'OLDER ENTRY')]:
            if 0 <= j < len(POSTS):
                p = POSTS[j]
                adjacent += f'<a href="{p["url"]}"><span>{label}</span><strong>{esc(p["title"])}</strong></a>'
        body = f'''<main class="article-main wrap" id="content"><a class="back-to-writing" href="/blog/">← All writing</a><header class="article-heading"><p class="eyebrow">WRITING / <time datetime="{post['date']}">{post['date'].replace('-', ' / ')}</time></p><h1>{esc(post['title'])}</h1><p>Chengzhi Zhao</p></header><article class="article-body">{post['content']}</article><nav class="article-pagination" aria-label="相邻文章">{adjacent}</nav><a class="back-to-writing" href="/blog/">← All writing</a></main>'''
        write(post['url'], page(post['title'], excerpt(post, 150), post['url'], body))


    listing('/blog/', POSTS)
    # Generate every year/month automatically, including pagination beyond page 2.
    prefixes = {''} | {p['date'][:4] for p in POSTS} | {p['date'][:7] for p in POSTS}
    for prefix in sorted(prefixes):
        selected = [post for post in POSTS if post['date'].startswith(prefix)]
        base = '/archives/' + (prefix.replace('-', '/') + '/' if prefix else '')
        pages = max(1, math.ceil(len(selected) / 10))
        for number in range(1, pages + 1):
            url = base if number == 1 else f'{base}page/{number}/'
            pager = ''
            if pages > 1:
                links = []
                for n in range(1, pages + 1):
                    target = base if n == 1 else f'{base}page/{n}/'
                    current = ' aria-current="page"' if n == number else ''
                    links.append(f'<a href="{target}"{current}>{n:02d}</a>')
                pager = '<nav class="writing-pagination" aria-label="文章分页">' + ''.join(links) + '</nav>'
            listing(url, selected[(number-1)*10:number*10], prefix or 'Archive', pager)
    listing('/page/2/', POSTS[10:], 'Earlier entries', '<nav class="writing-pagination"><a href="/blog/">← All entries</a></nav>')
    home = ROOT/'index.html'
    s = home.read_text()
    section = f'''<!-- WRITING START -->
    <section class="writing-section wrap" id="writing" aria-labelledby="writing-title"><div class="section-heading"><div><p class="eyebrow">NOTES ALONG THE WAY</p><h2 id="writing-title">A life beyond the lab.</h2></div><a class="text-link" href="/blog/">Explore all writing ↗</a></div><div class="writing-grid">{cards(POSTS[:3])}</div></section>
    <!-- WRITING END -->'''
    s = re.sub(r'<!-- WRITING START -->.*?<!-- WRITING END -->', lambda _: section, s, flags=re.S)
    (OUTPUT/'index.html').write_text(s)
    print(f'Built {len(POSTS)} articles and archives into {OUTPUT}.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default=str(ROOT / '_site'))
    args = parser.parse_args()
    build(output=Path(args.output))
