---
name: jlpt-doc-hieu-tong-hop
description: >
  Generate JLPT "đọc hiểu tổng hợp" (integrated / comparative comprehension / 統合理解)
  reading items as styled HTML files and output CSV training data for AI fine-tuning. Each
  item contains **TWO short Japanese passages A and B (total 600–800 characters)** on the
  same topic — with contrasting / complementary / debating viewpoints — tested via **2
  multiple-choice questions per item that probe comparison and integration across A and B**.
  All questions use the fixed label `question_comprehensive_understanding`.
  This skill applies ONLY to N1 (≈600-750 chars total) and N2 (≈600-800 chars total). Other
  JLPT levels do NOT have this reading type.
  Skill này bao gồm TOÀN BỘ luồng: gen → QC loop (checklist PASS/FAIL) → sửa. Gen từng bài
  một, kiểm tra đến khi đạt chất lượng mới chuyển sang bài tiếp theo. Output chỉ gồm HTML +
  CSV (không có screenshot PNG).
  Use this skill whenever the user wants to: gen bài đọc hiểu tổng hợp, tạo nội dung
  integrated / comparative reading, generate JLPT 統合理解 / comparative passages, produce
  AI fine-tuning data for the "đọc hiểu tổng hợp" section of JLPT N1 or N2.
  Also trigger when the user mentions: gen bài đọc hiểu tổng hợp, tạo bài so sánh AB,
  generate JLPT 統合理解, 2-đoạn comparative reading N1/N2, integrated comprehension,
  advice format 相談者 + 回答者A + 回答者B.
---

# JLPT 統合理解 / Đọc Hiểu Tổng Hợp — Workflow

> **🔒 NGUYÊN TẮC CỐT LÕI — ZERO-TOLERANCE (BẮT BUỘC):**
> 1. **Gen từng bài một** — không batch rồi QC sau
> 2. **Agent tự QC** — đọc lại bài + câu hỏi, tự đánh giá từng mục, log PASS/FAIL
> 3. **🚨 1 FAIL = CHƯA XONG** — sửa → QC lại TỪ ĐẦU → lặp đến khi ALL PASS. **TUYỆT ĐỐI CẤM:**
>    - Skip mục FAIL hoặc mark "tạm thời để đó"
>    - Tự ý sang bài tiếp khi còn ≥ 1 FAIL ở bài hiện tại
>    - Ghi PASS mà không thực sự đọc lại nội dung và verify
>    - "Hợp lý hoá" lỗi (vd "char count chỉ vượt 5 ký tự thì OK") — nếu rule nói FAIL thì là FAIL
> 4. **🔒 5 GATE bắt buộc** giữa các BƯỚC (0→1, 1→2, 2→3, 3→4, 4→5) — KHÔNG qua gate = KHÔNG được sang bước tiếp. Mỗi gate phải log explicit "GATE X→Y PASSED" trước khi tiếp tục.


## Cấu trúc file

| File | Nội dung | Đọc khi |
|------|----------|---------|
| `SKILL.md` (file này) | Workflow + QC Checklist | Luôn đọc đầu tiên |
| `rules/content.md` | R1 chủ đề N1/N2 (A↔B relationship) + R2 char count/Q count/paragraph count/A-B balance + R7 formats (standard + advice) + R8 visual (label A/B, marker, `<u>`, 注) | Gen HTML |
| `rules/vocabulary.md` | R3 từ vựng/ngữ pháp + R4 furigana (N1/N2) | Gen HTML + QC |
| `rules/questions.md` | R5 2 câu hỏi + label CỐ ĐỊNH + Q2 compare RULE + R6 đáp án/6 bẫy (role reversal, single-side, ...) | Gen Q&A + QC |
| `rules/technical.md` | R9 HTML template 780px (2-section + advice 3-section) + R10 clean HTML + R11 CSV schema + R12 QC automation | Gen HTML + CSV |
| `references/html-patterns.md` | Template chi tiết per level + AB balance patterns + advice format | Tra cứu khi gen HTML |
| `references/sample-analysis.md` | Phân tích định lượng data mẫu N1/N2 | Hiểu tần suất pattern |
| `scripts/process_html.py` | Xử lý HTML → CSV + count (total + per-section) + validate + 2-question support | Gen CSV + QC |
| `scripts/fill_qa.py` | Điền Q&A vào CSV (quote an toàn, 2 câu, FIXED_LABEL rule) | Sau khi gen Q&A |
| `scripts/load_references.py` | Load sample JSON để calibrate | BƯỚC 0 chuẩn bị |

## Outputs Per Item

1. **Styled HTML** → `assets/html/doc_hieu_tong_hop/{LEVEL}_{uuid}.html`
2. **Clean HTML** → CSV column `text_read` (no attributes, no `<rt>` content)
3. **CSV row** → `sheets/samples_v1.csv` với 2 câu hỏi populate (question_3, question_4, question_5 + related cols empty)

**KHÔNG có screenshot PNG.** CSV column `general_image` luôn `""`.

## Scope — CHỈ N1 và N2

| Level | Có "đọc hiểu tổng hợp"? | Q Count | Char Range (A + B) | Focus spec |
|-------|------------------------|---------|---------------------|------------|
| **N1** | ✅ có | **2** | **600–750** | so sánh và tổng hợp đa quan điểm |
| **N2** | ✅ có | **2** | **600–800** | so sánh và tổng hợp đa quan điểm |
| N3    | ❌ KHÔNG có            | —       | —                   | — |
| N4    | ❌ KHÔNG có            | —       | —                   | — |
| N5    | ❌ KHÔNG có            | —       | —                   | — |

> **⛔ KHÔNG gen N3, N4, N5 cho dạng đọc hiểu tổng hợp** — sẽ bị reject bởi spec.

## Số câu hỏi per level (BẮT BUỘC)

| Level | Q Count | Slots populate | Slots empty | Label CỐ ĐỊNH | Q2 rule |
|-------|---------|----------------|-------------|---------------|---------|
| **N1** | 2       | `question_{1,2}` | `question_{3,4,5}` | `question_comprehensive_understanding` | **Q2 compare A vs B** |
| **N2** | 2       | `question_{1,2}` | `question_{3,4,5}` | `question_comprehensive_understanding` | **Q2 compare A vs B** |

