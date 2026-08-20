# Philip's personal blog

## Writing workflow

```bash
# posts live in content/posts/N_title.md

# local preview with drafts, live-reloads at http://localhost:1313  (brew install hugo if not installed)
hugo server -D

# publish: set "draft: false" in front matter, then git commit & push
```

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
