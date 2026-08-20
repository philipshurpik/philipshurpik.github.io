# Personal blog - Hugo + PaperMod + GitHub Pages

Markdown in, website out. Push to `main` and GitHub Actions builds and deploys automatically.

## One-time setup

```bash
cd blog
git init -b main
git submodule add --depth=1 https://github.com/adityatelange/hugo-PaperMod.git themes/PaperMod
git add .
git commit -m "blog: initial setup"
git remote add origin git@github.com:philipshurpik/philipshurpik.github.io.git
git push -u origin main
```

Watch the Actions tab - the site is live in about a minute. (If the very first run raced ahead of step 2, just re-run it.)

## Writing workflow

```bash
# new post
cp content/posts/first-post.md content/posts/my-next-post.md

# local preview with drafts, live-reloads at http://localhost:1313
hugo server -D

# publish: set "draft: false" in front matter, then
git add . && git commit -m "post: my next post" && git push
```

Local Hugo install (only needed for preview - CI builds regardless): `brew install hugo`

## Front matter cheatsheet

```yaml
---
title: "Post title"
date: 2026-08-20
draft: true        # false to publish
tags: ["llm", "gpu"]
showtoc: true      # per-post table of contents
---
```

## Later

- **Custom domain**: buy one, add a `CNAME` DNS record pointing to `philipshurpik.github.io`, set it in Settings → Pages. HTTPS is automatic.
- **Update theme**: `git submodule update --remote --merge themes/PaperMod`
- **Search page, comments, analytics**: see PaperMod wiki - https://github.com/adityatelange/hugo-PaperMod/wiki/Features
