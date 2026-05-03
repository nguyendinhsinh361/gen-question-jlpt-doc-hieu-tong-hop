# Prompt — Gen bài Đọc Hiểu Tổng Hợp (JLPT 統合理解)

## Cách dùng

Copy prompt bên dưới, thay `{số}` rồi paste vào Claude hoặc Gemini.
SKILL.md chứa workflow + checklist 34 mục QC. rules/ chứa chi tiết. Prompt chỉ cần nói **cái gì** và **bao nhiêu**.

**⛔ Scope chỉ 2 level**: **N1** (2 câu/bài, tổng A+B ~600–750 chars) và **N2** (2 câu/bài, tổng A+B ~600–800 chars). N3/N4/N5 KHÔNG có kind này — KHÔNG gen.

**Đặc thù**: 2 đoạn **A và B** trên CÙNG topic, khác quan điểm (contrast / complement / debate / advice). Q2 BẮT BUỘC compare A vs B. Label CỐ ĐỊNH `question_comprehensive_understanding` cho cả 2 câu.

---

## Prompt ngắn (khuyên dùng)

```
Đọc .claude/skills/jlpt-reading-integrated/SKILL.md rồi gen bài đọc hiểu tổng hợp:
- N2: {số} bài (2 câu/bài, A+B ~600–800 chars)
- N1: {số} bài (2 câu/bài, A+B ~600–750 chars)

⛔ CHỈ N1 và N2. KHÔNG gen N3/N4/N5.

Lưu CSV vào sheets/samples_v1.csv. HTML lưu vào assets/html/doc_hieu_tong_hop/{LEVEL}_{uuid}.html.
Làm đúng theo SKILL.md — từng bài một, đọc rules/ trước khi gen.

⛔ Q COUNT BẮT BUỘC: cả N1 và N2 = 2 câu (fill question_{1,2}, slot 3–5 empty).

⛔ LABEL CỐ ĐỊNH: cả Q1 và Q2 đều là `question_comprehensive_understanding`. KHÔNG label nào khác.

⛔ Q2 COMPARE A vs B (BẮT BUỘC):
- Q2 PHẢI test tích hợp 2 đoạn (dùng cụm `AとB`, `AもBも`, `AとBで共通`, `AとBの違い`...)
- CẤM Q2 chỉ về A, chỉ về B, hoặc kiến thức ngoài bài
- Đáp án đúng Q2 PHẢI cần info từ CẢ A + B để chọn

⛔ Q1 + Q2 KHÔNG trùng khía cạnh:
- Q1 common → Q2 compare difference, hoặc Q1 focus 1 đoạn → Q2 compare tổng thể

⛔ A/B BALANCE — đặc thù dạng này:
- Mỗi đoạn 40–60% tổng chars; chênh lệch ≤ 30%
- 2 sections: <section class="passage-a"> + <section class="passage-b">, mỗi section có <span class="label">A|B</span>
- Paragraph per section: 2–4 <p>
- A và B CÙNG topic, khác quan điểm/góc nhìn (contrast / complement / debate / advice)

⛔ ĐA DẠNG — BẮT BUỘC:
1. Đọc rules/rule_doc_hieu.md (rule giáo viên — section 3-5 áp dụng trực tiếp) + rules/content.md (chủ đề + A↔B relationship + char range) + rules/questions.md (4 combo Q1/Q2).
2. Scan sheets/samples_v1.csv xem topic + relationship đã dùng.
3. Trong cùng level: KHÔNG trùng topic; đa dạng relationship type (contrast/complement/debate/advice).
4. Tag **tiếng Anh** từ cột `en` của `rules/topic.json` (vd: artificial intelligence, lifestyle, aging society). TUYỆT ĐỐI không tiếng Việt/Nhật.

⛔ DISTRACTOR Q2 — BẮT BUỘC ≥ 2 dạng:
- **Role reversal A/B** (đặc trưng dạng này): A nói X, B nói Y → distractor "A nói Y, B nói X"
- **Single-side**: chỉ khớp A hoặc chỉ khớp B, được presented như "cả 2"

⛔ FURIGANA — chỉ cho từ VƯỢT level. Cấm dạng "Ab". Data thực tế cả N1 và N2 = 0% ruby — ưu tiên 0 ruby. Tra rules/kanji_simplified.csv.

⛔ HTML rules: <p> thuần (KHÔNG <br> giữa câu), KHÔNG <table>. Container 780px, line-height 1.9.

⛔ ADVICE FORMAT (optional, ~5% data N2): 3 sections 相談者 + 回答者Ａ + 回答者Ｂ thay cho A+B.

Sau khi gen xong mỗi bài, tự QC checklist 34 mục trong SKILL.md (HTML + AB balance + content + Q&A + integrated-compare coverage → log PASS/FAIL). 1 FAIL = sửa → QC lại. Tất cả PASS mới sang bài tiếp.
Điền Q&A bằng scripts/fill_qa.py (KHÔNG sửa CSV bằng tay; label tự động điền cố định).
Sửa HTML = chạy lại process_html.py --refresh.
Verify cuối: python3 .claude/skills/jlpt-reading-integrated/scripts/process_html.py --validate --html-dir assets/html/doc_hieu_tong_hop
```

---

## Prompt có thêm ràng buộc (khi cần kiểm soát chất lượng)

