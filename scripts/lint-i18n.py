#!/usr/bin/env python3
"""
lint-i18n.py — 检查 i18n 译文 Markdown 的常见问题

用法：
  python3 scripts/lint-i18n.py zh-hans      # 检查指定语种（必填，只能传一个）
"""

import os
import re
import sys
import unicodedata

try:
    from markdown_it import MarkdownIt
except ImportError:
    MarkdownIt = None

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
I18N_ROOT = os.path.join(REPO_ROOT, "src", "i18n")
MD = MarkdownIt("commonmark", {"html": True}) if MarkdownIt is not None else None

NON_ASCII = re.compile(r"[^\x00-\x7f]")

def is_unicode_letter(ch):
    """返回 True 当且仅当 ch 是 Unicode 字母（category L*），即非标点、非符号。"""
    return unicodedata.category(ch).startswith('L')

def heading_slug(text):
    """模拟 goldmark WithAutoHeadingID：去掉非 ASCII、非 alnum 字符，空格转 -，小写。"""
    # 先剥掉行内代码（`...`）和加粗/斜体标记
    text = re.sub(r'`[^`]*`', '', text)
    text = re.sub(r'\*+|_+', '', text)
    # 只保留 ASCII 字母、数字、空格、连字符、下划线
    result = ''.join(c if c in '-_ ' or ('a' <= c <= 'z') or ('0' <= c <= '9') else ''
                     for c in text.lower())
    result = re.sub(r'[\s_]+', '-', result).strip('-')
    return result

def in_inline_code(line, pos):
    """判断 pos 位置是否处于行内代码（奇数个反引号之后）中。"""
    return line[:pos].count('`') % 2 == 1

def has_toc(raw):
    """返回 True 当且仅当文档在第一个 H2 之前有页内锚点链接（即存在手写 TOC）。"""
    before_h2 = raw.split('\n## ')[0].split('\n### ')[0]
    return bool(re.search(r'\]\(#[^)]+\)', before_h2))


def missing_toc_anchors(raw):
    """
    返回 TOC 中引用但既无 <a id> 定义、也无对应 ASCII 标题自然生成的 slug 列表。
    只有这些才是真实的锚点缺失问题。
    """
    # 提取 TOC 引用的所有锚点（文档第一个 H2 之前的列表中 (#slug) 形式）
    before_h2 = raw.split('\n## ')[0].split('\n### ')[0]
    toc_anchors = set(re.findall(r'\]\(#([^)]+)\)', before_h2))
    if not toc_anchors:
        return []

    # 收集文档中已有的显式锚点（<a id="..."> 或 <span id="..."/>）
    defined = set(re.findall(r'<(?:a|span) id="([^"]+)"', raw))

    # 收集所有纯 ASCII 标题自然生成的 slug（goldmark 可以正常处理）
    natural = set()
    for m in re.finditer(r'^#{1,6}\s+(.*)', raw, re.MULTILINE):
        s = heading_slug(m.group(1))
        if s:
            natural.add(s)

    # 缺失 = TOC 引用的 - 已定义的 - 自然生成的
    return sorted(toc_anchors - defined - natural)


def source_path_for_translation(path, locale):
    """将译文路径映射回英文原文路径；若无法映射则返回 None。"""
    rel = os.path.relpath(path, os.path.join(I18N_ROOT, locale, "docs", "markdown"))
    source_path = os.path.join(REPO_ROOT, "src", "docs", "markdown", rel)
    return source_path if os.path.isfile(source_path) else None


def strip_front_matter(raw):
    """移除文件开头的 YAML front matter，避免被 CommonMark 误解析为 hr/heading。"""
    if not raw.startswith("---\n"):
        return raw
    end = raw.find("\n---\n", 4)
    if end == -1:
        return raw
    return raw[end + 5:]


def strip_anchor_only_lines(raw):
    """移除仅用于补锚点的独立 HTML 行，避免吞掉后续 Markdown 标题。"""
    return re.sub(
        r'(?mi)^\s*(?:<a\s+id="[^"]+"\s*></a>|<span\s+id="[^"]+"\s*/>)\s*$\n?',
        '\n',
        raw,
    )


def html_block_kind(content):
    """将 html_block 归一化为我们关心的块级标签名。"""
    match = re.match(r'\s*<(aside|style|script|div)\b', content, re.I)
    if not match:
        return None
    return match.group(1).upper()