> **⛔ LABEL RULE**: Cả Q1 và Q2 (2 level) **ĐỀU PHẢI** là `question_comprehensive_understanding`. Không có label khác. Pipeline warn và override nếu sai.
> **⛔ Q2 COMPARE RULE**: Q2 PHẢI test **tích hợp A + B** (hỏi về cả 2 đoạn). Cấm Q2 chỉ về A hoặc chỉ về B.
> **⛔ DIVERSITY RULE**: Q1 và Q2 PHẢI test 2 khía cạnh KHÁC NHAU (Q1 common → Q2 compare khác biệt; Q1 focus 1 đoạn → Q2 compare tổng thể).

## A/B Balance Rule (đặc thù đọc hiểu tổng hợp)

| Rule | Yêu cầu |
|------|---------|
| Mỗi đoạn chiếm | 40–60% tổng chars |
| Chênh lệch | ≤ 30% (abs(A_chars - B_chars) / max(A_chars, B_chars) ≤ 0.30) |
| Section | `<section class="passage-a">` + `<section class="passage-b">` (hoặc advice 3-section) |
| Topic | A và B cùng 1 topic, quan điểm khác/bổ sung nhau |

---

# WORKFLOW

## BƯỚC 0: CHUẨN BỊ (1 lần cho batch)

1. **Đọc `rules/rule_doc_hieu.md`** — **Bộ Tiêu Chí Đánh Giá Đọc Hiểu JLPT toàn diện** từ giáo viên (source-of-truth, 11 phần: 4 tiêu chí, 程度 ±, 書き下ろし/による, nhãn A/B, **文体の統一 (thể chia)**, furigana per level, 8 loại câu hỏi, **7 loại bẫy** (5 chuẩn + **Single-side ĐẶC TRƯNG cho 統合理解** + Peripheral Source cho N1 khi 注 dài), tiêu chí chi tiết per level).
   **Phần áp dụng trực tiếp cho dạng đọc hiểu tổng hợp (統合理解)** — CHỈ N1 và N2:
   - Phần 1 (Tổng quan & Nguyên tắc 程度) — biên ± per level; ~600字 tổng A+B (mỗi bài 250–360字)
   - Phần 2 (Hình thức) — nhãn A/B rõ ràng; **không ①② cho câu so sánh**; có gạch chân khi câu hỏi chi tiết về A hoặc B
   - **Phần 2.4 (Thể chia nhất quán 文体の統一)** — N1/N2 dùng **普通形** (だ・である). Cả bài A và bài B + câu hỏi + 4 đáp án phải **thống nhất thể** — toàn bộ 普通形. (Văn phong A và B có thể khác nhau chút về sắc thái nhưng cùng level và cùng thể.)
   - Phần 3 (Furigana) — bảng quy tắc per level
   - Phần 4 (8 loại câu hỏi) — đặc biệt **`comprehensive_understanding`** (LABEL CỐ ĐỊNH cho cả 2 câu), 2 form chuẩn: 「AとBが共通して述べていることは何か」 + 「○○について、AとBはどのように述べているか」
   - Phần 5 (7 loại bẫy = 5 chuẩn + **Single-side ĐẶC TRƯNG** + Peripheral Source) — đặc biệt **Single-side** (bẫy đặc trưng riêng cho 統合理解) + **Cross-swap** (gán ý A cho B / ngược lại) cho Q2
   - **Phần 9.3 (N2 統合理解 ~600字, 2 câu)**, **Phần 10.4 (N1 統合理解 ~600字, 2 câu)** — tiêu chí chi tiết 4 chiều; A và B đối lập hoặc bổ sung
   - Phần 11 (Bảng so sánh tổng hợp) — tra cứu nhanh.
2. **Đọc rules skill**: `rules/content.md` + `rules/vocabulary.md` + `rules/technical.md` + `rules/questions.md`
3. **Đọc `rules/kanji_jlpt_sensei.csv`** — dùng để tra level từng kanji khi quyết định furigana
4. **Scan `sheets/samples_v1.csv` và `data/doc_hieu_tong_hop_n{1,2}_clean.json`** — xem format, topic đã dùng → chọn format chưa/ít dùng
5. **Load 2-3 sample calibrate style**:
   ```bash
   python3 .claude/skills/jlpt-reading-integrated/scripts/load_references.py --level N1 --count 2
   python3 .claude/skills/jlpt-reading-integrated/scripts/load_references.py --level N2 --count 2
   ```
6. **Lập kế hoạch batch**: mỗi bài gán format + topic + combo A↔B relationship (contrast/complement/debate/advice) khác nhau. Topic chọn **tiếng Anh** từ cột `en` của `rules/topic.json` (đa dạng ≥ 2 category trong batch > 3 bài). Mỗi topic phải phù hợp cho CẢ A và B viewpoints.

---

### 🔒 GATE 0→1 — KHÔNG QUA = KHÔNG ĐƯỢC GEN

Trước khi bắt đầu BƯỚC 1, agent PHẢI confirm bằng cách tick từng item:

- [ ] Đã đọc `rules/rule_doc_hieu.md` (đặc biệt Phần 1, 2, **2.4 thể chia**, 3, 4, 5, các phần per-level applicable, 11)
- [ ] Đã đọc đủ 4 file: `rules/content.md` + `rules/vocabulary.md` + `rules/technical.md` + `rules/questions.md`
- [ ] Đã đọc `rules/kanji_jlpt_sensei.csv` (sẵn sàng tra furigana)
- [ ] Đã chạy `load_references.py --level {LEVEL} --count 2` và đọc samples
- [ ] Đã scan `sheets/samples_v1.csv` để biết topic + label đã dùng
- [ ] Đã có kế hoạch batch (format + topic + label per bài)

❌ **Bất kỳ item nào CHƯA tick → quay lại BƯỚC 0**, KHÔNG được gen.
✅ Khi 6/6 tick → log `GATE 0→1 PASSED — ready to gen` rồi sang BƯỚC 1.

---

## BƯỚC 1→5: LẶP CHO TỪNG BÀI

### BƯỚC 1: GEN HTML + 2 CÂU HỎI

> Đọc: `rules/content.md` + `rules/vocabulary.md` + `rules/technical.md` + `rules/questions.md`
> Tham khảo: `references/html-patterns.md` cho template per level + advice format

