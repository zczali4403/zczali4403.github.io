# Chengzhi Zhao — personal website

English academic homepage with an interactive journey, plus the original Chinese blog in the same cream and forest-green style. This repository is the static site for https://zczali4403.github.io/.

## Local preview

```sh
python3 -m http.server 4174 --bind 127.0.0.1
```

Open http://127.0.0.1:4174/ for the homepage and http://127.0.0.1:4174/blog/ for all writing.

## Editing

- `profile.js`: biography, school details, photo credits and profile links.
- `index.html`: homepage structure and research descriptions; the writing section is generated.
- `styles.css`: shared appearance and responsive layouts.
- `script.js`: journey playback, city selection and campus photo dialogs.
- `posts.json`: original article titles, dates, URLs and HTML bodies. Edit here before rebuilding.

After changing posts, run:

```sh
python3 scripts/build_blog.py
```

The dependency-free script regenerates article pages, `/blog/`, existing archive pages, `/page/2/`, and the homepage's latest-writing cards. All 15 original article bodies and their URLs were preserved during migration. The original site remains in Git history; the earlier interactive prototype remains in the sibling `previous-site-files` directory.

## GitHub Pages

The output is plain HTML/CSS/JavaScript. No package installation or build service is needed. Publish this repository's root using GitHub Pages; `.nojekyll` is included. Blog links target the root domain `zczali4403.github.io`.

Map geometry and campus photos are local. Attribution is in `assets/ATTRIBUTION.md`. Existing blog images retain their original external URLs and depend on those hosts remaining available.
