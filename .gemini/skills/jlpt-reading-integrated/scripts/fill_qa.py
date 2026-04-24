#!/usr/bin/env python3
"""
Fill Q&A data vào CSV một cách an toàn cho đọc hiểu tổng hợp (multi-question 2 câu) —
tự động handle comma, newline, quoting. Agent BẮT BUỘC dùng script này, không edit
CSV bằng tay.

Đọc hiểu tổng hợp (統合理解 / integrated) có 2 câu hỏi per bài (CHỈ N1 & N2):
    - N1: 2 câu  → populate question_{1,2}, empty question_{3,4,5}
          Q1 + Q2 ĐỀU là `question_comprehensive_understanding` (FIXED LABEL)
          Q2 BẮT BUỘC test so sánh A vs B (compare/integrate viewpoints)
    - N2: 2 câu  → populate question_{1,2}, empty question_{3,4,5}
          Q1 + Q2 ĐỀU là `question_comprehensive_understanding` (FIXED LABEL)
          Q2 BẮT BUỘC test so sánh A vs B (compare/integrate viewpoints)

Usage (ví dụ N1 — 2 câu):
    python3 fill_qa.py \\
        --csv sheets/samples_v1.csv \\
        --row-id N1_abc123 \\
        --level N1 \\
        --q1 "AとBで共通して述べられているのはどれか。" \\
        --a1 "選択肢1
選択肢2
選択肢3
選択肢4" \\
        --ca1 2 \\
        --evn1 "..." \\
        --een1 "..." \\
        --q2 "XについてAとBはどのように述べているか。" \\
        --a2 "A\\nB\\nC\\nD" \\
        --ca2 3 --evn2 "..." --een2 "..."

LABEL RULE:
    - CẢ Q1 và Q2 luôn là `question_comprehensive_understanding` (FIXED)
    - Flag `--qN-label` là OPTIONAL; nếu bỏ qua, script tự điền FIXED_LABEL
    - Nếu có `--qN-label` và KHÔNG khớp FIXED_LABEL → script warn + override
"""
import argparse
import csv
import os
import sys

CSV_FIELDNAMES = [
    "_id", "level", "tag", "jp_char_count", "kind", "general_audio", "general_image",
    "text_read", "text_read_vn", "text_read_en",
    "question_label_1", "question_1", "question_image_1", "answer_1", "correct_answer_1", "explain_vn_1", "explain_en_1",
    "question_label_2", "question_2", "question_image_2", "answer_2", "correct_answer_2", "explain_vn_2", "explain_en_2",
    "question_label_3", "question_3", "question_image_3", "answer_3", "correct_answer_3", "explain_vn_3", "explain_en_3",
    "question_label_4", "question_4", "question_image_4", "answer_4", "correct_answer_4", "explain_vn_4", "explain_en_4",
    "question_label_5", "question_5", "question_image_5", "answer_5", "correct_answer_5", "explain_vn_5", "explain_en_5",
]

# Đọc hiểu tổng hợp — LABEL CỐ ĐỊNH duy nhất cho toàn bộ câu hỏi (spec JLPT)
FIXED_LABEL = "question_comprehensive_understanding"

# Đọc hiểu tổng hợp CHỈ có N1 và N2 (spec JLPT không có N3/N4/N5)
EXPECTED_Q_COUNT = {
    "N1": 2,
    "N2": 2,
}


def validate_answer_string(raw: str, slot_idx: int) -> str:
    """Validate 4 options, no prefix, return cleaned '\\n'-joined string."""
    opts = [x.strip() for x in raw.strip().split("\n") if x.strip()]
    if len(opts) != 4:
        print(
            f"❌ answer_{slot_idx} phải có đúng 4 lựa chọn (thấy {len(opts)}).\n"
            f"   Options: {opts}",
            file=sys.stderr,
        )
        sys.exit(1)
    for i, opt in enumerate(opts, 1):
        # Chặn prefix kiểu "1. ", "1)", "①", "1、"
        if (
            opt[:2].strip() in ("1.", "2.", "3.", "4.", "1)", "2)", "3)", "4)")
            or opt[:1] in ("①", "②", "③", "④")
            or (len(opt) >= 2 and opt[0] in "1234" and opt[1] in "．、)")
        ):
            print(
                f"❌ answer_{slot_idx} option {i} chứa prefix ('{opt[:2]}'). "
                f"Bỏ prefix đi, chỉ ghi nội dung thuần.",
                file=sys.stderr,
            )
            sys.exit(1)
    return "\n".join(opts)


