# Docs Translation Notes

这份记录总结了本仓库 `docs` 翻译与润色时的经验，后续继续翻译时请优先遵守。适用于所有语种。

## 核心原则

- 先保结构，再翻内容。
- 术语统一优先于字面直译。
- URL、锚点、代码、命令名、品牌名要谨慎处理，能不翻就不翻。
- Markdown 里的图片、链接、HTML 标签、脚注、目录结构，必须保持原始语义和渲染方式。

## 常见坑

- 不要破坏原文的 HTML 结构（`<img>`、`<aside>`、`<style>` 等）和 Markdown 图片语法。
- 不要翻译命令名、子命令、包名、模块名、品牌名、指令名、匹配器名称（如 `xcaddy`、`Railway`、`mise`、`reverse_proxy`）；只翻说明文字。
- 不要机械替换有技术语义的词：`header` 在 HTTP 语境应译为 `标头`（不是 `标题`）；`profile` 在性能语境应译为 `剖析`（不是 `个人资料`）。
- 不要凭感觉改页内锚点，标题翻译后 `#slug` 会变，需检查 TOC 和正文链接。
- 原文 `_..._` 斜体在译文中必须改为 `*...*`（goldmark 遵循 CommonMark，`_` 紧邻 Unicode 字母时无法触发斜体）。
- `**...**` 加粗同理：闭合 `**` 前面是标点、后面是汉字时（如 `。**它`），CommonMark 判定不满足 right-flanking，加粗失效。修复：在闭合 `**` 后加一个空格（`。** 它`）。
- 原文 HTML 片段（非 Markdown 代码块）里的占位符（如 `<path>`）必须写成 `&lt;path&gt;`，否则渲染异常。
- 代码块（Caddyfile、shell、systemd 配置等）内的 `# 注释` 也要翻译；Go 接口注释（`// Provision implements...`）可保留英文。
- Prometheus 指标文档中的 `# HELP` / `# TYPE` 行是机器可读格式，**不翻译**。
- 列表项缩进必须严格对齐原文。少一级缩进会把子项抬成外层列表，多一级缩进会意外生成新的嵌套列表；这类问题不会总是肉眼明显，但会改变 Markdown AST 结构。

## 锚点经验

goldmark 会跳过所有多字节 UTF-8 字符（非 ASCII），含译文字符的标题会生成 `heading`、`heading-1` 这类无意义 ID，导致 TOC 链接失效。

修复方法：在含非 ASCII 字符的标题前加一行 `<a id>`，沿用英文原版 slug：

```markdown
<a id="overview"></a>
## 概述
```

纯英文标题无需处理，goldmark 可以正常生成语义 ID。

## 翻译风格

- 面向开发者的文档，要自然、直接、少修辞。
- 尽量简洁，不要把句子翻得过长。
- 说明类段落可以稍微意译，但不要丢掉条件、限制、警告和默认行为。
- 列表项、标题、注释要尽量和原文结构对齐，方便后续 diff 和同步更新。

## 多语言架构（`common.js` / `docs/index.html`）

新增语种需要同步修改**两处代码**，并提供译文文件：

**1. `src/resources/js/common.js`** — `SITE_LOCALES` 数组（在 `getDocsLocalePrefix` 函数前）：

```js
const SITE_LOCALES = [
    { prefix: '',         label: 'English' },
    { prefix: '/zh-hans', label: '中文' },
    // 新增：{ prefix: '/ja', label: '日本語' },
];
```

- `getDocsLocalePrefix()` 和 `initLangSwitcher()` 均从该数组读取，无需改动。
- `localizeDocsLinks()` 选择器为 `a[href^="/docs"]:not(#lang-switcher)`，确保语言切换链接不被本地化覆盖。

**2. `src/docs/index.html`** — 顶部 locale 检测块（`$locale` / `$htmlLang`）：

```html
{{if hasPrefix "/zh-hans/" .OriginalReq.URL.Path -}}
    {{$locale = "zh-hans" -}}
    {{$htmlLang = "zh-Hans" -}}
{{/* 新增：{{else if hasPrefix "/ja/" ...}} */}}
{{end -}}
```

译文 md 路径规则：`/i18n/{locale}/docs/markdown/`；若文件不存在，自动回退到英文原版。

**3. 译文文件** — 在 `src/i18n/{locale}/docs/markdown/` 下放置 `.md` 文件，目录结构与 `src/docs/markdown/` 一致；缺失文件自动回退英文，无需全量翻译即可上线。

**4. 侧边栏导航** — 在 `src/i18n/{locale}/includes/docs/nav.html` 放置译文导航 HTML，参照 `src/includes/docs/nav.html`（英文原版）翻译链接文字即可；`docs/index.html` 会自动选取，文件不存在时回退英文。

## 本项目里建议保留的词

- `Caddy`
- `Caddyfile`
- `xcaddy`
- `Railway`
- `mise`
- `ACME`
- `TLS`
- `ECH`
- `HTTPS` / `HTTP`
- `DNS`
- `JSON`
- `Markdown`
- `systemd`
- Caddyfile 指令名：`abort`, `acme_server`, `basic_auth`, `bind`, `encode`, `error`, `file_server`, `forward_auth`, `fs`, `handle`, `handle_errors`, `handle_path`, `header`, `import`, `intercept`, `invoke`, `log`, `log_append`, `log_name`, `log_skip`, `map`, `method`, `metrics`, `php_fastcgi`, `push`, `redir`, `request_body`, `request_header`, `respond`, `reverse_proxy`, `rewrite`, `root`, `route`, `templates`, `tls`, `tracing`, `try_files`, `uri`, `vars`
- 架构术语：`handler`, `middleware`, `matcher`, `route`, `upstream`, `placeholder`

## 质量检查工具

`scripts/lint-i18n.py` 用于检测常见翻译渲染问题，在仓库根目录运行：

```bash
# 示例：
.venv/bin/python scripts/lint-i18n.py zh-hans
```

- `MARKERS` 检查基于 `markdown-it-py` 解析 Markdown AST，对比原文与译文的块级结构（标题层级、列表、代码块、`aside/style/script/div` 等），不是简单的正则计数。
- 结构对比前会剥离 YAML front matter，以及独立一行的 `<a id="..."></a>` / `<span id="..."/>` 补锚点行，避免把译文为修 slug 主动添加的锚点误报为结构漂移。
- 若 `MARKERS` 报 `UL` 数量不一致，优先检查列表项缩进是否与原文一致，尤其是连续的 `- item`、嵌套子项，以及列表项下方的说明段落是否仍属于同一列表项。
- 若 `MARKERS` 报 `H2`/`H3` 数量不一致，但肉眼能看到标题存在，优先检查标题前是否紧邻 `<aside ...>`、`<a id>`、`<span id>` 等 HTML 行；解析器可能把它们与标题合并成一个 `html_block`。