```
Đọc .claude/skills/jlpt-reading-integrated/SKILL.md rồi gen bài đọc hiểu tổng hợp:
- N2: {số} bài | N1: {số} bài

⛔ CHỈ N1 và N2. KHÔNG gen N3/N4/N5.

Lưu CSV vào sheets/samples_v1.csv. HTML lưu vào assets/html/doc_hieu_tong_hop/{LEVEL}_{uuid}.html.
Trước khi gen:
1. Đọc rules/rule_doc_hieu.md (rule giáo viên — source-of-truth cho vocab/grammar/distractor)
2. Đọc rules/content.md + rules/vocabulary.md + rules/technical.md + rules/questions.md
3. Đọc rules/kanji_simplified.csv để tra level kanji
4. Đọc 1-2 sample: scripts/load_references.py --level {LEVEL} --count 2
5. Scan sheets/samples_v1.csv xem topic + relationship + Q combo nào đã dùng

⛔ Q COUNT: cả N1 và N2 = 2 câu. Slot 3-5 empty.

⛔ LABEL CỐ ĐỊNH: cả Q1 và Q2 = `question_comprehensive_understanding`. Không label nào khác. fill_qa.py auto-fill nếu thiếu.

⛔ Q2 COMPARE A vs B (HARD RULE):
- Dùng cụm AとB / AもBも / AとBで共通 / AとBの違い / 「相談者」の相談に対するＡ、Ｂの回答
- Đáp án đúng Q2 PHẢI cần info từ CẢ A + B
- CẤM Q2 chỉ về A, chỉ về B, hoặc kiến thức ngoài bài

⛔ 4 COMBO Q1+Q2 (chọn 1):
1. Common + Compare (50%+ dùng): Q1 `AとBで共通して述べられているのはどれか。` → Q2 `XについてAとBはどのように述べているか。`
2. Compare + Compare: Q1 compare X → Q2 compare Y (cùng topic, 2 khía cạnh)
3. A-focus + Compare (có marker ①): Q1 `①...とあるが、どのようなことか。` → Q2 `AとBに共通する考え方はどれか。`
4. Advice + Compare: Q1 hỏi về 相談者 → Q2 `「相談者」の相談に対するＡ、Ｂの回答について、正しいものはどれか。`

⛔ A/B BALANCE:
- Mỗi đoạn 40–60% tổng chars; chênh lệch ≤ 30%
- HTML structure: <section class="passage-a"> + <section class="passage-b">, mỗi section có <span class="label">A|B</span>
- Paragraph per section: 2–4 <p>

⛔ A ↔ B RELATIONSHIP — chọn 1, đa dạng trong batch:
- Contrast: A vs B đối lập (A khen vs B chê)
- Complement: A và B nhìn 2 khía cạnh khác của cùng issue
- Debate: A đưa argument, B phản biện
- Advice: 相談者 → Ａ, Ｂ đưa 2 lời khuyên khác (3-section format, ~5% data N2)

⛔ ĐA DẠNG CHỦ ĐỀ + RELATIONSHIP:
- Trong cùng level: KHÔNG trùng topic; đa dạng relationship type ≥ 2 loại
- Cross-level: ưu tiên topic chưa xuất hiện
- Tag **tiếng Anh** từ cột `en` của `rules/topic.json` (artificial intelligence, lifestyle, environment, etc.) — TUYỆT ĐỐI không tiếng Việt/Nhật

⛔ FURIGANA ZERO-TOLERANCE:
- Kanji vượt level PHẢI có <ruby><rt>. Cấm dạng "Ab"
- Density per level: N1 ≤ 3, N2 ≤ 5. Ưu tiên 0 (data thực tế = 0%)

⛔ HTML rules:
- <p> thuần, KHÔNG <br> giữa câu, KHÔNG <table>
- Container 780px, line-height 1.9, word-break keep-all
- Marker ①② chỉ cho Q1 A-focus (Combo 3); Q2 KHÔNG có marker

⛔ ĐÁP ÁN — 4 options newline-separated, KHÔNG prefix "1.", "①", "1)".

Yêu cầu chất lượng câu hỏi:
- Distractor Q2 BẮT BUỘC ≥ 2 dạng: Role reversal A/B HOẶC Single-side
- Đa dạng 6 loại bẫy: Role reversal / Single-side / Mix A+B / Scope / Extreme / Extraneous
- Mỗi distractor PHẢI dùng info thật từ A hoặc B, KHÔNG bịa
- Paraphrase: đáp án đúng KHÔNG copy nguyên văn ≥ 4 từ liên tiếp (N1) / 5 từ (N2)
- Self-solve: tự giải từng câu, đặc biệt check Role reversal (thứ tự chủ thể trong distractor ngược với bài)
- Explanation 3 phần (VN + EN), Q2 trích dẫn CẢ A + B

Sau khi gen xong mỗi bài, BẮT BUỘC tự QC theo 34 mục checklist trong SKILL.md:
- Phần A HTML + AB balance (13) + B Content (6) + C Q&A + verify (11) + D Compare coverage (4)
- 1 FAIL = sửa → refresh CSV (nếu sửa HTML) → QC lại

Lưu ý kỹ thuật:
- Điền Q&A bằng scripts/fill_qa.py (KHÔNG edit CSV tay; label cố định auto-fill)
- Refresh CSV sau sửa HTML: process_html.py --refresh
- Verify cuối: process_html.py --validate --html-dir assets/html/doc_hieu_tong_hop
```
