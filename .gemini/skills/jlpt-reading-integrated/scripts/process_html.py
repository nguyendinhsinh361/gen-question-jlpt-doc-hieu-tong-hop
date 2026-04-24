#!/usr/bin/env python3
"""
process_html.py — Pipeline for JLPT "đọc hiểu tổng hợp" (integrated / 統合理解) HTML files.

Đặc trưng dạng đọc hiểu tổng hợp:
  * **2 đoạn riêng biệt A + B** trong CÙNG 1 file HTML (tổng 600–800 chars)
  * **Luôn đúng 2 câu hỏi** / bài cho cả N1 và N2
  * **Mọi câu đều dùng label = `question_comprehensive_understanding`**
    (theo `kind_mission_mapping.json`, required_question_label = cố định)
  * Test **so sánh / tổng hợp** quan điểm của A và B

Does three things — NO screenshot:
  1. Count visible body characters (JLPT standard)
  2. Extract clean HTML (no attributes / no <rt> text / collapsed whitespace)
  3. Append / update rows in the 45-column question_sheet.csv
     — populates 2 câu hỏi (cả N1 và N2), label cố định

This skill applies only to N1 and N2. Other levels are rejected với UNSUPPORTED_LEVEL.

Usage
-----
# Count chars only
python3 process_html.py --count-only --file assets/html/doc_hieu_tong_hop/N1_abcdef.html

# Validate Target Range + A/B structure
python3 process_html.py --validate --html-dir assets/html/doc_hieu_tong_hop

# Full pipeline — RECOMMENDED: JSON file cho 2 questions
python3 process_html.py \
    --file assets/html/doc_hieu_tong_hop/N1_abcdef.html \
    --csv sheets/samples_v1.csv \
    --tag "xã luận giáo dục" \
    --questions-json /tmp/qs.json

# Full pipeline — CLI flags (2 câu per bài, cùng label)
python3 process_html.py \
    --file assets/html/doc_hieu_tong_hop/N1_abcdef.html \
    --csv sheets/samples_v1.csv \
    --tag "xã luận giáo dục" \
    --q1 "AとBで共通して述べられていることは何か。" --a1 "A|B|C|D" --c1 2 --ev1 "..." --ee1 "..." \
    --q2 "XについてAとBはどのように述べているか。" --a2 "A|B|C|D" --c2 3 --ev2 "..." --ee2 "..."

# (label mặc định = question_comprehensive_understanding cho cả 2 câu,
#  không cần set --q1-label / --q2-label trừ khi muốn override)

# Refresh char count + text_read (giữ câu hỏi)
python3 process_html.py --refresh --html-dir assets/html/doc_hieu_tong_hop --csv sheets/samples_v1.csv

Questions JSON format
---------------------
{
  "questions": [
    {
      "label": "question_comprehensive_understanding",   // auto-default nếu thiếu
      "question": "AとBで共通して述べられていることは何か。",
      "answers": ["選択肢A", "選択肢B", "選択肢C", "選択肢D"],
      "correct": 2,
      "explain_vn": "...",
      "explain_en": "..."
    },
    { ... 1 more với cùng label ... }
  ]
}
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

# ── Constants ───────────────────────────────────────────────────────

KIND = "đọc hiểu tổng hợp"

# Target ranges (P25–P75 của data mẫu + spec chính thức).
# Chỉ N1 & N2 — N3/N4/N5 không có kind này.
# Data N1: min=600, p25=626, p50=652, p75=697, avg=665, max=804
# Data N2: min=604, p25=615, p50=644, p75=778, avg=705, max=1021
TARGET_RANGE = {
    "N1": (600, 750),
    "N2": (600, 800),
}
HARD_REJECT = {
    "N1": 570,
    "N2": 570,
}
# Số câu hỏi chuẩn per level (từ rules/question_format.json — cả N1 và N2 đều 2)
EXPECTED_Q_COUNT = {
    "N1": 2,
    "N2": 2,
}

# Label BẮT BUỘC cho mọi câu hỏi (từ rules/kind_mission_mapping.json)
REQUIRED_QUESTION_LABEL = "question_comprehensive_understanding"

CSV_FIELDNAMES = [
    "_id", "level", "tag", "jp_char_count", "kind", "general_audio", "general_image",
    "text_read", "text_read_vn", "text_read_en",
    "question_label_1", "question_1", "question_image_1", "answer_1", "correct_answer_1", "explain_vn_1", "explain_en_1",
    "question_label_2", "question_2", "question_image_2", "answer_2", "correct_answer_2", "explain_vn_2", "explain_en_2",
    "question_label_3", "question_3", "question_image_3", "answer_3", "correct_answer_3", "explain_vn_3", "explain_en_3",
    "question_label_4", "question_4", "question_image_4", "answer_4", "correct_answer_4", "explain_vn_4", "explain_en_4",
    "question_label_5", "question_5", "question_image_5", "answer_5", "correct_answer_5", "explain_vn_5", "explain_en_5",
]

FILENAME_RE = re.compile(r"^(N[1-5])_([0-9a-fA-F]{8,})$")


# ── Character Counting ──────────────────────────────────────────────

class BodyTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.texts: list[str] = []
        self.skip_depth = 0
        self.in_body = False

    def handle_starttag(self, tag, attrs):
        if tag == "body":
            self.in_body = True
        if tag in ("rt", "style", "script"):
            self.skip_depth += 1

    def handle_endtag(self, tag):
        if tag in ("rt", "style", "script"):
            self.skip_depth -= 1

    def handle_data(self, d):
        if self.in_body and self.skip_depth == 0:
            self.texts.append(d)


def count_body_chars(html_string: str) -> int:
    ext = BodyTextExtractor()
    ext.feed(html_string)
    text = "".join(ext.texts)
    return len(re.sub(r"[ \t\n\r\u3000]", "", text))


# ── A/B Section Counter (per-section chars) ─────────────────────────

class SectionCharCounter(HTMLParser):
    """
    Count visible chars inside each <section class="passage-a"> / <section class="passage-b">
    block. Fallback: track divs / sections with id ="A"/"B" hoặc class chứa "passage-a"/"passage-b".

    Nếu HTML dùng pattern legacy <p>A</p><p>...text A...</p><p>B</p><p>...text B...</p>
    thì vẫn đo được bằng cách detect label `A` / `B` đơn độc trong <p>.
    """

    def __init__(self):
        super().__init__()
        # Stack of dicts {label: 'A'|'B', depth: int, active: bool}
        self.stack: list[dict] = []
        self.chars_a = 0
        self.chars_b = 0
        self.depth = 0
        self.skip_depth = 0
        # For legacy <p>A</p> / <p>B</p> detection:
        self.legacy_label: str | None = None   # 'A' or 'B' currently active paragraph sequence
        self.in_legacy_label_p = False
        self.pending_legacy: str | None = None

    def _section_label(self, attrs) -> str | None:
        adict = dict(attrs)
        cls = adict.get("class", "")
        sid = adict.get("id", "")
        if "passage-a" in cls or sid.lower() == "a":
            return "A"
        if "passage-b" in cls or sid.lower() == "b":
            return "B"
        return None

    def handle_starttag(self, tag, attrs):
        self.depth += 1
        if tag in ("rt", "style", "script"):
            self.skip_depth += 1
            return
        if tag in ("section", "div", "article"):
            lbl = self._section_label(attrs)
            if lbl:
                self.stack.append({"label": lbl, "depth": self.depth})
                self.legacy_label = None  # reset legacy when proper section starts
                return
        if tag == "p" and not self.stack:
            # Only enter legacy-label mode khi KHÔNG nằm trong một proper section —
            # tránh nuốt nội dung <p> chính trong <section class="passage-a/b">.
            # Could be legacy <p>A</p> / <p>B</p> marker
            self.in_legacy_label_p = True
            self.pending_legacy = ""

    def handle_endtag(self, tag):
        if tag in ("rt", "style", "script"):
            self.skip_depth -= 1
        if tag in ("section", "div", "article") and self.stack:
            if self.stack[-1]["depth"] == self.depth:
                self.stack.pop()
        if tag == "p" and self.in_legacy_label_p:
            t = (self.pending_legacy or "").strip()
            if t in ("A", "Ａ", "B", "Ｂ"):
                self.legacy_label = "A" if t in ("A", "Ａ") else "B"
            self.in_legacy_label_p = False
            self.pending_legacy = None
        self.depth -= 1

    def handle_data(self, data):
        if self.skip_depth > 0:
            return
        clean = re.sub(r"[ \t\n\r\u3000]", "", data)
        # Legacy <p>A</p> accumulator — counts label text but NOT into A/B body
        if self.in_legacy_label_p:
            self.pending_legacy = (self.pending_legacy or "") + data
            # But legacy label of 1 char should NOT be counted into body chars either
            # If not exactly the label, flush through as normal text later via end-tag path.
            # We simply return here — will reconsider in handle_endtag.
            return
        # If inside a proper <section>
        if self.stack:
            active_label = self.stack[-1]["label"]
            if active_label == "A":
                self.chars_a += len(clean)
            elif active_label == "B":
                self.chars_b += len(clean)
            return
        # Else, fall back to legacy label
        if self.legacy_label == "A":
            self.chars_a += len(clean)
        elif self.legacy_label == "B":
            self.chars_b += len(clean)


def count_section_chars(html_string: str) -> tuple[int, int]:
    """Return (chars_a, chars_b). 0 0 nếu không detect được A/B section."""
    ext = SectionCharCounter()
    ext.feed(html_string)
    return ext.chars_a, ext.chars_b


# ── Clean HTML Extraction ───────────────────────────────────────────

class CleanHTMLExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.result: list[str] = []
        self.skip_depth = 0
        self.in_body = False
        self.body_done = False

    def handle_starttag(self, tag, attrs):
        if tag == "body":
            self.in_body = True
            return
        if not self.in_body or self.body_done:
            return
        if tag in ("style", "script", "rt"):
            self.skip_depth += 1
            return
        if self.skip_depth > 0:
            return
        self.result.append(f"<{tag}>")

    def handle_startendtag(self, tag, attrs):
        if not self.in_body or self.body_done or self.skip_depth > 0:
            return
        if tag in ("style", "script", "rt"):
            return
        self.result.append(f"<{tag}>")

    def handle_endtag(self, tag):
        if tag == "body":
            self.body_done = True
            return
        if not self.in_body or self.body_done:
            return
        if tag in ("style", "script", "rt"):
            self.skip_depth -= 1
            return
        if self.skip_depth > 0:
            return
        self.result.append(f"</{tag}>")

    def handle_data(self, data):
        if not self.in_body or self.body_done or self.skip_depth > 0:
            return
        self.result.append(data)


def clean_html(full_html: str) -> str:
    ext = CleanHTMLExtractor()
    ext.feed(full_html)
    raw = "".join(ext.result)
    raw = re.sub(r"\s+", " ", raw)
    raw = re.sub(r"\s*<", "<", raw)
    raw = re.sub(r">\s*", ">", raw)
    raw = re.sub(r"<(\w+)></\1>", "", raw)
    return raw.strip()


# ── Filename / ID helpers ───────────────────────────────────────────

def parse_filename(path: str) -> tuple[str | None, str]:
    stem = Path(path).stem
    m = FILENAME_RE.match(stem)
    if m:
        return m.group(1).upper(), stem
    return None, stem


# ── Validation ──────────────────────────────────────────────────────

def classify_char_count(level: str | None, chars: int) -> str:
    if level not in TARGET_RANGE:
        # N3/N4/N5 không có đọc hiểu tổng hợp
        return "UNSUPPORTED_LEVEL"
    lo, hi = TARGET_RANGE[level]
    hard = HARD_REJECT[level]
    if chars < hard:
        return "HARD_REJECT"
    if chars < lo:
        return "UNDER_TARGET"
    if chars > hi + 100:
        return "OVER_TARGET"
    return "OK"


def classify_ab_balance(chars_a: int, chars_b: int) -> tuple[str, float]:
    """Return (status, ratio). ratio = |a - b| / max(a, b)."""
    if chars_a == 0 and chars_b == 0:
        return "AB_UNDETECTED", 0.0
    if chars_a == 0 or chars_b == 0:
        return "AB_MISSING", 1.0
    bigger = max(chars_a, chars_b)
    ratio = abs(chars_a - chars_b) / bigger if bigger else 0.0
    if ratio > 0.30:
        return "AB_IMBALANCE", ratio
    return "AB_OK", ratio


def validate_file(html_path: str) -> dict:
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()
    level, name = parse_filename(html_path)
    chars = count_body_chars(html)
    chars_a, chars_b = count_section_chars(html)
    status = classify_char_count(level, chars)
    ab_status, ab_ratio = classify_ab_balance(chars_a, chars_b)
    target = TARGET_RANGE.get(level) if level else None
    return {
        "file": html_path,
        "name": name,
        "level": level,
        "chars": chars,
        "chars_a": chars_a,
        "chars_b": chars_b,
        "ab_status": ab_status,
        "ab_ratio": ab_ratio,
        "target": target,
        "status": status,
    }


# ── Question helpers ────────────────────────────────────────────────

def format_answers(answers: list[str]) -> str:
    # R6.1: 4 options newline-separated, KHÔNG prefix ("1.", "①", "1)", ...)
    return "\n".join(a.strip() for a in answers)


def parse_answers_pipe(pipe_string: str) -> list[str]:
    return [s.strip() for s in pipe_string.split("|")]


def _normalize_label(raw: str | None) -> str:
    """Default về `question_comprehensive_understanding` nếu rỗng."""
    if not raw:
        return REQUIRED_QUESTION_LABEL
    return raw


def validate_question_list(level: str | None, questions: list[dict]) -> list[str]:
    """Return list of warnings. Non-empty = có vấn đề."""
    warnings = []
    expected = EXPECTED_Q_COUNT.get(level, None)
    actual = len(questions)
    if level not in EXPECTED_Q_COUNT:
        warnings.append(f"Level {level} không thuộc scope đọc hiểu tổng hợp (chỉ N1/N2).")
    elif actual != expected:
        warnings.append(f"Số câu hỏi là {actual}, nhưng level {level} yêu cầu {expected}.")
    for i, q in enumerate(questions, 1):
        if not q.get("question"):
            warnings.append(f"Q{i}: thiếu `question`")
        label = q.get("label") or ""
        if label and label != REQUIRED_QUESTION_LABEL:
            warnings.append(
                f"Q{i}: label={label!r} — đọc hiểu tổng hợp yêu cầu label cố định "
                f"{REQUIRED_QUESTION_LABEL!r} (sẽ bị override)."
            )
        ans = q.get("answers", [])
        if len(ans) != 4:
            warnings.append(f"Q{i}: phải có đúng 4 đáp án (hiện {len(ans)})")
        correct = q.get("correct")
        if not (isinstance(correct, int) and 1 <= correct <= 4):
            warnings.append(f"Q{i}: `correct` phải là int 1-4 (hiện {correct!r})")
        if not q.get("explain_vn"):
            warnings.append(f"Q{i}: thiếu `explain_vn`")
        if not q.get("explain_en"):
            warnings.append(f"Q{i}: thiếu `explain_en`")
    # Check 2 câu không trùng nhau
    if actual >= 2:
        q_texts = [q.get("question", "").strip() for q in questions]
        if len(set(q_texts)) < len(q_texts):
            warnings.append("Có câu hỏi trùng nhau — 'Các câu gen ra không được trùng nhau'.")
    return warnings


# ── CSV Operations ──────────────────────────────────────────────────

def empty_row() -> dict:
    return {field: "" for field in CSV_FIELDNAMES}


def build_csv_row(
    html_path: str,
    *,
    tag: str = "",
    questions: list[dict] = None,
) -> tuple[dict, list[str]]:
    """Build row + return (row, warnings)."""
    with open(html_path, "r", encoding="utf-8") as f:
        full_html = f.read()
    level, name = parse_filename(html_path)
    if level is None:
        raise ValueError(
            f"Filename '{Path(html_path).name}' không đúng format {{LEVEL}}_{{uuid32hex}}.html"
        )
    char_count = count_body_chars(full_html)
    cleaned = clean_html(full_html)

    row = empty_row()
    row.update({
        "_id": name,
        "level": level,
        "tag": tag,
        "jp_char_count": str(char_count),
        "kind": KIND,
        "general_audio": "",
        "general_image": "",
        "text_read": cleaned,
        "text_read_vn": "",
        "text_read_en": "",
    })

    questions = questions or []
    warnings = validate_question_list(level, questions) if questions else []

    for i, q in enumerate(questions, 1):
        if i > 5:
            warnings.append(f"Bỏ qua Q{i}: CSV chỉ hỗ trợ tối đa 5 câu.")
            break
        # Force label = question_comprehensive_understanding (spec bắt buộc)
        row[f"question_label_{i}"] = REQUIRED_QUESTION_LABEL
        row[f"question_{i}"] = q.get("question", "")
        row[f"question_image_{i}"] = ""
        ans = q.get("answers", []) or []
        row[f"answer_{i}"] = format_answers(ans) if ans else ""
        correct = q.get("correct", "")
        row[f"correct_answer_{i}"] = str(correct) if correct != "" else ""
        row[f"explain_vn_{i}"] = q.get("explain_vn", "")
        row[f"explain_en_{i}"] = q.get("explain_en", "")

    return row, warnings


def load_csv(csv_path: str) -> list[dict]:
    if not os.path.exists(csv_path):
        return []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def write_csv(csv_path: str, rows: list[dict]) -> None:
    os.makedirs(os.path.dirname(csv_path) or ".", exist_ok=True)
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in CSV_FIELDNAMES})


def upsert_row(existing: list[dict], new_row: dict) -> list[dict]:
    key = new_row.get("_id", "")
    for i, row in enumerate(existing):
        if row.get("_id", "") == key and key:
            existing[i] = new_row
            return existing
    existing.append(new_row)
    return existing


def refresh_row(existing_row: dict, html_path: str) -> dict:
    with open(html_path, "r", encoding="utf-8") as f:
        full_html = f.read()
    chars = count_body_chars(full_html)
    cleaned = clean_html(full_html)
    existing_row["jp_char_count"] = str(chars)
    existing_row["kind"] = KIND
    existing_row["text_read"] = cleaned
    existing_row["general_image"] = ""
    return existing_row


# ── Question collection (CLI flags → questions list) ────────────────

def collect_questions_from_cli(args) -> list[dict]:
    """Extract questions from --q1/--q1-label/--a1/--c1/--ev1/--ee1 flags (up to q5).
    Note: --qN-label is optional vì đọc hiểu tổng hợp có label cố định duy nhất."""
    questions = []
    for i in range(1, 6):
        q_text = getattr(args, f"q{i}", None)
        q_label = getattr(args, f"q{i}_label", None)
        if not q_text and not q_label:
            continue
        ans_pipe = getattr(args, f"a{i}", "") or ""
        correct = getattr(args, f"c{i}", None)
        ev = getattr(args, f"ev{i}", "") or ""
        ee = getattr(args, f"ee{i}", "") or ""
        questions.append({
            "label": _normalize_label(q_label),
            "question": q_text or "",
            "answers": parse_answers_pipe(ans_pipe) if ans_pipe else [],
            "correct": int(correct) if correct is not None else None,
            "explain_vn": ev,
            "explain_en": ee,
        })
    return questions


def load_questions_json(path: str) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    qs = data.get("questions") if isinstance(data, dict) else data
    if not isinstance(qs, list):
        raise ValueError(f"Invalid questions JSON: {path} — expected list or {{\"questions\": [...]}}")
    return qs


# ── CLI modes ───────────────────────────────────────────────────────

def _fmt_ab(info: dict) -> str:
    a, b = info["chars_a"], info["chars_b"]
    if a == 0 and b == 0:
        return "A/B=?"
    return f"A={a} B={b}"


def cmd_count(files: list[str]) -> int:
    print(f"Counting {len(files)} file(s)...\n")
    any_hard_reject = False
    for f in files:
        info = validate_file(f)
        marker = ""
        status = info["status"]
        if status == "HARD_REJECT":
            marker = "  🚫 HARD REJECT"
            any_hard_reject = True
        elif status == "UNDER_TARGET":
            marker = "  ⚠️  UNDER TARGET"
        elif status == "OVER_TARGET":
            marker = "  ⚠️  OVER TARGET"
        elif status == "UNSUPPORTED_LEVEL":
            marker = "  ❌ UNSUPPORTED (chỉ N1/N2)"
        tgt = f"target {info['target'][0]}-{info['target'][1]}" if info["target"] else ""
        print(f"  {info['name']}: {info['chars']} chars [{info['level']}] {tgt} ({_fmt_ab(info)}){marker}")
    return 1 if any_hard_reject else 0


def cmd_validate(files: list[str]) -> int:
    print(f"Validating {len(files)} file(s)...\n")
    fails = 0
    for f in files:
        info = validate_file(f)
        ok = info["status"] == "OK"
        ab_ok = info["ab_status"] == "AB_OK"
        status = info["status"]
        ab_status = info["ab_status"]
        if status == "HARD_REJECT":
            badge = "🚫"
        elif status == "UNSUPPORTED_LEVEL":
            badge = "❌"
        elif not ok:
            badge = "⚠️ "
        else:
            badge = "✅"
        tgt = f"target {info['target'][0]}-{info['target'][1]}" if info["target"] else "target ?"
        ab_note = ""
        if ab_status == "AB_UNDETECTED":
            ab_note = " [A/B không phát hiện]"
        elif ab_status == "AB_MISSING":
            ab_note = " [thiếu 1 trong 2 đoạn A/B]"
        elif ab_status == "AB_IMBALANCE":
            ab_note = f" [A/B chênh {int(info['ab_ratio']*100)}% > 30%]"
        print(
            f"  {badge} {info['name']}: {info['chars']} chars [{info['level']}] {tgt} "
            f"({_fmt_ab(info)}) — {status}{ab_note}"
        )
        if not ok or not ab_ok:
            fails += 1
    print(f"\n{len(files) - fails}/{len(files)} files OK.")
    return 1 if fails else 0


def cmd_refresh(files: list[str], csv_path: str) -> None:
    rows = load_csv(csv_path)
    by_id = {r.get("_id", ""): r for r in rows}
    updated, added, skipped = 0, 0, 0
    for f in files:
        level, name = parse_filename(f)
        if level is None:
            print(f"  [skip] {Path(f).name} — filename không hợp lệ")
            skipped += 1
            continue
        if level not in TARGET_RANGE:
            # N3/N4/N5 không có kind đọc hiểu tổng hợp — không commit.
            print(f"  [skip] {Path(f).name} — UNSUPPORTED_LEVEL ({level}), chỉ N1/N2.")
            skipped += 1
            continue
        if name in by_id:
            refresh_row(by_id[name], f)
            updated += 1
        else:
            row, _ = build_csv_row(f)
            rows.append(row)
            added += 1
    write_csv(csv_path, rows)
    print(
        f"Refreshed {updated} existing row(s), added {added} new row(s), "
        f"skipped {skipped} → {csv_path}"
    )


def cmd_single_full(args) -> None:
    questions = []
    if args.questions_json:
        questions = load_questions_json(args.questions_json)
        # Auto-fill label mặc định cho mỗi câu thiếu label
        for q in questions:
            q["label"] = _normalize_label(q.get("label"))
    else:
        questions = collect_questions_from_cli(args)

    if not questions:
        print("⚠️  Không có question nào (cần --questions-json hoặc --q1/--q2/...).", file=sys.stderr)
        sys.exit(2)

    row, warnings = build_csv_row(args.file, tag=args.tag or "", questions=questions)

    level = row["level"]
    chars = int(row["jp_char_count"])
    status = classify_char_count(level, chars)

    info = validate_file(args.file)
    ab_status = info["ab_status"]
    chars_a, chars_b = info["chars_a"], info["chars_b"]

    if warnings:
        print("⚠️  Warnings:")
        for w in warnings:
            print(f"   - {w}")

    if status == "UNSUPPORTED_LEVEL":
        print(f"❌ {row['_id']}: level {level} không thuộc đọc hiểu tổng hợp (chỉ N1/N2). Không commit.")
        sys.exit(1)
    if status == "HARD_REJECT":
        print(f"🚫 {row['_id']}: {chars} chars — dưới Hard Reject ({HARD_REJECT[level]}). GEN LẠI, không commit CSV.")
        sys.exit(1)
    if status == "UNDER_TARGET":
        print(f"⚠️  {row['_id']}: {chars} chars — dưới Target Range {TARGET_RANGE[level]}. Cân nhắc bổ sung.")

    if ab_status == "AB_UNDETECTED":
        print(f"⚠️  A/B không detect được (cần <section class='passage-a'>…</section> hoặc <p>A</p>/<p>B</p>).")
    elif ab_status == "AB_MISSING":
        print(f"⚠️  Thiếu 1 đoạn: A={chars_a} B={chars_b}. Cần cả 2 đoạn A và B.")
    elif ab_status == "AB_IMBALANCE":
        print(f"⚠️  A/B chênh lệch {int(info['ab_ratio']*100)}% > 30%: A={chars_a} B={chars_b}. Cân nhắc cân bằng.")

    rows = load_csv(args.csv)
    rows = upsert_row(rows, row)
    write_csv(args.csv, rows)
    expected_q = EXPECTED_Q_COUNT.get(level, "?")
    print(
        f"✅ Upserted {row['_id']} ({chars} chars A={chars_a}/B={chars_b}, "
        f"{level}, {len(questions)} câu — expected {expected_q}) → {args.csv}"
    )


def collect_files(args) -> list[str]:
    if args.file:
        return [args.file]
    if args.html_dir:
        return sorted(
            os.path.join(args.html_dir, f)
            for f in os.listdir(args.html_dir)
            if f.endswith(".html")
        )
    print("Provide --file or --html-dir", file=sys.stderr)
    sys.exit(2)


def main():
    ap = argparse.ArgumentParser(
        description="Process JLPT 'đọc hiểu tổng hợp' HTML files (no screenshot, 2 questions, N1+N2 only, 2 sections A+B).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--file", help="Single HTML file")
    ap.add_argument("--html-dir", help="Directory with HTML files")
    ap.add_argument("--csv", default="sheets/samples_v1.csv", help="CSV file path")

    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--count-only", action="store_true")
    mode.add_argument("--validate", action="store_true")
    mode.add_argument("--refresh", action="store_true")

    ap.add_argument("--tag", help="Topic tag")
    ap.add_argument("--questions-json", help="Path to JSON file with questions array")

    for i in range(1, 6):
        ap.add_argument(f"--q{i}-label", dest=f"q{i}_label",
                        help=f"question_label_{i} (mặc định = {REQUIRED_QUESTION_LABEL})")
        ap.add_argument(f"--q{i}", dest=f"q{i}",
                        help=f"Câu hỏi {i} tiếng Nhật")
        ap.add_argument(f"--a{i}", dest=f"a{i}",
                        help=f"Answer {i}: 4 đáp án ngăn cách |")
        ap.add_argument(f"--c{i}", dest=f"c{i}", type=int,
                        help=f"Correct {i}: 1-4")
        ap.add_argument(f"--ev{i}", dest=f"ev{i}",
                        help=f"Explain VN {i}")
        ap.add_argument(f"--ee{i}", dest=f"ee{i}",
                        help=f"Explain EN {i}")

    args = ap.parse_args()
    files = collect_files(args)

    if args.count_only:
        sys.exit(cmd_count(files))
    if args.validate:
        sys.exit(cmd_validate(files))
    if args.refresh:
        cmd_refresh(files, args.csv)
        return

    if args.file and (args.questions_json or any(getattr(args, f"q{i}", None) for i in range(1, 6))):
        cmd_single_full(args)
        return

    if args.html_dir and not args.file:
        print("⚠️  Chạy --html-dir mà không có mode. Mặc định count.\n")
        sys.exit(cmd_count(files))
    sys.exit(cmd_count(files))


if __name__ == "__main__":
    main()