def structural_counts(raw):
    """基于 Markdown AST 统计需与原文保持一致的块级结构。"""
    if MD is None:
        raise RuntimeError("缺少依赖 markdown-it-py；请使用工作区 .venv 或先安装它")

    raw = strip_anchor_only_lines(strip_front_matter(raw))

    counts = {
        "H1": 0,
        "H2": 0,
        "H3": 0,
        "FENCE": 0,
        "UL": 0,
        "OL": 0,
        "LI": 0,
        "BQ": 0,
        "HR": 0,
        "ASIDE": 0,
        "STYLE": 0,
        "SCRIPT": 0,
        "DIV": 0,
    }

    for token in MD.parse(raw):
        if token.type == "heading_open":
            if token.tag == "h1":
                counts["H1"] += 1
            elif token.tag == "h2":
                counts["H2"] += 1
            elif token.tag == "h3":
                counts["H3"] += 1
        elif token.type == "fence":
            counts["FENCE"] += 1
        elif token.type == "bullet_list_open":
            counts["UL"] += 1
        elif token.type == "ordered_list_open":
            counts["OL"] += 1
        elif token.type == "list_item_open":
            counts["LI"] += 1
        elif token.type == "blockquote_open":
            counts["BQ"] += 1
        elif token.type == "hr":
            counts["HR"] += 1
        elif token.type == "html_block":
            kind = html_block_kind(token.content)
            if kind:
                counts[kind] += 1

    return counts


def marker_mismatches(path, locale, raw):
    """对比原文与译文的块级 Markdown 结构，返回不一致项。"""
    source_path = source_path_for_translation(path, locale)
    if not source_path:
        return []

    with open(source_path, encoding="utf-8") as f:
        source_raw = f.read()

    source_markers = structural_counts(source_raw)
    translated_markers = structural_counts(raw)
    mismatches = []
    for key, source_count in source_markers.items():
        translated_count = translated_markers[key]
        if source_count != translated_count:
            mismatches.append(f"{key} {translated_count}!={source_count}")
    return mismatches


# ── 检测函数 ──────────────────────────────────────────────────────────────────