def add_question_args(parser: argparse.ArgumentParser, idx: int, required: bool) -> None:
    grp = parser.add_argument_group(f"Question {idx} ({'required' if required else 'optional'})")
    grp.add_argument(
        f"--q{idx}-label",
        dest=f"q{idx}_label",
        help=f"question_label_{idx} (OPTIONAL — luôn là '{FIXED_LABEL}')",
    )
    grp.add_argument(f"--q{idx}", dest=f"q{idx}", help=f"Câu hỏi {idx} tiếng Nhật")
    grp.add_argument(
        f"--a{idx}",
        dest=f"a{idx}",
        help=f"answer_{idx}: 4 đáp án newline-separated, KHÔNG prefix",
    )
    grp.add_argument(f"--ca{idx}", dest=f"ca{idx}", help=f"correct_answer_{idx} (1-4)")
    grp.add_argument(
        f"--evn{idx}",
        dest=f"evn{idx}",
        help=f"Explanation VN {idx} (3-part format)",
    )
    grp.add_argument(
        f"--een{idx}",
        dest=f"een{idx}",
        help=f"Explanation EN {idx} (3-part format)",
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Fill Q&A data vào CSV đọc hiểu tổng hợp (2 questions per bài, N1/N2). "
            f"Label CỐ ĐỊNH = '{FIXED_LABEL}' cho cả Q1 và Q2."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--csv", required=True, help="Đường dẫn file CSV (vd sheets/samples_v1.csv)")
    parser.add_argument("--row-id", required=True, help="_id của row cần update")
    parser.add_argument(
        "--level",
        required=True,
        choices=sorted(EXPECTED_Q_COUNT.keys()),
        help="N1|N2 — đọc hiểu tổng hợp CHỈ có 2 level này (không N3/N4/N5)",
    )
    # Q1-Q5 all optional at argparse level; we validate theo level sau
    for i in range(1, 6):
        add_question_args(parser, i, required=False)
    args = parser.parse_args()

    level = args.level
    expected = EXPECTED_Q_COUNT[level]

    # Validate CSV exists
    csv_path = args.csv
    if not os.path.exists(csv_path):
        print(f"❌ CSV không tồn tại: {csv_path}", file=sys.stderr)
        sys.exit(1)

    # Read CSV
    with open(csv_path, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    # Find row
    target = None
    for row in rows:
        if row.get("_id") == args.row_id:
            target = row
            break
    if target is None:
        print(
            f"❌ Row _id={args.row_id} không tìm thấy trong {csv_path}\n"
            f"   Hãy chạy process_html.py để tạo row trước.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Collect provided questions
    provided = []
    for i in range(1, 6):
        q_text = getattr(args, f"q{i}", None)
        q_label = getattr(args, f"q{i}_label", None)
        a_raw = getattr(args, f"a{i}", None)
        ca = getattr(args, f"ca{i}", None)
        evn = getattr(args, f"evn{i}", None)
        een = getattr(args, f"een{i}", None)
        # --qN-label là OPTIONAL (default FIXED_LABEL)
        has_any = any(x is not None for x in (q_text, q_label, a_raw, ca, evn, een))
        if has_any:
            # Check tất cả field BẮT BUỘC của slot này (label optional)
            missing = []
            if not q_text: missing.append(f"--q{i}")
            if not a_raw: missing.append(f"--a{i}")
            if not ca: missing.append(f"--ca{i}")
            if not evn: missing.append(f"--evn{i}")
            if not een: missing.append(f"--een{i}")
            if missing:
                print(
                    f"❌ Q{i} có một số flag nhưng thiếu: {missing}. "
                    f"Một slot phải đủ 5 flag (q, a, ca, evn, een) — label OPTIONAL.",
                    file=sys.stderr,
                )
                sys.exit(1)
            provided.append(i)

    # Validate số câu hỏi = expected cho level
    if len(provided) != expected:
        print(
            f"❌ Level {level} cần đúng {expected} câu hỏi, provided {len(provided)} (slots: {provided}).\n"
            f"   Đọc hiểu tổng hợp N1/N2 đều 2 câu (--q1..--q2).",
            file=sys.stderr,
        )
        sys.exit(1)

    # Validate slot liên tiếp từ 1 (không được provide q1 + q3 mà skip q2)
    if provided != list(range(1, expected + 1)):
        print(
            f"❌ Phải provide slots liên tiếp từ 1. Got {provided}, expected {list(range(1, expected + 1))}.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Resolve labels — auto-fill FIXED_LABEL nếu không provide; warn nếu provide sai
    resolved_labels = []
    for i in provided:
        user_label = getattr(args, f"q{i}_label")
        if user_label is None:
            resolved_labels.append(FIXED_LABEL)
        elif user_label != FIXED_LABEL:
            print(
                f"⚠️  --q{i}-label='{user_label}' KHÔNG khớp FIXED_LABEL.\n"
                f"    Đọc hiểu tổng hợp có label CỐ ĐỊNH duy nhất = '{FIXED_LABEL}'.\n"
                f"    Script override Q{i} → '{FIXED_LABEL}'.",
                file=sys.stderr,
            )
            resolved_labels.append(FIXED_LABEL)
        else:
            resolved_labels.append(FIXED_LABEL)

    # Validate correct_answer mỗi câu
    for i in provided:
        ca = getattr(args, f"ca{i}")
        if ca not in ("1", "2", "3", "4"):
            print(f"❌ --ca{i} phải là 1-4 (thấy '{ca}')", file=sys.stderr)
            sys.exit(1)

    # Validate + clean answer per slot
    cleaned_answers = {}
    for i in provided:
        a_raw = getattr(args, f"a{i}")
        cleaned_answers[i] = validate_answer_string(a_raw, i)

    # Soft warn: Q2 nên có cụm compare A vs B
    q2_text = getattr(args, "q2", "") or ""
    compare_keywords = ["AとB", "AもBも", "A、B", "ＡとＢ", "ＡもＢも", "Ａ、Ｂ", "共通", "違い", "異なる", "回答者"]
    if q2_text and not any(kw in q2_text for kw in compare_keywords):
        print(
            f"⚠️  Q2 có vẻ KHÔNG compare A vs B:\n"
            f"    Q2: {q2_text[:80]}{'...' if len(q2_text) > 80 else ''}\n"
            f"    Đọc hiểu tổng hợp Q2 BẮT BUỘC test tích hợp 2 đoạn.\n"
            f"    Nên dùng cụm: AとB / AもBも / AとBで共通 / AとBの違い / 回答者Ａ,Ｂ...\n"
            f"    Nếu thực sự compare, bỏ qua cảnh báo; nếu không, viết lại Q2.",
            file=sys.stderr,
        )

    # Fill fields cho slots được provide
    for slot, lbl in zip(provided, resolved_labels):
        target[f"question_label_{slot}"] = lbl
        target[f"question_{slot}"] = getattr(args, f"q{slot}")
        target[f"question_image_{slot}"] = ""
        target[f"answer_{slot}"] = cleaned_answers[slot]
        target[f"correct_answer_{slot}"] = getattr(args, f"ca{slot}")
        target[f"explain_vn_{slot}"] = getattr(args, f"evn{slot}")
        target[f"explain_en_{slot}"] = getattr(args, f"een{slot}")

    # Clear các slot còn lại
    for i in range(expected + 1, 6):
        for fld in (
            f"question_label_{i}",
            f"question_{i}",
            f"question_image_{i}",
            f"answer_{i}",
            f"correct_answer_{i}",
            f"explain_vn_{i}",
            f"explain_en_{i}",
        ):
            target[fld] = ""

    # Đảm bảo general_image luôn rỗng (đọc hiểu tổng hợp không có screenshot)
    target["general_image"] = ""

    # Write back
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in CSV_FIELDNAMES})

    # Summary
    print(f"✅ Đã fill {expected} câu hỏi cho {args.row_id} ({level}) trong {csv_path}")
    for slot, lbl in zip(provided, resolved_labels):
        q = getattr(args, f"q{slot}")
        ca = getattr(args, f"ca{slot}")
        opts = cleaned_answers[slot].split("\n")
        print(f"  Q{slot} [{lbl}]: {q[:60]}{'...' if len(q) > 60 else ''}")
        for j, opt in enumerate(opts, 1):
            marker = "  ✓" if str(j) == ca else ""
            print(f"     ({j}) {opt[:50]}{'...' if len(opt) > 50 else ''}{marker}")
        print(f"     correct_answer_{slot}: {ca}")
    print(f"  Fixed label: {FIXED_LABEL} (OK cho cả Q1 và Q2)")


if __name__ == "__main__":
    main()