1. **Gen `_id`** = `{LEVEL}_{uuid.uuid4().hex}` (full 32-char hex). Level ∈ {N1, N2}.
2. **Chọn format** từ R7 (`rules/content.md`):
   - **Standard 2-section**: A + B, cùng topic, khác quan điểm (phổ biến nhất)
   - **Advice 3-section**: 相談者 + 回答者Ａ + 回答者Ｂ (tư vấn; chỉ N2; ~5% data)
3. **Chọn `tag`** (topic) — **tiếng Anh** từ cột `en` của `rules/topic.json`, đa dạng trong batch
4. **Chọn A↔B relationship type** (R1.2):
   - **Contrast**: A vs B đối lập (VD A khen vs B chê)
   - **Complement**: A và B nhìn 2 khía cạnh khác của cùng issue
   - **Debate**: A đưa argument, B phản biện / counter
   - **Advice**: 相談者 → Ａ, Ｂ đưa 2 lời khuyên khác
5. **Plan 2 viewpoints + common thread** — viết trước:
   - Topic chung là gì?
   - A nói gì (thesis + 1-2 supporting points)
   - B nói gì (thesis + 1-2 supporting points)
   - Điểm chung của A và B là gì? Điểm khác biệt ở đâu?
6. **Chọn combo 2 câu hỏi** (R5.3):
   - **Combo 1 — Common + Compare** (50%+ dùng): Q1 `AとBで共通して述べられているのはどれか。` → Q2 `XについてAとBはどのように述べているか。`
   - **Combo 2 — Compare + Compare**: Q1 compare X → Q2 compare Y
   - **Combo 3 — A-focus + Compare** (có marker ①): Q1 `①...とあるが、どのようなことか。` → Q2 `AとBに共通する考え方はどれか。`
   - **Combo 4 — Advice + Compare**: Q1 hỏi về 相談者 → Q2 `「相談者」の相談に対するＡ、Ｂの回答について、正しいものはどれか。`
7. **Gen HTML** theo rules → save `assets/html/doc_hieu_tong_hop/{LEVEL}_{uuid}.html`
   - Container `max-width: 780px; margin: 0 auto; padding: 40px 20px; line-height: 1.9`
   - `word-break: keep-all`, `line-break: strict`
   - 2 (hoặc 3) `<section>` — mỗi section có `<span class="label">A|B|相談者|回答者Ａ|回答者Ｂ</span>` ở đầu
   - `<p>` thuần, KHÔNG `<br>` giữa câu
   - **Paragraph per section**: 2–4 `<p>` per section (bài ngắn, súc tích)
   - **A/B balance**: mỗi đoạn 40–60% tổng chars
   - Marker ①② chỉ khi Q1 là A-focus (Combo 3); **Q2 KHÔNG dùng marker** (vì compare tổng thể)
   - Furigana chỉ cho từ vượt level (tra `rules/kanji_jlpt_sensei.csv`) — data 0% nên ưu tiên 0 ruby
   - **Source line**: hầu như KHÔNG dùng (data N1:4%, N2:0%)
   - **Annotation 注**: hiếm (data N1:4%, N2:0%)
   - **KHÔNG** dùng `<br>` giữa câu, KHÔNG dùng `<table>` layout
8. **Gen 2 câu hỏi + 4 đáp án mỗi câu** theo `rules/questions.md`:
   - 4 options ngăn cách `\n`, KHÔNG số thứ tự `1.`, `①`, `1)`
   - `correct_answer_i` = integer 1-4
   - Mỗi distractor PHẢI dùng info/ý THẬT từ bài (1 trong 6 loại bẫy: **Role reversal A/B** / Single-side / Mix A+B / Scope / Extreme / Extraneous)
   - **BẮT BUỘC ≥ 2 distractor dạng Role reversal hoặc Single-side** cho Q2 compare
   - Paraphrase: đáp án đúng KHÔNG copy > 4 từ (N1) hoặc > 5 từ (N2) liên tiếp
   - Giải thích `explain_vn_i` + `explain_en_i` theo format 3 phần
   - **Cả Q1 và Q2**: `question_label` = `question_comprehensive_understanding` (CỐ ĐỊNH)
   - **Q2 PHẢI compare A vs B** (tích hợp 2 đoạn)
9. **Tạo CSV row** bằng `process_html.py` hoặc `fill_qa.py` (⚠️ **dùng script, KHÔNG sửa CSV tay**):
   ```bash
   # Recommended cho 2 câu: JSON
   python3 .claude/skills/jlpt-reading-integrated/scripts/process_html.py \
     --file assets/html/doc_hieu_tong_hop/{LEVEL}_{uuid}.html \
     --csv sheets/samples_v1.csv \
     --tag "{topic_vn}" \
     --questions-json /tmp/qs.json
   ```
   Hoặc dùng `fill_qa.py` với flags per-question:
   > **⛔ KHÔNG ĐƯỢC sửa CSV bằng tay. Commas + newlines trong nội dung (`100,000円`, `A\nB\nC\nD`) sẽ làm vỡ cột.**
   ```bash
   # Ví dụ N1 (2 câu)
   python3 .claude/skills/jlpt-reading-integrated/scripts/fill_qa.py \
     --csv sheets/samples_v1.csv --row-id {LEVEL}_{uuid} --level N1 \
     --q1 "AとBで共通して述べられているのはどれか。" --a1 "A\nB\nC\nD" --ca1 2 --evn1 "..." --een1 "..." \
     --q2 "XについてAとBはどのように述べているか。" --a2 "A\nB\nC\nD" --ca2 3 --evn2 "..." --een2 "..."
   ```
   (Label tự động điền `question_comprehensive_understanding` — không cần flag `--q1-label`.)

---

### 🔒 GATE 1→2 — KHÔNG QUA = KHÔNG ĐƯỢC QC

Trước khi sang BƯỚC 2 (QC), agent PHẢI confirm:

- [ ] File HTML đã save vào `assets/html/doc_hieu_tong_hop/{LEVEL}_{uuid}.html` (verify file tồn tại)
- [ ] CSV row đã tạo bằng `process_html.py` (KHÔNG sửa CSV tay)
- [ ] `_id` đúng format `{LEVEL}_{uuid32}` (không tạm thời, không placeholder)
- [ ] Tất cả Q + 4 đáp án + correct_answer + explain_vn + explain_en đã fill (không "TODO", không empty)
- [ ] Đã đọc lại file HTML vừa gen (mở file, đọc content) — KHÔNG dựa vào "tôi nhớ tôi đã gen"

