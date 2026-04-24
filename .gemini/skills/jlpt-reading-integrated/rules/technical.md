# Rules: HTML Template & CSV Schema & QC Automation (R9, R10, R11)

> **Scope**: Đọc hiểu tổng hợp (統合理解 / integrated) — **CHỈ N1 & N2**.
> Bài có 2 section A và B (hoặc 3 section 相談者 + 回答者A + 回答者B).

## R9. HTML Template

### R9.1 Standalone HTML template (container 780px, 2-section)

```html
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>[Topic ngắn bằng tiếng Nhật]</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&display=swap');
        body {
            font-family: 'Noto Sans JP', sans-serif;
            background: #f9fafb;
            color: #111827;
            line-height: 1.9;
            word-break: keep-all;
            line-break: strict;
            overflow-wrap: break-word;
            margin: 0;
            padding: 40px 20px;
        }
        .container {
            max-width: 780px;
            margin: 0 auto;
        }
        .passage-a, .passage-b, .consultant {
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 6px;
            padding: 40px 48px 36px 48px;
            font-size: 16px;
            position: relative;
        }
        .passage-a, .consultant { margin-bottom: 24px; }
        .label {
            display: inline-block;
            background: #1e40af;
            color: white;
            font-weight: 700;
            font-size: 0.95em;
            padding: 3px 14px;
            border-radius: 4px;
            margin-bottom: 14px;
        }
        .passage-a p, .passage-b p, .consultant p {
            margin: 0 0 0.9em 0;
            text-indent: 1em;
        }
        .passage-a p:last-child, .passage-b p:last-child, .consultant p:last-child {
            margin-bottom: 0;
        }
        .ellipsis {
            text-align: center;
            font-size: 0.9em;
            color: #6b7280;
            margin: 0.8em 0;
            text-indent: 0;
        }
        .marker { font-weight: bold; color: #1e40af; }
        .annotations {
            margin-top: 1.2em;
            padding-top: 0.8em;
            border-top: 1px dashed #d1d5db;
            font-size: 0.9em;
            color: #374151;
            line-height: 1.7;
        }
        .annotations p { margin: 0.2em 0; text-indent: 0; }
        ruby { ruby-align: center; ruby-position: over; vertical-align: baseline; }
        ruby rt { font-size: 0.55em; color: #374151; letter-spacing: 0.02em; line-height: 1; vertical-align: top; }
        u { text-decoration: underline; text-decoration-thickness: 1.5px; }
    </style>
</head>
<body>
<div class="container">
    <section class="passage-a">
        <span class="label">A</span>
        <p>[Đoạn A — quan điểm 1 về topic. 2-4 paragraph, ~280-380 chars]</p>
    </section>
    <section class="passage-b">
        <span class="label">B</span>
        <p>[Đoạn B — quan điểm 2 về CÙNG topic. 2-4 paragraph, ~280-380 chars]</p>
    </section>
</div>
</body>
</html>
```

### R9.2 Advice format (optional, cho topic tư vấn)

```html
<div class="container">
    <section class="consultant">
        <span class="label">相談者</span>
        <p>[Mô tả vấn đề / nỗi lo của người hỏi]</p>
    </section>
    <section class="passage-a">
        <span class="label">回答者Ａ</span>
        <p>[Lời khuyên 1]</p>
    </section>
    <section class="passage-b">
        <span class="label">回答者Ｂ</span>
        <p>[Lời khuyên 2 — khác góc nhìn]</p>
    </section>
</div>
```

Chú ý: **full-width Ａ / Ｂ** cho nhãn 回答者 (matching data gốc).

### R9.3 Style rules

| Property | Value | Lý do |
|----------|-------|-------|
| Container max-width | **780px** | Rộng vừa cho 2 section stacked vertically |
| Container padding | 40px 20px (body) | Breathing space |
| Section padding | 40px 48px 36px 48px | Padding vừa, label bên trên có spacing |
| Section margin-bottom | 24px | A to B gap |
| Line-height | **1.9** | Readable density cho văn luận thuyết ngắn |
| Font-size | 16px | Standard |
| Label color | #1e40af | Blue navy |

### R9.4 HTML rules CẤM

- **KHÔNG** dùng `<br>` giữa câu — dùng `<p>` thuần
- **KHÔNG** dùng `<table>` cho layout — dùng `<section class="passage-a|b">`
- **KHÔNG** dùng `<span>` ngoài `.marker` và `.label`
- **KHÔNG** dùng inline style (`style="..."`)
- **KHÔNG** source line (đọc hiểu tổng hợp không có source)
- **KHÔNG** tên tác giả có thật hoặc tên báo có thật

---

## R10. Clean HTML Extraction

Khi lưu vào CSV column `text_read`, HTML phải được **clean**:

