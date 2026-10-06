# Chengzhi Zhao — personal website

Interactive academic homepage and Chinese blog, published at https://zczali4403.github.io/.

## 在线写作

入口：https://zczali4403.github.io/admin/

1. 点击「进入写作后台」，使用 GitHub 登录 Pages CMS。
2. 首次安装 Pages CMS GitHub App 时，只选择 `zczali4403.github.io` 仓库。
3. 选择该仓库的 `main` 分支，进入「日记与文章」。
4. 新建文章，填写标题、日期、正文。正文是可视化编辑器，不需要写 JSON 或 HTML。
5. 点击图片按钮，上传图片或选用「日记图片」里的现有图片。
6. 保存即提交到公开仓库。`Publish website` 自动测试、生成页面并发布；在 Actions 中等到成功后刷新网站。

上传图片放在 `assets/blog/`；新上传文件使用随机名称，避免覆盖同名图片。旧文章地址保留不变。新文章地址由创建时的文件名生成，修改标题或日期不会更改地址。不需要手工新建月份目录。

本站是公开仓库，保存的文章和上传的图片都是公开内容，不提供私密草稿功能。

## 首次发布设置

仓库 Settings → Pages → Build and deployment → Source 应设为 **GitHub Actions**。
工作流是 `.github/workflows/publish.yml`，可在 Actions 页面手动点击 Run workflow。
Pages CMS 的登录授权与网页的 GitHub Pages 发布设置是独立的。

## 本地编辑与预览

每篇文章对应 `content/posts/` 下的一份 JSON 文件；该目录是文章的唯一编辑源。旧的合并文件 `posts.json` 已迁移，不再使用。

```sh
python3 -m unittest discover -s tests -v
python3 scripts/build_blog.py --output _site
python3 -m http.server 4175 --bind 127.0.0.1 --directory _site
```

打开 http://127.0.0.1:4175/。构建会重建 `_site/`，因此编辑源码，不要编辑 `_site/` 中的文件。它不会把 CMS 源文件、测试或工作流复制到公开站点，但 GitHub 仓库本身仍是公开的。

- `content/posts/*.json`：文章标题、日期、HTML 正文，以及旧文章的固定 URL。
- `.pages.yml`：在线编辑表单、图片库、上传规则。
- `scripts/build_blog.py`：生成文章、首页摘要、博客列表、年份/月度归档和分页；删除文章后不残留旧输出。
- `index.html`：首页模板与研究介绍；writing 标记中的内容在构建时更新。
- `profile.js`：个人介绍、学校、照片来源、个人链接。
- `styles.css` / `script.js`：外观与足迹交互。
- `admin/index.html`：写作后台入口与使用说明。

根目录保留的旧文章 HTML 是迁移前的静态快照，便于核对旧链接；生产站点只部署新构建的 `_site/`。

## 图片来源

地图数据和校园照片来源见 `assets/ATTRIBUTION.md`。80 张博客原图位于 `assets/blog/`；原 `photo` 仓库的本地完整备份位于同级 `previous-site-files/photo-repository-backup`。