❌ Bất kỳ item nào CHƯA confirm → quay lại BƯỚC 1 fix, KHÔNG được QC.
✅ Khi 5/5 tick → log `GATE 1→2 PASSED — ready to QC` rồi sang BƯỚC 2.

---

### BƯỚC 2: ⛔ QC — AGENT TỰ ĐÁNH GIÁ CHECKLIST

> **ĐÂY LÀ BƯỚC QUAN TRỌNG NHẤT. KHÔNG ĐƯỢC BỎ QUA.**
>
> Agent phải **đọc lại** file HTML vừa gen + **TOÀN BỘ** 2 câu hỏi/đáp án trong CSV,
> rồi **tự đánh giá từng mục** bên dưới. Log kết quả theo format:
>
> ```
> QC: {_id}  |  Level: N1  |  Q count: 2/2  |  Labels: [comprehensive_understanding × 2]
> ────────────────────────────────
> [ 1] ✅ PASS — Char count (687 chars, range 600-750)
> [ 2] ✅ PASS — A/B balance (A=338, B=349, diff 3%)
> [ 3] ❌ FAIL — Q2 compare rule (Q2 chỉ hỏi về A, không đề cập B)
> ...
> ────────────────────────────────
> ⚠️ 1 FAIL → sửa rồi QC lại
> ```
>
> **⛔ KHÔNG ĐƯỢC tự PASS mà không đọc lại nội dung. Phải confirm từng mục cho CẢ 2 câu hỏi.**

---

### 🔒 GATE 2→3 — KHÔNG QUA = KHÔNG ĐƯỢC ĐÁNH GIÁ CHECKLIST

Trước khi vào BƯỚC 3 (đánh giá 34 mục checklist), agent PHẢI cam kết:

- [ ] **TÔI SẼ kiểm tra ĐẦY ĐỦ 34 mục** — không skip, không "tạm bỏ qua", không "mục này hiển nhiên PASS"
- [ ] **TÔI SẼ đọc lại HTML + CSV thực tế** trước khi tick mục — KHÔNG dựa vào "tôi đoán/nhớ"
- [ ] **TÔI SẼ log explicit PASS/FAIL** cho từng mục với evidence (số ký tự, dòng nội dung, trích dẫn)
- [ ] **TÔI SẼ KHÔNG markup hàng loạt PASS** — phải đánh giá độc lập từng mục
- [ ] **TÔI SẼ đặc biệt cẩn thận** mục self-solve (BẮT BUỘC giải lại bài từ đầu, không nhìn correct_answer)

❌ Bất kỳ cam kết nào CHƯA tick → quay lại BƯỚC 2 (đọc lại checklist instructions).
✅ Khi 5/5 tick → log `GATE 2→3 PASSED — bắt đầu đánh giá 34 mục checklist`.

---

### BƯỚC 3: ⛔ CHECKLIST — TẤT CẢ PHẢI PASS

> **Quy tắc: 1 FAIL = chưa xong. Sửa → QC lại từ đầu → lặp đến khi ALL PASS.**
> **Tổng: 34 checks ở 4 phần (A HTML + AB balance 13, B content 6, C questions/answers + C2 verify 11, D integrated-compare coverage 4).**

#### PHẦN A: HTML + A/B BALANCE (13 checks)

Agent đọc lại file HTML và kiểm tra:

| # | Check | Cách verify | PASS nếu |
|---|-------|-------------|----------|
| 1 | **Scope level** | Đọc filename `{LEVEL}_...` | Level ∈ {N1, N2}. **N3/N4/N5 = FAIL ngay, không apply** |
| 2 | **Char count (tổng A+B)** | Chạy `process_html.py --count-only --file ...` | Trong Target Range: N1 600-750, N2 600-800 |
| 3 | **Không Hard Reject** | So với Hard Reject threshold | ≥ 570 (cả 2 level) |
| 4 | **A/B balance** | Đếm chars riêng mỗi `<section>` + tính tỷ lệ | Mỗi đoạn 40–60% tổng; chênh lệch ≤ 30% |
| 5 | **2 sections A và B** | Xem HTML structure | Có `<section class="passage-a">` + `<section class="passage-b">` (HOẶC 3 sections advice: 相談者+回答者Ａ+回答者Ｂ) |
| 6 | **Nhãn A/B hiển thị** | Xem HTML | Mỗi section có `<span class="label">A</span>` / `<span class="label">B</span>` (hoặc 相談者 / 回答者Ａ / 回答者Ｂ) |
| 7 | **Flow text** | Tìm `。<br>` trong HTML | Không có `。<br>` nào (dùng `<p>` thuần) |
| 8 | **Container CSS** | Xem CSS | `max-width: 780px`, `margin: 0 auto`, `padding: 40px 20px`, `line-height: 1.9`, `word-break: keep-all` |
| 9 | **White section background** | Xem CSS | `.passage-a`, `.passage-b` có `background: white`, border `#e5e7eb`, border-radius 6px |
| 10 | **Paragraph count per section** | Đếm `<p>` trong mỗi section | Mỗi section 2–4 `<p>` (bài ngắn, súc tích) |
| 11 | **Furigana format** | Tìm ngoặc `漢字(かんじ)` hoặc `漢字【かんじ】` | Không có — tất cả furigana dùng `<ruby><rt>` |
| 12 | **Ruby có `<rt>` không rỗng** | Xem mọi `<ruby>...</ruby>` | Tất cả đều có `<rt>` chứa furigana **không rỗng** (vd `<ruby>未曾有<rt>みぞう</rt></ruby>`). CẤM `<ruby>未曾有</ruby>` (thiếu rt) hoặc `<ruby>未曾有<rt></rt></ruby>` (rt rỗng). Auto-check: `process_html.py --validate` |
| 13 | **Ruby count đúng level** | Đếm `<ruby>` | N1 ≤ 3, N2 ≤ 5. Ưu tiên 0 (data gốc = 0%) |

#### PHẦN B: NỘI DUNG & TỪ VỰNG (6 checks)