1. **Strip attributes**: `<p class="..." style="...">` → `<p>`
2. **Keep tags** (cần preserve): `<p>`, `<section>`, `<span class="label">`, `<span class="marker">`, `<u>`, `<ruby>`, `<rt>`
3. **Remove** (nếu có): `<style>`, `<script>`, `<div>` wrapper (nếu có)
4. **Collapse whitespace**: multiple spaces/newlines → 1 space/newline
5. **Preserve structure**: giữ `<section class="passage-a">`, `<section class="passage-b">` để parser CSV hiểu A/B

### Count body chars + A/B balance

```python
from html.parser import HTMLParser
import re

class BodyTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.texts, self.skip_depth, self.in_body = [], 0, False
    def handle_starttag(self, tag, attrs):
        if tag == 'body': self.in_body = True
        if tag in ('rt', 'style', 'script'): self.skip_depth += 1
    def handle_endtag(self, tag):
        if tag in ('rt', 'style', 'script'): self.skip_depth -= 1
    def handle_data(self, d):
        if self.in_body and self.skip_depth == 0: self.texts.append(d)

def count_body_chars(html_string):
    ext = BodyTextExtractor()
    ext.feed(html_string)
    text = ''.join(ext.texts)
    return len(re.sub(r'[ \t\n\r\u3000]', '', text))

def count_section_chars(html_string, section_class):
    """Count chars trong 1 section cụ thể."""
    # Extract section HTML via regex
    pattern = rf'<section class="{section_class}">(.*?)</section>'
    match = re.search(pattern, html_string, re.DOTALL)
    if not match:
        return 0
    return count_body_chars(f"<body>{match.group(1)}</body>")

def ab_balance(html_string):
    a = count_section_chars(html_string, 'passage-a')
    b = count_section_chars(html_string, 'passage-b')
    if max(a, b) == 0:
        return None
    return abs(a - b) / max(a, b)  # 0.30 = 30% imbalance
```

Skip `<rt>`, `<style>`, `<script>`. Remove whitespace: space, tab, newline, full-width space (　).

---

## R11. CSV Schema

45 cột chuẩn từ `rules/question_sheet.csv`.

### R11.1 Core columns

| Column | Value |
|--------|-------|
| `_id` | `{LEVEL}_{uuid32hex}` — unique |
| `level` | `N1` hoặc `N2` (chỉ 2 level) |
| `tag` | Topic tiếng Việt (`AI và đời sống`, `giáo dục trẻ em`, ...) |
| `jp_char_count` | Result `count_body_chars()` (tổng A + B) |
| `kind` | Always `đọc hiểu tổng hợp` |
| `general_audio` | **""** (không audio) |
| `general_image` | **""** (không screenshot) |
| `text_read` | Clean HTML (cả 2 sections, include `<section class="passage-a\|b">`) |
| `text_read_vn` | **""** (optional, để trống) |
| `text_read_en` | **""** (optional, để trống) |

### R11.2 Question columns (2 câu cho cả N1 và N2)

| Column | Slot 1 | Slot 2 | Slots 3-5 |
|--------|--------|--------|-----------|
| `question_label_X` | **`question_comprehensive_understanding`** | **`question_comprehensive_understanding`** | **""** |
| `question_X` | Câu hỏi tiếng Nhật | Câu hỏi tiếng Nhật (compare A vs B) | **""** |
| `question_image_X` | **""** (luôn empty) | **""** | **""** |
| `answer_X` | 4 options `\n`-separated, không prefix | Same format | **""** |
| `correct_answer_X` | `1`\|`2`\|`3`\|`4` (1-based) | Same | **""** |
| `explain_vn_X` | Explain VN 3-part format | Same | **""** |
| `explain_en_X` | Explain EN 3-part format | Same | **""** |

### R11.3 Per-level fill pattern

**Cả N1 và N2**: fill slots 1, 2; empty slots 3, 4, 5.

Pipeline `fill_qa.py` tự clear các slot không dùng.

### R11.4 Label enforcement

**CẢ 2 câu label = `question_comprehensive_understanding`**. Nếu provide label khác → pipeline WARN + override về `question_comprehensive_understanding`.

**Lý do**: đây là `required_question_label` theo `kind_mission_mapping.json`.

### R11.5 CSV field quoting

- CSV dùng default quoting (csv.QUOTE_MINIMAL)
- Fields chứa `,`, `"`, `\n` → tự động quoted và escape
- `answer_X` chứa `\n` → CSV tự quote

---

## R12. QC Automation Checks

### R12.1 HTML check (`check_html()`)

