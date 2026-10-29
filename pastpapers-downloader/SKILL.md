---
name: pastpapers-downloader
description: Use when downloading CAIE A-Level past papers (QP/MS/ER/CI/GT). Batch-fetch PDFs from pastpapers.co with studyhatch fallback.
---

# PastPapers Downloader — CAIE A-Level 试卷批量下载

批量下载 CAIE A-Level 试卷：Question Paper (qp)、Mark Scheme (ms)、Examiner Report (er)、Confidential Instructions (ci)、Grade Thresholds (gt)。

## 触发场景
"下载试卷 / 下载 past papers / 要 9702 2023 的 QP 和 MS / 批量下载某科某考季"。

## 关键事实（2026-09-24 实测，覆盖旧版说明）

1. **文件名规则**（旧版 `9702-physics-june-2023-question-paper-33.pdf` 是错的，会 404）：
   `{syllabus}_{s|w|m}{yy}_{type}_{paper}{variant}.pdf`
   例：`9702_s23_qp_33.pdf`、`9701_s24_ms_22.pdf`、`9618_w23_qp_11.pdf`
   - s = May/June，w = Oct/Nov，m = Feb/March；`33` = Paper 3 Variant 3
2. **pastpapers.co 的 `/api/file/...?download=1` 必须带 cookie**：先 GET 一次该科目考季页
   (`https://pastpapers.co/caie/a-level/{slug}/{session}/`) 拿 session cookie，再用同一 cookie jar 请求文件；
   否则返回的是 HTML 查看页（HTTP 200 + text/html），不是 PDF。同时带 UA + Referer。
3. **目录 slug**（括号原样保留，**不要** URL 编码）：
   - 9702 physics-9702 ｜ 9701 chemistry-9701 ｜ 9709 mathematics-9709
   - 9231 mathematics-further-9231 ｜ 9618 `computer-science-(for-first-examination-in-2021)-(9618)`
4. **考季 slug**：`2023-may-june`、`2023-october-november`、`2024-february-march`
5. **不存在 ≠ 脚本坏了**：9702/33、9702/52 这类实验卷只在 May/June 有，Oct/Nov 请求 w23_qp_33 返回 404 属正常。
6. **备用源**（无需 cookie）：`https://studyhatch.com/Past-Papers/PDFs/CIE_AL/{code}/{year}/{MJ|ON|FM}/{name}`
   —— 注意目录用 MJ/ON/FM 而文件名仍用 s/w/m；必须跟随重定向（urllib 默认跟随；curl 要加 `-L`，不加会 404）。

## 用法

```bash
python scripts/download_papers.py --subject 9702 --session 2023-may-june \
    --combos 33 11 12 --types qp ms --out "C:/Users/da_shan/AppData/Local/hermes/workspace/学习资料/9702_2023_MJ"
```
- `--combos`：卷号+变体号，如 `11 12 13 21 22 23 31 32 33 41 42 43 51 52 53`
- `--types`：`qp ms er ci gt`（默认 `qp ms`）
- `--source auto`（默认）：先 pastpapers.co，失败的文件自动用 studyhatch 补下

## 铁律

1. **先下 1 个文件确认拿到 `%PDF`，再批量**（不要盲下 40 个链接）。
2. **落盘后校验**：以 `%PDF` 开头且 > 50 KB。200 + text/html 是伪装成功的最常见坑。
3. 单个文件 404 不要重试——先判断该考季是否真有这一卷。
4. 下载完把 PDF 归到 workspace 的归档目录（如 `archive/<科目>/` 或 `学习资料/<科目>_<年>_<季>/`），不要散落在桌面或临时目录。
5. 需要 QP+MS 才算一套；只发 QP 给用户前先确认对方是否需要 MS。

## 手工命令（脚本不可用时）

```bash
cd "$TMPDIR" && rm -f cj.txt
curl -s -c cj.txt -o /dev/null -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126" \
  "https://pastpapers.co/caie/a-level/physics-9702/2023-may-june/"
curl -sL -b cj.txt -c cj.txt -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126" \
  -e "https://pastpapers.co/caie/a-level/physics-9702/2023-may-june/" -o 9702_s23_qp_33.pdf \
  "https://pastpapers.co/api/file/caie/a-level/physics-9702/2023-may-june/9702_s23_qp_33.pdf?download=1"
file 9702_s23_qp_33.pdf   # 必须显示 PDF document
```

## 竞赛试卷下载补充（AMC 等非 CAIE 试卷）

适用于用户指定竞赛名称、年份/场次并要求下载可打印试题 PDF 的场景；不强行套用 CAIE 文件命名或站点规则。

1. **先找可核验的原始/授权 PDF**：优先竞赛主办方，其次明确注明许可/转载来源的竞赛资源站；用搜索结果交叉确认竞赛年份、场次和文档类型（题目卷 vs 答案/解析）。
2. **先单份下载验证**：用 `curl -fL` 跟随重定向，输出到 workspace 的归档目录；路径交给 curl 时使用 Windows 原生正斜杠绝对路径（如 `C:/Users/...`），避免 MSYS 把 `$PWD`/中文目录拆错。文件名和目录尽量 ASCII。
3. **验证内容而非只看 HTTP 成功**：`file <path>` 应识别为 PDF；文件头应为 `%PDF-`，文件大小合理；如有 PDF 工具，再核对页数/标题。若是 HTML 错误页或下载结果异常，不要交付。
4. **题目与答案分离**：用户要计时摸底时只下载/发题目卷，不附答案和解析；需要答案时另行明确提供。
5. **归档与交付**：建议放 `workspace/archive/contest_papers/`，用含竞赛、年份/场次、文档类型的文件名；回复提供本地文件链接，并简述已验证的文件类型/页数。
6. **批量下载前先确认清单**：逐个确认竞赛、年份/场次、卷别及是否需要答案/解析；先下载一个样本验证源站和命名，再批量执行并逐文件核验。

## 更新记录
- 2026-09-24：重写。修正文件名规则（旧版用 `9702-physics-june-2023-question-paper-33.pdf`，实测 404）；补充 cookie 前置、studyhatch 备用源、卷次可用性规则；新增经验证的 `scripts/download_papers.py`（9702/9701/9709/9231/9618 多考季实测通过）。
- 2026-09-10：初版。