| # | Check | Cách verify | PASS nếu |
|----|-------|-------------|----------|
| 14 | **Chủ đề đúng level** | Đọc nội dung, đối chiếu R1 | N1: triết học/văn hóa/xã luận cao cấp. N2: văn hóa đời sống/công nghệ/giáo dục/môi trường |
| 15 | **A và B CÙNG topic** | So 2 đoạn | A và B bàn về CÙNG 1 vấn đề (VD AI; SNS; giáo dục), chỉ khác quan điểm/góc nhìn |
| 16 | **A ↔ B có relationship rõ** | Đọc 2 đoạn | Xác định được: contrast / complement / debate / advice. Không được A và B nói 2 chủ đề không liên quan |
| 17 | **Không mơ hồ (test 2 cách hiểu)** | Đọc từng câu, thử hiểu theo cách 2 | Chỉ có DUY NHẤT 1 cách hiểu hợp lý cho từng câu hỏi |
| 18 | **Từ vựng đúng level** | Đọc từng từ, đối chiếu R3 | Key terms ≤ level, không dùng ngữ pháp vượt level. N1 văn luận thuyết cao cấp (`～にほかならない`/`～ざるを得ない`). N2 formal trung cấp (`～に伴い`/`～を踏まえて`) |
| 19 | **Furigana đúng từ (tra CSV)** | Tra từng kanji trong `rules/kanji_jlpt_sensei.csv` | Mọi từ có kanji vượt level đều có `<ruby><rt>`. Không thừa furigana cho từ đúng level. Không dạng "Ab" (構ちく) |

#### PHẦN C: CÂU HỎI & ĐÁP ÁN (11 checks — áp dụng cho TỪNG câu hỏi)

Agent đọc TOÀN BỘ 2 câu hỏi + 4 đáp án từ CSV và đánh giá từng câu (Q1, Q2):

| # | Check | Cách verify | PASS nếu |
|----|-------|-------------|----------|
| 20 | **Số câu hỏi đúng level** | Xem CSV đếm slot đã fill | Cả N1 và N2: Q1+Q2 có content, Q3+Q4+Q5 empty |
| 21 | **Label CỐ ĐỊNH (cả 2 câu)** | Xem `question_label_1` + `question_label_2` | **CẢ 2** phải là `question_comprehensive_understanding`. KHÔNG label nào khác |
| 22 | **Q2 compare A vs B (BẮT BUỘC)** | Đọc Q2 | Q2 test tích hợp 2 đoạn (có cụm `AとB`, `AもBも`, `AとBで共通`, `AとBの違い` hoặc tương đương). **Cấm Q2 chỉ về A, chỉ về B, hoặc kiến thức ngoài bài** |
| 23 | **Q1 và Q2 test khía cạnh khác nhau** | So nội dung Q1 vs Q2 | Q1 ≠ Q2 về khía cạnh: VD Q1 common → Q2 compare difference; Q1 focus 1 đoạn → Q2 compare tổng thể |
| 24 | **Marker khớp câu hỏi (nếu có)** | So marker trong HTML với câu hỏi | Nếu Q1 có marker (`①...とあるが`): HTML phải có `<span class="marker">①</span>` trong A hoặc B. **Q2 KHÔNG có marker** (vì compare tổng thể) |
| 25 | **Answer format (mỗi câu)** | Xem 4 đáp án trong CSV | Đúng 4 options ngăn cách `\n`, KHÔNG `1.`/`①`/`1)` prefix. Độ dài tương đương (ratio < 2.0) |
| 26 | **correct_answer (mỗi câu + batch)** | Xem giá trị `correct_answer_i` | Integer 1-4. Scan batch: không lặp cùng vị trí ≥ 3 bài liên tiếp |
| 27 | **Paraphrase đáp án đúng (mỗi câu)** | So đáp án đúng với bài gốc | KHÔNG trùng cụm ≥ 4 từ liên tiếp (N1) hoặc ≥ 5 từ (N2) |
| 28 | **Distractor đa dạng bẫy (mỗi câu)** | Phân loại 3 distractor | Đa dạng ≥ 3 loại (6 loại: Role reversal A/B / Single-side / Mix A+B / Scope / Extreme / Extraneous). **Q2 BẮT BUỘC ≥ 2 distractor dạng Role reversal HOẶC Single-side** |
| 29 | **Distractor có căn cứ trong bài (mỗi câu)** | Với mỗi đáp án sai: trích được câu/vị trí trong A hoặc B để bác bỏ | KHÔNG bịa. Mỗi distractor dùng info/concept từ bài nhưng sai ngữ cảnh |
| 30 | **Explanations 3 phần (mỗi câu)** | Đọc `explain_vn_i` + `explain_en_i` | Có đủ 3 phần: đáp án đúng (trích A + B cho Q2) + đáp án sai (nêu loại bẫy, đặc biệt Role reversal) + tóm tắt. Cả VN và EN đầy đủ |

#### PHẦN C2: VERIFY ĐÁP ÁN (⛔ QUAN TRỌNG NHẤT) — 2 checks

> **Agent tự giải từng câu từ đầu — KHÔNG nhìn đáp án đã gen.**
> Đây là bước bắt lỗi distractor bịa, câu hỏi ambiguous, sai `correct_answer`, đặc biệt distractor đảo vai A/B.

| # | Check | Cách verify | PASS nếu |
|----|-------|-------------|----------|
| 31 | **Tự giải Q1 + Q2** | Đọc A + B + từng câu hỏi, tự chọn đáp án từ đầu (KHÔNG nhìn `correct_answer_i`) | CẢ 2 kết quả tự chọn KHỚP với `correct_answer_i` trong CSV |
| 32 | **Distractor self-test (toàn bộ câu)** | Với TỪNG đáp án sai trong TỪNG câu: trích dẫn chính xác câu/vị trí trong A hoặc B dùng để bác bỏ. Kiểm tra distractor Role reversal: thứ tự chủ thể trong distractor phải ngược với bài | Mọi distractor đều trích được. Không trích được = BỊA → FAIL |

#### PHẦN D: INTEGRATED-COMPARE COVERAGE (2 checks)

> **Đặc biệt quan trọng cho đọc hiểu tổng hợp**: Q2 phải compare tổng thể 2 đoạn, Q1 + Q2 không trùng khía cạnh.

| # | Check | Cách verify | PASS nếu |
|----|-------|-------------|----------|
| 33 | **Q2 tích hợp cả A và B** | Xác định đáp án đúng Q2 có dựa trên cả A và B | Đáp án đúng Q2 PHẢI cần info từ CẢ A + B để chọn. Nếu chỉ cần A hoặc chỉ cần B → FAIL |
| 34 | **Common thread rõ ràng** | Xác định được điểm chung / điểm khác giữa A và B | Có thể tóm tắt trong 1 câu: "A và B cùng ... nhưng khác ở ..." HOẶC "A cho rằng X, B cho rằng Y". Nếu A và B không có relationship rõ → FAIL |

