# Twitter to Markdown

## Shit to Do

- 明明下面还有推文却无法继续获取

```text
plantgazer -> ============================================================
plantgazer -> 第 88 次滚动，正在获取推文...(12/12)
plantgazer -> 发布时间： ********
plantgazer -> 发布者： ********
plantgazer -> 推文地址： ********
plantgazer -> 推文内容： ********
plantgazer -> 推文图片： []
抓取时出错: Locator expected to be visible
Actual value: <element(s) not found> 
Call log:
LocatorAssertions.to_be_visible with timeout 100000ms
  - waiting for locator("article").first


Process finished with exit code 0
```

- 把推文内容中含有的 `@username` 替换成 `[@username](https://x.com/username)` 
- 将推文保存为 Markdown 文件
- 下载推文中的图片，保存到附件文件夹