def check_file(path, locale):
    errors = []

    with open(path, encoding="utf-8") as f:
        raw = f.read()

    mismatches = marker_mismatches(path, locale, raw)
    if mismatches:
        errors.append((0, "MARKERS", "Markdown 结构标记数量与原文不一致：" + ", ".join(mismatches)))

    lines = raw.splitlines()
    in_code = False
    in_script = False
    prev_nonempty = ""
    file_has_toc = has_toc(raw)

    # ② TOC 引用的锚点缺失（文件级别一次性检查）
    for slug in missing_toc_anchors(raw):
        errors.append((0, "ANCHOR", f"TOC 引用的锚点 #{slug} 未定义（缺少 <a id=\"{slug}\"> 或对应的纯 ASCII 标题）"))

    for lineno, line in enumerate(lines, 1):

        # 跟踪代码块（``` 开闭）和 <script> 块
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
        if not in_code:
            if re.match(r'<script[\s>]', stripped, re.I):
                in_script = True
            elif re.match(r'</script>', stripped, re.I):
                in_script = False

        # ① # HELP / # TYPE 行含非 ASCII（被误翻）
        if in_code and re.match(r"#\s+(HELP|TYPE)\b", stripped):
            if NON_ASCII.search(stripped):
                errors.append((lineno, "HELP/TYPE", "# HELP / # TYPE 行不应翻译"))

        if not in_code and not in_script:
            # ③ ** 加粗真正失效的精确条件（CommonMark right-flanking 规则）：
            #    closing ** 无法满足 right-flanking 当且仅当：
            #      - 前一字符是 Unicode 标点/符号（category P* or S*）
            #      - 后一字符是 Unicode 字母/数字（category L* or N*，即非空白非标点）
            #    用奇偶计数区分 opening（第1、3、5…个 **）和 closing（第2、4、6…个 **）
            #    先剥掉行内代码，避免 `code **x**` 干扰计数
            clean = re.sub(r'`[^`]*`', lambda m: ' ' * len(m.group()), line)
            parts = clean.split('**')
            for idx in range(1, len(parts)):  # idx=1 是第1个 **, idx=2 是第2个...
                if idx % 2 == 1:
                    continue  # 奇数 = opening，跳过
                # 偶数 = closing
                pre_str = parts[idx - 1]
                post_str = parts[idx]
                if not pre_str or not post_str:
                    continue
                pre_ch = pre_str[-1]
                post_ch = post_str[0]
                pre_cat = unicodedata.category(pre_ch)
                post_cat = unicodedata.category(post_ch)
                if (pre_cat.startswith('P') or pre_cat.startswith('S')) and \
                   (post_cat.startswith('L') or post_cat.startswith('N')):
                    errors.append((lineno, "BOLD",
                        f"闭合 ** 前为标点「{pre_ch}」后为字母「{post_ch}」（加粗失效）：{line.rstrip()}"))
                    break

            # ④ _..._ 斜体在无空格时紧邻非 ASCII 字母（斜体失效）
            #    只报告 _X 或 X_ 中 X 是非 ASCII 字母、且 _ 另一侧也没有空格/标点的情况
            for m in re.finditer(r'(\S)_(\S)', line):
                left, right = m.group(1), m.group(2)
                # 左侧是非 ASCII 字母（不是空白/标点），或右侧是非 ASCII 字母
                left_bad = not left.isascii() and is_unicode_letter(left)
                right_bad = not right.isascii() and is_unicode_letter(right)
                if left_bad or right_bad:
                    if not in_inline_code(line, m.start()):
                        errors.append((lineno, "ITALIC", f"_ 斜体两侧无空格且紧邻非 ASCII 字母（斜体失效）：{line.rstrip()}"))
                        break

            # ⑤ 行内未转义的 HTML 占位符（如 <path>、<var>）
            #    仅报告原文已使用 &lt;tag&gt; 转义写法的情况（即翻译时漏了转义）
            #    含下划线的名称（如 <response_matcher>）是 Caddyfile 语法文档的参数占位符惯例
            #    原文本身就未转义，不属于翻译引入的问题，不报告
            for m in re.finditer(r'<([a-z][a-z0-9_-]*)>', line):
                tag = m.group(1)
                # 跳过合法 HTML 标签
                if tag in {"a", "b", "i", "em", "strong", "code", "pre", "ul", "ol",
                           "li", "p", "div", "span", "img", "table", "thead", "tbody",
                           "tr", "th", "td", "br", "hr", "h1", "h2", "h3", "h4",
                           "aside", "details", "summary", "script", "style", "nav",
                           "article", "section", "header", "footer", "main",
                           "kbd", "abbr", "sup", "sub", "mark", "small", "del", "ins"}:
                    continue
                # 跳过含下划线的参数占位符（Caddyfile 语法文档惯例，原文本身也未转义）
                if '_' in tag:
                    continue
                if in_inline_code(line, m.start()):
                    continue
                errors.append((lineno, "PLACEHOLDER", f"未转义占位符 <{tag}>，应写为 &lt;{tag}&gt;：{line.rstrip()}"))
                break

        if stripped:
            prev_nonempty = line

    return errors


# ── 入口 ──────────────────────────────────────────────────────────────────────

def main():
    if MarkdownIt is None:
        print("缺少依赖：markdown-it-py")
        print("请使用工作区 Python：.venv/bin/python scripts/lint-i18n.py <locale>")
        print("或先安装：python -m pip install markdown-it-py")
        sys.exit(2)

    if len(sys.argv) != 2:
        print("用法：python3 scripts/lint-i18n.py <locale>")
        print(f"可用语种：{', '.join(sorted(os.listdir(I18N_ROOT)))}")
        sys.exit(2)
    locales = [sys.argv[1]]

    total_errors = 0

    for locale in locales:
        md_root = os.path.join(I18N_ROOT, locale, "docs", "markdown")
        if not os.path.isdir(md_root):
            continue

        locale_errors = 0
        for dirpath, _, files in os.walk(md_root):
            for fname in sorted(files):
                if not fname.endswith(".md"):
                    continue
                fpath = os.path.join(dirpath, fname)
                rel = os.path.relpath(fpath, REPO_ROOT)
                errs = check_file(fpath, locale)
                for lineno, code, msg in errs:
                    print(f"[{locale}] {rel}:{lineno} [{code}] {msg}")
                    locale_errors += 1

        if locale_errors:
            print(f"  → {locale}: {locale_errors} 处问题\n")
        else:
            print(f"  → {locale}: OK\n")
        total_errors += locale_errors

    if total_errors:
        print(f"共 {total_errors} 处问题")
        sys.exit(1)
    else:
        print("全部通过")


if __name__ == "__main__":
    main()