---

### 🔒 GATE 3→4 — KHÔNG QUA = KHÔNG ĐƯỢC SỬA

Sau khi đánh giá 34 mục, agent PHẢI confirm trước khi vào fix loop:

- [ ] Đã hoàn tất đánh giá ĐẦY ĐỦ 34/34 mục (không thiếu mục nào)
- [ ] Đã liệt kê **chính xác** danh sách các mục FAIL (số mục + lý do FAIL)
- [ ] Mỗi FAIL có **diagnosis cụ thể** (sửa cái gì, ở đâu, theo rule nào)
- [ ] Phân biệt rõ **fix HTML** (cần `--refresh` CSV sau) vs **fix CSV** (chỉ cần `fill_qa.py`) vs **fix Q&A logic** (gen lại distractor)

> **🚨 LƯU Ý ĐẶC BIỆT:**
> - Nếu **≥ 50% mục FAIL** → bài này hỏng tổng thể → **GEN LẠI TỪ ĐẦU** (giữ `_id`), KHÔNG fix vá
> - Nếu **mục #25/#26 (self-solve) FAIL** → đáp án có vấn đề logic → BẮT BUỘC review lại bài + Q+A, có thể GEN LẠI
> - Nếu **char count FAIL > Hard Reject** → GEN LẠI HOÀN TOÀN (giữ `_id`)

❌ Bất kỳ item nào CHƯA tick → quay lại BƯỚC 3 đánh giá lại.
✅ Khi 4/4 tick → log `GATE 3→4 PASSED — fix list: [#x, #y, #z] với diagnoses` rồi sang BƯỚC 4.

---

### BƯỚC 4: SỬA & LẶP LẠI

> **⛔ Khi sửa HTML, CẬP NHẬT CSV — chạy lại `process_html.py --refresh` để cập nhật `text_read`, `jp_char_count` trong CSV.**
>
> **🚨 ĐẶC BIỆT khi sửa `<ruby>` thiếu/rỗng `<rt>`:** Đây là lỗi PHỔ BIẾN — agent hay chỉ sửa HTML mà QUÊN refresh CSV → CSV cột `text_read` vẫn chứa ruby hỏng → AI fine-tuning data BỊ HỎNG.
> Workflow BẮT BUỘC khi sửa ruby:
> 1. Sửa HTML: thay `<ruby>未曾有</ruby>` → `<ruby>未曾有<rt>みぞう</rt></ruby>`
> 2. **BẮT BUỘC** chạy: `python3 .claude/skills/jlpt-reading-integrated/scripts/process_html.py --refresh --html-dir assets/html/doc_hieu_tong_hop --csv sheets/samples_v1.csv`
> 3. Verify: `python3 .claude/skills/jlpt-reading-integrated/scripts/process_html.py --validate --html-dir assets/html/doc_hieu_tong_hop --csv sheets/samples_v1.csv` — output PHẢI có dòng `✅ CSV ...: 0 row với broken ruby`. Nếu vẫn báo `🚫 CSV ... có N row với broken ruby` → CSV chưa sync, chạy lại `--refresh`.
>
> Không có screenshot nên KHÔNG cần chạy lại screenshot script.

| Nếu FAIL | Hành động | Sau đó |
|-----------|-----------|--------|
| #1 (scope level) | Level sai → REJECT, không gen lại — đọc hiểu tổng hợp chỉ có N1/N2 | Không tiếp tục |
| #2, #3 (chars) | Bổ sung/cắt nội dung. Nếu Hard Reject → gen lại hoàn toàn | Chạy `--refresh` → QC lại |
| #4 (A/B balance) | Cân bằng 2 đoạn (đoạn quá ngắn bổ sung, đoạn quá dài cắt) | Chạy `--refresh` → QC lại |
| #5, #6 (sections/label A/B) | Sửa HTML: thêm `<section class="passage-a\|b">` + `<span class="label">A\|B</span>` | Chạy `--refresh` → QC lại |
| #7 (flow text) | Sửa `<br>` → `</p><p>` | Chạy `--refresh` → QC lại |
| #8, #9 (CSS/structure) | Sửa CSS (780px, 40px 20px, line-height 1.9) + background/border | Chạy `--refresh` → QC lại |
| #10 (paragraph count) | Chia/gộp paragraph đạt 2–4 per section | Chạy `--refresh` → QC lại |
| #11, #12, #13 (ruby) | Sửa ruby tags (tra lại `rules/kanji_jlpt_sensei.csv`). Ưu tiên thay từ thay vì rắc furigana | Chạy `--refresh` → QC lại |
| #14-#16 | Gen lại nội dung (giữ _id): đảm bảo A/B cùng topic + quan điểm khác + relationship rõ | Chạy `--refresh` → QC lại |
| #17 (mơ hồ) | Sửa từ ngữ câu có 2 cách hiểu | Chạy `--refresh` → QC lại |
| #18 (từ vựng) | Thay từ/ngữ pháp về đúng level | Chạy `--refresh` → QC lại |
| #19 (furigana tra CSV) | Sửa ruby tags | Chạy `--refresh` → QC lại |
| #20 (số câu hỏi) | Thêm/xóa câu bằng `fill_qa.py` để đúng 2 slot | QC lại |
| #21 (label cố định) | Sửa label trong `fill_qa.py` về `question_comprehensive_understanding` cho cả 2 câu | QC lại |
| #22 (Q2 compare) | **Viết lại Q2 để test A vs B** — dùng `AとB`/`AもBも`/`AとBで共通`/`AとBの違い` | QC lại |
| #23 (Q1 trùng Q2) | Viết lại Q1 hoặc Q2 để test khía cạnh khác | QC lại |
| #24 (marker ko khớp) | Thêm/bớt marker trong HTML hoặc sửa câu hỏi. Q2 không được có marker | Chạy `--refresh` nếu sửa HTML → QC lại |
| #25, #26, #27 (đáp án) | Sửa đáp án bằng `fill_qa.py` | QC lại |
| #28 (distractor bẫy) | Viết lại distractor dùng 6 loại bẫy. **Q2 phải có ≥ 2 Role reversal / Single-side** | QC lại |
| #29 (distractor bịa) | Viết lại distractor dùng info thật từ A hoặc B | QC lại |
| #30 (explanation) | Viết lại explain 3 phần đầy đủ cho từng câu, trích dẫn A + B cho Q2 | QC lại |
| #31, #32 (self-solve + distractor) | Đáp án có thể sai → xem lại bài vs. đáp án, đặc biệt kiểm tra Role reversal | Sửa đáp án hoặc bài. QC lại |
| #33 (Q2 không tích hợp) | **Viết lại Q2 để cần CẢ A + B để trả lời** | QC lại |
| #34 (common thread yếu) | Gen lại A hoặc B để có relationship rõ hơn | Chạy `--refresh` → QC lại |

