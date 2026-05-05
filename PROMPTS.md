# Prompt — Gen bài Đọc Hiểu Tổng Hợp (JLPT 統合理解)

## Cách dùng

Copy prompt bên dưới, thay `{số}` rồi paste vào Claude hoặc Gemini.

**⛔ Scope chỉ 2 level**: **N1** (2 câu/bài, A+B ~600–750 chars) và **N2** (2 câu/bài, A+B ~600–800 chars). N3/N4/N5 KHÔNG có kind này — KHÔNG gen.

**Đặc thù**: 2 đoạn **A và B** trên CÙNG topic, khác quan điểm (contrast / complement / debate / advice). Q2 BẮT BUỘC compare A vs B. Label CỐ ĐỊNH `question_comprehensive_understanding` cho cả 2 câu.

> **🚨 ZERO-TOLERANCE QC**: Chỉ cần **1 tiêu chí FAIL** trong checklist 34 mục QC của SKILL.md → **fix ngay hoặc gen lại** trước khi sang bài tiếp.

---

## Prompt

```
Đọc .claude/skills/jlpt-reading-integrated/SKILL.md rồi gen bài đọc hiểu tổng hợp:
- N2: {số} bài (2 câu/bài, A+B ~600–800 chars)
- N1: {số} bài (2 câu/bài, A+B ~600–750 chars)

⛔ CHỈ N1 và N2. Không gen N3/N4/N5.

Lưu CSV: sheets/samples_v1.csv. HTML: assets/html/doc_hieu_tong_hop/{LEVEL}_{uuid}.html.

═══ BƯỚC 0 — CHUẨN BỊ (1 lần) ═══
1. Đọc rules/rule_doc_hieu.md (rule giáo viên — source-of-truth, 11 phần). Áp dụng đặc biệt:
   - Phần 2.4 (Thể chia 文体の統一): N1/N2 → 普通形 (だ・である). Cả bài A + B + câu hỏi + 4 đáp án thống nhất 普通形 toàn bộ. (A và B có thể khác sắc thái nhưng cùng level + cùng thể.)
   - Phần 3 (Furigana), Phần 4 (8 loại Q — comprehensive_understanding cố định), Phần 5 (5 loại bẫy chuẩn + **Single-side** đặc trưng dạng này).
2. Đọc rules/content.md + vocabulary.md + technical.md + questions.md.
3. Đọc rules/kanji_jlpt_sensei.csv (2495 kanji) để tra furigana.
4. Load 2 sample/level: scripts/load_references.py --level {LEVEL} --count 2.
5. Scan sheets/samples_v1.csv xem topic + relationship + Q combo đã dùng.

═══ BƯỚC 1→5 — LẶP CHO TỪNG BÀI ═══
1. Gen _id = {LEVEL}_{uuid32}; chọn topic + A↔B relationship + Q combo chưa/ít dùng.
   - Relationship: contrast (đối lập) / complement (bổ sung) / debate (phản biện) / advice (3-section 相談者+回答者Ａ+回答者Ｂ, ~5% data N2).
2. Tag = **tiếng Anh** từ cột `en` của rules/topic.json (artificial intelligence, lifestyle...). TUYỆT ĐỐI không tiếng Việt/Nhật.
3. Gen HTML: container 780px, line-height 1.9, word-break keep-all, <p> thuần (KHÔNG <br> giữa câu, KHÔNG <table>).
   - 2 sections: <section class="passage-a"> + <section class="passage-b">, mỗi section có <span class="label">A|B</span>; 2–4 <p> per section.
   - Mỗi đoạn 40–60% tổng chars; chênh lệch ≤ 30%. A và B CÙNG topic, khác quan điểm.
   - **Toàn bộ 普通形 (Phần 2.4)**. Furigana chỉ cho từ vượt level (cấm "Ab"); ưu tiên 0 ruby (data thực tế = 0%).
   - Marker ①② chỉ cho Q1 A-focus (Combo 3); Q2 KHÔNG có marker.
4. Gen 2 câu Q + 4 đáp án (newline \n, KHÔNG prefix); **label CỐ ĐỊNH = question_comprehensive_understanding cho cả Q1 + Q2**.
   - Q2 BẮT BUỘC compare A vs B (dùng AとB / AもBも / AとBで共通 / AとBの違い / 「相談者」の相談に対するＡ、Ｂの回答). Đáp án Q2 PHẢI cần info từ CẢ A + B. CẤM Q2 chỉ về A, chỉ về B, hoặc kiến thức ngoài.
   - 4 combo Q1+Q2 (chọn 1): Common+Compare (≥50%) | Compare+Compare | A-focus+Compare (có ①) | Advice+Compare.
   - Q1 + Q2 KHÔNG trùng khía cạnh.
   - Distractor Q2 BẮT BUỘC ≥ 2 dạng: **Role reversal A/B** (đặc trưng) + **Single-side**. Đa dạng 6 loại bẫy: Role reversal / Single-side / Mix A+B / Scope / Extreme / Extraneous. Mọi distractor dùng info THẬT từ A hoặc B.
5. Tạo CSV row bằng scripts/process_html.py. Fill Q&A bằng scripts/fill_qa.py (KHÔNG sửa CSV tay; label cố định auto-fill).

═══ BƯỚC 2 — QC ZERO-TOLERANCE (BẮT BUỘC) ═══
Tự đánh giá 34 mục checklist trong SKILL.md, log PASS/FAIL:
- A. HTML + AB balance (13) + B. Content (6 — chủ đề, từ vựng level, **toàn bộ 普通形** A và B đồng nhất) + C. Q&A + verify (11 — label cố định, paraphrase ≥4 từ N1 / ≥5 từ N2, explain VN+EN trích cả A+B cho Q2, self-solve khớp correct, đặc biệt check Role reversal) + D. Compare coverage (4)
- **1 FAIL = fix ngay hoặc gen lại → refresh CSV (nếu sửa HTML) → QC lại từ đầu**. CẤM bỏ qua.

═══ HARD REJECT (gen lại ngay) ═══
- Q count khác 2 (slot 3-5 phải empty); label khác question_comprehensive_understanding
- Q2 không compare A vs B (chỉ về A, chỉ về B, hoặc kiến thức ngoài)
- A/B balance vỡ: 1 đoạn < 40% hoặc > 60% tổng chars
- Char range A+B ngoài: N1 600–750 | N2 600–800
- HTML thiếu <section class="passage-a/b"> hoặc thiếu <span class="label">A|B</span>; có <table> hoặc <br> giữa câu
- <ruby> thiếu <rt> hoặc <rt> rỗng; furigana dạng "Ab"
- Thể chia trộn lẫn (xuất hiện です・ます trong A hoặc B)
- Q2 distractor không có Role reversal hoặc Single-side
- Tag tiếng Việt/Nhật; trong cùng level: trùng topic hoặc <2 relationship type khác nhau (khi N≥2 bài)

═══ CUỐI BATCH ═══
python3 .claude/skills/jlpt-reading-integrated/scripts/process_html.py --validate --html-dir assets/html/doc_hieu_tong_hop --csv sheets/samples_v1.csv
```