```python
def check_html(path: str, level: str) -> list[str]:
    errors = []
    html = open(path).read()

    # 1. Char count tổng
    chars = count_body_chars(html)
    target = {"N1": (600, 750), "N2": (600, 800)}
    lo, hi = target[level]
    if chars < 570:
        errors.append(f"Total chars {chars} < 570 (HARD REJECT)")
    elif not (lo <= chars <= hi):
        errors.append(f"Total chars {chars} out of {lo}-{hi}")

    # 2. A/B balance
    imbalance = ab_balance(html)
    if imbalance is None:
        errors.append("Missing .passage-a or .passage-b section")
    elif imbalance > 0.30:
        errors.append(f"A/B imbalance {imbalance:.0%} > 30%")

    # 3. Required structure
    if '<section class="passage-a">' not in html and '<section class="passage-a' not in html:
        errors.append("Missing <section class='passage-a'>")
    if '<section class="passage-b">' not in html and '<section class="passage-b' not in html:
        errors.append("Missing <section class='passage-b'>")

    # 4. Required labels
    if '<span class="label">' not in html:
        errors.append("Missing <span class='label'> for A/B")

    # 5. CẤM elements
    if "<br" in html:
        errors.append("Contains <br> — use <p> instead")
    if "<table" in html:
        errors.append("Contains <table> — use <section> instead")
    if "による）" in html or "による)" in html:
        errors.append("Contains source line — not allowed for integrated comprehension")

    # 6. Real name/author check (optional manual check)
    # ...

    return errors
```

### R12.2 CSV row check (`check_csv_row()`)

```python
FIXED_LABEL = "question_comprehensive_understanding"
EXPECTED_Q_COUNT = {"N1": 2, "N2": 2}

def check_csv_row(row: dict) -> list[str]:
    errors = []
    level = row["level"]

    # 1. Level scope
    if level not in EXPECTED_Q_COUNT:
        errors.append(f"Level {level} not in N1/N2")
        return errors

    # 2. Kind
    if row["kind"] != "đọc hiểu tổng hợp":
        errors.append(f"kind='{row['kind']}' ≠ 'đọc hiểu tổng hợp'")

    # 3. general_image must be empty
    if row["general_image"].strip():
        errors.append(f"general_image must be empty")

    # 4. Question count
    expected = EXPECTED_Q_COUNT[level]
    filled = [i for i in range(1, 6) if row.get(f"question_{i}", "").strip()]
    if len(filled) != expected:
        errors.append(f"Level {level} needs {expected} Q, got {len(filled)}")

    # 5. Slots sequential
    if filled != list(range(1, expected + 1)):
        errors.append(f"Q slots must be sequential 1..{expected}")

    # 6. Labels FIXED
    for i in range(1, expected + 1):
        lbl = row.get(f"question_label_{i}", "").strip()
        if lbl != FIXED_LABEL:
            errors.append(f"question_label_{i}='{lbl}' ≠ '{FIXED_LABEL}'")

    # 7. Empty slots cleared
    for i in range(expected + 1, 6):
        for fld in ("question_label_", "question_", "answer_", "correct_answer_",
                    "explain_vn_", "explain_en_"):
            if row.get(f"{fld}{i}", "").strip():
                errors.append(f"{fld}{i} must be empty for level {level}")

    # 8. Answer format (4 options, no prefix)
    for i in range(1, expected + 1):
        ans = row.get(f"answer_{i}", "")
        opts = [x.strip() for x in ans.split("\n") if x.strip()]
        if len(opts) != 4:
            errors.append(f"answer_{i} needs 4 options, got {len(opts)}")
        for j, opt in enumerate(opts, 1):
            if opt[:2].strip() in ("1.", "2.", "3.", "4.") or opt[:1] in "①②③④":
                errors.append(f"answer_{i} option {j} has prefix")

    # 9. correct_answer valid
    for i in range(1, expected + 1):
        ca = row.get(f"correct_answer_{i}", "")
        if ca not in ("1", "2", "3", "4"):
            errors.append(f"correct_answer_{i}='{ca}' not in 1-4")

    return errors
```

### R12.3 Agent bắt buộc chạy QC

- `python3 scripts/process_html.py --validate --html-dir assets/html/doc_hieu_tong_hop` (sau gen HTML)
- `python3 scripts/fill_qa.py --csv sheets/samples_v1.csv --row-id ... --level ... ...` (fill Q&A)

Không được edit CSV tay — pipeline đảm bảo quoting/escape đúng.

---

## R13. File Naming & ID Convention

```python
import uuid
def gen_id(level: str) -> str:
    return f"{level}_{uuid.uuid4().hex}"
```

Regex filename: `^(N1|N2)_[0-9a-fA-F]{8,}$`

Path: `assets/html/doc_hieu_tong_hop/{LEVEL}_{uuid}.html`

## R14. Batch rules

- Batch size: **5 bài/lần** (bài ngắn, structure đơn giản)
- Mỗi batch ≥ 3 bài → topic từ ≥ 2 nhóm khác nhau
- Mỗi batch ≥ 2 bài dùng **format chuẩn** (A/B), 0-1 bài dùng **advice format** (相談者+回答者)
- Kiểu quan hệ A↔B đa dạng: không phải tất cả "contrast", cần mix contrast/complement/debate