**Lệnh refresh CSV sau khi sửa HTML:**
```bash
python3 .claude/skills/jlpt-reading-integrated/scripts/process_html.py \
  --refresh \
  --file assets/html/doc_hieu_tong_hop/{LEVEL}_{uuid}.html \
  --csv sheets/samples_v1.csv
```

> **Vòng lặp BẮT BUỘC: sửa → refresh CSV (nếu sửa HTML) → quay lại BƯỚC 2 (QC lại TẤT CẢ 34 mục TỪ ĐẦU, KHÔNG chỉ check mục đã FAIL) → nếu còn FAIL thì lặp lại.**
> **Tối đa 5 vòng. Sau 5 vòng vẫn FAIL → báo lỗi cho user, KHÔNG bỏ qua, KHÔNG sang bài tiếp.**
>
> **🚨 CẤM TUYỆT ĐỐI:**
> - Mark "đủ tốt rồi" khi còn ≥ 1 FAIL
> - Bỏ qua mục FAIL với lý do "minor"
> - Sang bài tiếp khi bài hiện tại chưa ALL PASS
> - QC lại chỉ mục đã sửa mà không check lại 34 mục (vì sửa 1 chỗ có thể làm vỡ chỗ khác)

### 🔒 GATE 4→5 — KHÔNG QUA = KHÔNG ĐƯỢC HOÀN THÀNH

Trước khi log "ALL PASSED", agent PHẢI confirm:

- [ ] Đã chạy QC checklist 34 mục TRỌN VẸN ở vòng cuối (không skip)
- [ ] **TẤT CẢ 34/34 mục đều PASS** (không có FAIL nào, không có "skip", không có "n/a")
- [ ] Nếu có sửa HTML trong loop → đã chạy `process_html.py --refresh` để sync CSV
- [ ] Đã chạy `process_html.py --validate` cho file hiện tại — KHÔNG có broken ruby trong cả HTML lẫn CSV
- [ ] Self-solve thực sự thực hiện: agent tự giải bài + chọn đáp án mà không nhìn correct_answer → KHỚP

❌ Bất kỳ item nào CHƯA tick → quay lại BƯỚC 4 sửa tiếp.
✅ Khi 5/5 tick → cho phép sang BƯỚC 5.

---

### BƯỚC 5: ✅ HOÀN THÀNH → BÀI TIẾP THEO

Chỉ khi **TẤT CẢ 34 checks PASS + GATE 4→5 PASSED** → log:
```
🎉 ALL PASSED (34/34) — {_id} hoàn thành — 2 câu hỏi (comprehensive_understanding × 2)
GATE 4→5 PASSED — bài này hoàn tất, sang bài tiếp.
```
→ Chuyển sang bài tiếp theo (quay lại GATE 0→1 nếu là bài đầu batch, hoặc BƯỚC 1 nếu cùng batch).

**Batch size**: 5 bài/lần (bài ngắn 600-800 chars, structure đơn giản 2 sections).

---

## BƯỚC CUỐI: VERIFY BATCH (sau khi gen xong TẤT CẢ bài)

Sau khi hoàn thành toàn bộ batch, chạy verify toàn bộ:

```bash
# 1. Validate tất cả file HTML (char count + A/B balance + broken ruby)
python3 .claude/skills/jlpt-reading-integrated/scripts/process_html.py \
  --validate --html-dir assets/html/doc_hieu_tong_hop

# 2. Đếm số rows trong CSV + check số câu hỏi + label CỐ ĐỊNH rule
python3 -c "
import csv
expected_q = {'N1': 2, 'N2': 2}
FIXED_LABEL = 'question_comprehensive_understanding'
with open('sheets/samples_v1.csv', 'r', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))
print(f'Total rows: {len(rows)}')
bad = 0
for r in rows:
    lv = r.get('level')
    if lv not in expected_q:
        continue
    want = expected_q[lv]
    got = sum(1 for i in range(1, 6) if r.get(f'question_{i}', '').strip())
    if got != want:
        bad += 1
        print(f\"  ❌ {r['_id']} ({lv}): {got} câu, expected {want}\")
        continue
    bad_lbl = False
    for i in range(1, want + 1):
        lbl = r.get(f'question_label_{i}', '')
        if lbl != FIXED_LABEL:
            bad += 1
            bad_lbl = True
            print(f\"  ❌ {r['_id']} ({lv}): câu {i} label = {lbl}, expected {FIXED_LABEL}\")
            break
print(f'Multi-question + label OK: {len(rows) - bad}/{len(rows)}')
for level in ['N1','N2']:
    n = sum(1 for r in rows if r.get('level') == level)
    print(f'  {level}: {n}')
"
```

### Batch-level checklist

