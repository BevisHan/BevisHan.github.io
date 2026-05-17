# Obsidian 笔记 → 博客文章

## 工作流

1. 在 Obsidian 中写笔记
2. 把笔记复制到 `_notes/` 目录
3. 运行 `python3 scripts/sync-notes.py`（或 GitHub Actions 自动同步）
4. 笔记自动转换成博客文章 → 部署到 `bevishan.github.io`

## 笔记格式

笔记文件名：`YYYY-MM-DD-标题.md`

笔记开头需要 front matter：

```yaml
---
title: 遇到的问题标题
date: 2024-01-01
categories: [踩坑实录]   # 或 [最佳实践], [学习笔记]
tags: [Spring Cloud, Nacos]
published: true
---
```

笔记内容使用标准 Markdown 即可。

## 分类建议

- `踩坑实录` — 各种 Bug 排查和问题解决过程
- `最佳实践` — 技术选型、架构设计经验
- `学习笔记` — 新技术的学习总结

## 不使用 Obsidian？

如果你不想用 Obsidian，也可以直接在 `_posts/` 目录下手动创建 `.md` 文件，
按照标准的 Chirpy 博客格式写，`push` 到 GitHub 后会自动部署。