- [ ] Mỗi bài có `_id` unique, đúng format `{LEVEL}_{uuid}`, Level ∈ {N1, N2}
- [ ] `kind` = `đọc hiểu tổng hợp` trong tất cả rows
- [ ] `level` chỉ là N1 hoặc N2 (KHÔNG có N3/N4/N5)
- [ ] `general_image` = `""` (empty) — KHÔNG có PNG
- [ ] `general_audio` = `""` (empty)
- [ ] Char count (tổng A+B) trong Target Range (N1:600-750, N2:600-800)
- [ ] Không bài nào dưới Hard Reject threshold (570)
- [ ] **A/B balance ≤ 30%** — mỗi đoạn 40–60% tổng chars
- [ ] Bài có 2 sections A + B (hoặc 3 sections advice 相談者+回答者Ａ+回答者Ｂ)
- [ ] Mỗi section có `<span class="label">A|B</span>` (hoặc nhãn advice)
- [ ] Paragraph per section 2–4 `<p>`
- [ ] Furigana chỉ cho từ vượt level, không dạng "Ab", mọi `<ruby>` có `<rt>`
- [ ] Ruby tags count ≤ expected (N1:3, N2:5). Ưu tiên 0.
- [ ] **Mỗi bài có đúng 2 câu hỏi** (cả N1 và N2) — Q3, Q4, Q5 slot empty
- [ ] **Cả Q1 và Q2 có `question_label` = `question_comprehensive_understanding`** (CỐ ĐỊNH cho toàn dạng này)
- [ ] **Q2 BẮT BUỘC compare A vs B** (không chỉ về A, không chỉ về B)
- [ ] Q1 và Q2 test 2 khía cạnh khác nhau
- [ ] Mỗi câu hỏi có 4 đáp án ngăn cách `\n` (KHÔNG số thứ tự)
- [ ] `correct_answer_i` phân bố đều 1-4 trong batch
- [ ] Distractor dùng info từ bài (không bịa), đa dạng 6 loại bẫy
- [ ] **Q2 có ≥ 2 distractor dạng Role reversal A/B hoặc Single-side**
- [ ] `explain_vn_i` + `explain_en_i` đủ 3 phần cho cả 2 câu
- [ ] Q2 explanation trích dẫn CẢ A + B để chứng minh đáp án đúng
- [ ] Bài có **A ↔ B relationship rõ ràng** (contrast/complement/debate/advice)
- [ ] A và B CÙNG topic, khác quan điểm/góc nhìn
- [ ] `text_read` clean — không attribute, không class, không `<rt>` content
- [ ] `<p>` thuần, không `<br>` giữa câu, không `<table>`
- [ ] Trong batch, tag đa dạng ≥ 2 category (nếu batch > 3)
- [ ] Trong batch, relationship types đa dạng ≥ 2 loại (contrast/complement/debate/advice)

---

## Reference Data & Samples

Data mẫu có sẵn trong `data/`:

| Level | File | Samples |
|-------|------|---------|
| N1 | `doc_hieu_tong_hop_n1_clean.json` | 21 |
| N2 | `doc_hieu_tong_hop_n2_clean.json` | 37 |

N3, N4, N5 **KHÔNG CÓ** file data cho đọc hiểu tổng hợp — không applicable.

Load bằng:
```bash
# Stats N1/N2
python3 .claude/skills/jlpt-reading-integrated/scripts/load_references.py --stats

# 2 random samples N1
python3 .claude/skills/jlpt-reading-integrated/scripts/load_references.py --level N1 --count 2
```

**LƯU Ý khi đọc data gốc**:
- Data gốc N1 100% có A/B labels, N2 62% — skill LUÔN dùng `<section class="passage-a\|b">` với `<span class="label">`.
- Data gốc N2 `<table>` 27% — legacy noise. Skill KHÔNG dùng `<table>` (dùng `<section>`).
- Data gốc `<br>` N1:28%, N2:13% — thói quen xấu. Output HTML skill dùng `<p>` thuần.
- Data gốc N1 95% có 2 câu (khớp spec). N2 59% có 2 câu, 38% có 3 câu — skill FOLLOW SPEC (2 câu) không bắt chước data 3q.
- Data gốc ruby = 0% cả 2 level — skill giữ ruby cực ít (ưu tiên 0).
- Data gốc source line N1:4%, N2:0% — skill KHÔNG dùng source line.
- Data gốc annotation 注 N1:4%, N2:0% — skill hiếm khi dùng.
- Advice format (相談者/回答者) chỉ có ~5% data N2 — optional, mỗi batch ≤ 1 bài.

Chi tiết phân tích từng level xem `references/sample-analysis.md`.

---

## Common errors (dạng đọc hiểu tổng hợp hay gặp)

1. **Gen level ngoài N1/N2** — SAI, skill này CHỈ N1/N2 (spec JLPT đọc hiểu tổng hợp không có N3/N4/N5)
2. **Gen 1 hoặc 3 câu** — SAI, đọc hiểu tổng hợp = đúng 2 câu cho cả 2 level
3. **Dùng label khác `question_comprehensive_understanding`** — SAI. CẢ 2 câu đều phải là label này
4. **Cả 2 câu chỉ về A hoặc chỉ về B** — SAI. **Q2 PHẢI compare A vs B**
5. **Q1 và Q2 trùng khía cạnh** — SAI, phải test 2 aspects khác nhau
6. **Char count < 570**: bài quá ngắn — gen lại từ đầu
7. **A/B chênh lệch > 30%**: 1 đoạn quá dài — cân bằng lại
8. **Chỉ có 1 đoạn (không có A và B)** — SAI. Phải có cả 2 sections
9. **A và B nói chủ đề khác nhau** — SAI. A và B PHẢI cùng topic, chỉ khác quan điểm/góc nhìn
10. **Dùng `<table>` cho layout** — KHÔNG, dùng `<section class="passage-a\|b">`
11. **Dùng `<br>` giữa câu** — KHÔNG, dùng `<p>` thuần
12. **Thiếu nhãn A/B** — phải có `<span class="label">A</span>` / `<span class="label">B</span>`
13. **Distractor weak** — thiếu dạng "Role reversal A/B" hoặc "Single-side". Q2 BẮT BUỘC có ≥ 2
14. **Q2 dùng marker ①②** — SAI, Q2 compare tổng thể, không marker
15. **Quên `question_` prefix trong label** — label phải là `question_comprehensive_understanding` (đủ prefix)
16. **Q2 có thể trả lời chỉ bằng A hoặc chỉ bằng B** — SAI, Q2 PHẢI cần cả 2 đoạn
17. **A và B không có relationship rõ** — SAI. Phải contrast / complement / debate / advice
18. **Abuse ruby (> 3 N1, > 5 N2)** — đọc hiểu tổng hợp thực tế gần như không có ruby. Ưu tiên 0

---

## Cảnh báo bảo mật dữ liệu

> **🚫 KHÔNG ĐƯỢC GHI VÀO THƯ MỤC `rules/`** — `rules/question_sheet.csv`, `rules/topic.json`, `rules/kanji_jlpt_sensei.csv`, `rules/question_format.json`, `rules/kind_mission_mapping.json`, `rules/mission.json`, `rules/rule_doc_hieu.md` là file tham chiếu, chỉ đọc. Mọi dữ liệu gen phải ghi vào `sheets/samples_v1.csv`.
