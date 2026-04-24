# HANDOVER — Đọc Hiểu Tổng Hợp Skill

Tài liệu giao/nhận cho skill **jlpt-reading-integrated** (統合理解 / đọc hiểu tổng hợp). Đọc file này trước khi chạy batch gen hoặc khi bàn giao cho team mới.

## 1. Mục đích

Gen dữ liệu huấn luyện AI cho **dạng "đọc hiểu tổng hợp"** (統合理解 / integrated-comparative) của JLPT. Mỗi bài gồm:

- **2 đoạn văn A + B** cùng chủ đề nhưng quan điểm khác nhau / bổ sung (tổng 600–800 ký tự)
- **Đúng 2 câu hỏi** multiple-choice 4 đáp án cho cả N1 và N2
- **Tất cả câu hỏi LUÔN có label `question_comprehensive_understanding`** (cố định, không có exception)
- **Câu 2 BẮT BUỘC so sánh A vs B** (điểm chung, điểm khác, hoặc góc nhìn từng bên)
- Giải thích tiếng Việt + tiếng Anh cho từng câu

**Scope hẹp — CHỈ N1 và N2**. Theo `rules/question_format.json`, N3/N4/N5 KHÔNG có kind "đọc hiểu tổng hợp", nên skill hard-block các level đó (status `UNSUPPORTED_LEVEL`, exit 1).

So với các phase trước:

| Phase | Kind | Levels | Chars | Q/bài | Container | Cấu trúc | Label |
|-------|------|--------|-------|-------|-----------|----------|-------|
| 0 | tìm thông tin | N1-N5 | varies | 1 | — (có PNG) | Ads / bảng lịch | varies |
| 1 | đoạn văn ngắn | N1-N5 | 80–290 | 1 | 640px | 1 khối ngắn | varies |
| 2 | đoạn văn vừa | N1-N5 | 250–620 | 2–3 | 720px | 1 essay ngắn | varies |
| 3 | đoạn văn dài | N1 + N3 | 550–1150 | 3–4 | 780px | 1 essay/thư dài | varies |
| 4 | đọc hiểu chủ đề | N1 + N2 | 900–1200 | 3 | 800px | 1 xã luận thuần | câu cuối fixed |
| **5** | **đọc hiểu tổng hợp** | **N1 + N2** | **600–800** | **2** | **780px** | **2 đoạn A + B** | **Tất cả fixed** |

**Đọc hiểu tổng hợp = bài NGẮN NHẤT series** (600-800 chars) nhưng yêu cầu **2 đoạn độc lập có quan điểm so sánh được**. Workload gen nhẹ nhưng quality control chặt (AB-balance, cross-passage compare question).

## 2. Cấu trúc project

```
gen-question-doc-hieu-tong-hop/
├── data/                                        # Sample JSON từ đề JLPT cũ
│   ├── doc_hieu_tong_hop_n1_clean.json          # 21 samples
│   └── doc_hieu_tong_hop_n2_clean.json          # 37 samples
├── .claude/skills/jlpt-reading-integrated/
│   ├── SKILL.md                                 # Main skill definition (~430 dòng)
│   ├── scripts/
│   │   ├── process_html.py                      # Count + A/B balance + CSV upsert (2 Q)
│   │   └── load_references.py                   # Pretty-print JSON cho gen agent
│   └── references/
│       ├── sample-analysis.md                   # Phân tích pattern N1/N2
│       └── html-patterns.md                     # HTML template 780px + section A/B
├── .gemini/skills/jlpt-reading-integrated/      # Mirror identical của .claude/
├── assets/html/doc_hieu_tong_hop/               # Output HTML files (runtime)
├── sheets/                                      # Output CSV files (runtime)
├── rules/                                       # Schema & spec
│   ├── question_sheet.csv                       # 45-col CSV header
│   ├── question_format.json                     # N1=2, N2=2
│   ├── kind_mission_mapping.json                # required_question_label
│   ├── mission.json                             # Question label catalog
│   └── topic.json
├── HANDOVER.md                                  # (file này)
└── PROMPTS.md                                   # Prompt templates cho gen agent
```

## 3. Pipeline chuẩn

### Bước 1 — Load references (calibrate style)

```bash
cd /path/to/gen-question-doc-hieu-tong-hop
python3 .claude/skills/jlpt-reading-integrated/scripts/load_references.py --stats
python3 .claude/skills/jlpt-reading-integrated/scripts/load_references.py --level N1 --count 1 --seed 42
python3 .claude/skills/jlpt-reading-integrated/scripts/load_references.py --level N2 --count 1 --seed 42
```

Gen agent đọc 1 sample cùng level để học:
- Độ dài **TỔNG A+B** (P25–P75: N1 ≈ 626–697, N2 ≈ 615–778)
- Chủ đề (N1 = triết học/tâm lý/văn hóa cao; N2 = văn hóa đời sống/công nghệ/tư vấn)
- Cấu trúc 2 đoạn A + B (mỗi đoạn 2-4 paragraph, cân đối ≤ 30%)
- Quan hệ A ↔ B: bổ sung / trái chiều / tranh luận / advice-dual

**KHÔNG bắt chước styling data gốc 100%** — data N2 có 27% `<table>` legacy noise, 45% `<span>` wrappers. Skill dùng `<section class="passage-a|b">` thay thế.

### Bước 2 — Gen HTML + câu hỏi từ LLM

LLM dùng prompt trong `PROMPTS.md` (template N1 / N2) để gen ra:

1. HTML file đầy đủ (có `<!DOCTYPE>`, Noto Sans JP CSS, `max-width: 780px`)
2. **2 `<section>` con**: A (passage-a, label xanh Ａ) và B (passage-b, label đỏ Ｂ)
3. **Đúng 2 câu** cho cả N1 và N2, mỗi câu 4 đáp án + đáp án đúng
4. Giải thích VN + EN cho từng câu
5. **Cả 2 câu LUÔN có label `question_comprehensive_understanding`** (cố định)
6. **Câu 2 BẮT BUỘC so sánh A vs B** — common / difference / which-side / compare
7. A/B char balance ≤ 30% chênh lệch
8. `(中略)` optional (N1 23%, N2 10%) — dùng khi muốn lược đoạn giữa trong A hoặc B

**Biến thể advice format (<10% data N2)**: 3 sections = `<section class="consultant">` (相談者) + `<section class="passage-a">` (回答者Ａ) + `<section class="passage-b">` (回答者Ｂ). Câu 1 thường về nội dung 相談, câu 2 so sánh 2 lời khuyên.

Output khuyến nghị ở dạng JSON file `questions.json`:

```json
{
  "questions": [
    {
      "label": "question_comprehensive_understanding",
      "question": "AとBで共通して述べられているのはどれか。",
      "answers": ["A option", "B option", "C option", "D option"],
      "correct": 1,
      "explain_vn": "...",
      "explain_en": "..."
    },
    {
      "label": "question_comprehensive_understanding",
      "question": "XについてAとBはどのように述べているか。",
      "answers": ["A", "B", "C", "D"],
      "correct": 2,
      "explain_vn": "...",
      "explain_en": "..."
    }
  ]
}
```

### Bước 3 — Save HTML

Tên file: `{LEVEL}_{uuid4().hex}.html`. Ví dụ: `N1_a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6.html`.

```python
import uuid
filename = f"N1_{uuid.uuid4().hex}.html"
```

Save vào `assets/html/doc_hieu_tong_hop/`.

### Bước 4 — Process + commit CSV (2 cách)

**Cách A (KHUYẾN NGHỊ) — JSON file chứa 2 câu hỏi**:

```bash
python3 .claude/skills/jlpt-reading-integrated/scripts/process_html.py \
    --file assets/html/doc_hieu_tong_hop/N1_abc123...html \
    --csv sheets/samples_v1.csv \
    --tag "học tập độc lập vs có giáo viên" \
    --questions-json /tmp/qs.json
```

**Cách B — CLI flags (2 câu)**:

```bash
python3 .claude/skills/jlpt-reading-integrated/scripts/process_html.py \
    --file assets/html/doc_hieu_tong_hop/N2_abc123...html \
    --csv sheets/samples_v1.csv \
    --tag "AI giáo dục vs giáo viên truyền thống" \
    --q1 "AとBで共通して..." --a1 "A|B|C|D" --c1 2 --ev1 "..." --ee1 "..." \
    --q2 "XについてAとBは..." --a2 "A|B|C|D" --c2 3 --ev2 "..." --ee2 "..."
```

Script sẽ:

- Count `jp_char_count` từ full HTML (skip `<rt>`, whitespace)
- Count **per-section chars** (A vs B) cho AB balance check
- Extract clean HTML (bỏ attribute, collapse whitespace, bỏ `<rt>`)
- **Validate level** (N1/N2 only) — block commit nếu N3/N4/N5
- **Validate đúng 2 câu** — warning nếu khác 2
- **Auto-override label** về `question_comprehensive_understanding` cho mọi câu (warning nếu input khác)
- **Validate AB balance** — warning nếu ratio > 30%, error nếu không detect được A/B
- **Hard-reject** nếu dưới 570 (cả 2 level) — exit 1, không commit CSV
- Cảnh báo nếu dưới Target Range hoặc vượt xa Target (> hi + 100)
- Upsert row vào CSV (45 columns) theo `_id` = filename, populate `question_1..question_2`, còn lại `""`

### Bước 5 — Validate batch

```bash
python3 .claude/skills/jlpt-reading-integrated/scripts/process_html.py \
    --validate --html-dir assets/html/doc_hieu_tong_hop
```

Exit 0 = tất cả pass; 1 = có file fail (UNDER_TARGET / HARD_REJECT / UNSUPPORTED_LEVEL / AB_IMBALANCE / AB_UNDETECTED).

### Bước 6 — Refresh sau khi edit HTML

Giữ câu hỏi cũ, chỉ refresh `jp_char_count` + `text_read`:

```bash
python3 .claude/skills/jlpt-reading-integrated/scripts/process_html.py \
    --refresh --html-dir assets/html/doc_hieu_tong_hop --csv sheets/samples_v1.csv
```

## 4. Target ranges & số câu (BẮT BUỘC)

| Level | Target Range (A+B) | Hard Reject | Số câu/bài | Label bắt buộc |
|-------|--------------------|-------------|-----------|----------------|
| N1    | 600–750            | < 570       | **2**     | `question_comprehensive_understanding` (cả 2 câu) |
| N2    | 600–800            | < 570       | **2**     | `question_comprehensive_understanding` (cả 2 câu) |

> **Scope hẹp**: N3, N4, N5 KHÔNG có kind này. Nếu tệp `.html` mang tên `N3_*` đi qua pipeline, script sẽ báo `UNSUPPORTED_LEVEL` và KHÔNG commit vào CSV.

> **Data vs Spec**: N1 data khớp spec (95% 2 câu, 5% 3 câu). N2 data noise (59% 2 câu, 38% 3 câu — legacy đề cũ). Skill **LUÔN follow SPEC** — cả N1 và N2 = 2 câu.

> **Q2 BẮT BUỘC compare A vs B**: Câu 2 phải test quan hệ giữa 2 đoạn:
> - Common: `AとBで共通して述べられているのはどれか。`
> - Difference: `AとBの考え方の違いはどれか。`
> - Side-by-side: `XについてAとBはどのように述べているか。`
> - Which: `AとBのどちらが...と述べているか。`
> - Advice compare: `「相談者」に対するＡ、Ｂの回答について、正しいものはどれか。`

> **A/B balance ≤ 30%**: 2 đoạn phải cân đối. Nếu A = 200 chars, B ≥ 140 và ≤ 260 (ratio ≤ 30%).

## 5. CSV Schema (45 columns)

Populate 2 câu hỏi, các cột 3-5 để trống:

| Column | Value |
|--------|-------|
| `_id`  | `{LEVEL}_{uuid32hex}` (`LEVEL` ∈ {N1, N2}) |
| `level` | N1 hoặc N2 |
| `tag`  | Topic label (ví dụ "học tập độc lập vs có giáo viên") |
| `jp_char_count` | Result `count_body_chars()` — tổng A+B |
| `kind` | Always `đọc hiểu tổng hợp` |
| `general_audio` | "" |
| `general_image` | "" (empty — no PNG) |
| `text_read` | Clean HTML (đã normalize) |
| `text_read_vn` / `text_read_en` | "" |
| `question_label_1` | `question_comprehensive_understanding` (fixed) |
| `question_1` | Câu hỏi 1 tiếng Nhật (thường về common hoặc single-focus) |
| `question_image_1` | "" |
| `answer_1` | `1. A\n2. B\n3. C\n4. D` |
| `correct_answer_1` | 1-4 |
| `explain_vn_1` / `explain_en_1` | Giải thích câu 1 |
| `question_label_2` | `question_comprehensive_understanding` (fixed) |
| `question_2` | Câu hỏi 2 tiếng Nhật (BẮT BUỘC compare A vs B) |
| `answer_2`..`explain_en_2` | Câu 2 |
| `question_label_3`..`explain_en_3` | **""** |
| `question_label_4`..`explain_en_4` | **""** |
| `question_label_5`..`explain_en_5` | **""** |

## 6. Quality Gates

Trước khi coi 1 batch là xong:

- [ ] 100% file qua Hard Reject threshold (570 cho cả 2 level)
- [ ] ≥ 80% file nằm trong Target Range
- [ ] 100% file có `level` ∈ {N1, N2}
- [ ] **100% row có ĐÚNG 2 câu hỏi** (cả N1 và N2)
- [ ] **100% `question_label_1` và `question_label_2` = `question_comprehensive_understanding`**
- [ ] **Câu 2 LUÔN so sánh A vs B** (common / difference / side-by-side / which)
- [ ] A/B balance ≤ 30% chênh lệch (nếu A < B, `A/B ≥ 0.7`)
- [ ] Cả A và B detect được từ HTML (không có `AB_UNDETECTED`)
- [ ] Q1 và Q2 KHÔNG trùng nội dung / ý
- [ ] Marker ①② trong HTML khớp với câu hỏi reference (nếu Q1 là single-focus)
- [ ] **Mỗi đoạn A hoặc B có 2–4 paragraph**
- [ ] **2 đoạn có quan điểm khác / bổ sung / tranh luận** — KHÔNG cùng hệt 1 ý
- [ ] Batch ≥ 3 bài có ≥ 2 `tag` khác nhau
- [ ] 0 file có furigana dạng "Ab" (cấm 週かん, 友だち)
- [ ] 100% file có `general_image = ""`
- [ ] 100% row có `kind = "đọc hiểu tổng hợp"`
- [ ] 0 row có `question_3`, `question_4`, hoặc `question_5` non-empty
- [ ] Mỗi câu có 4 đáp án trong `answer_X`, `correct_answer_X` là 1–4
- [ ] `explain_vn_X` + `explain_en_X` đều non-empty cho 2 câu
- [ ] 2 đoạn cùng chủ đề chung (cùng nói về X, có thể A ủng hộ, B phản biện)
- [ ] Source line: không dùng tên thật (data Phase 5 gần như 0% có source line)

## 7. Edge cases & pitfalls

1. **Gen 3 câu cho N2** — SAI, dù data N2 gốc 38% có 3 câu. Follow spec 2 câu.
2. **Gen 1 câu** — SAI, đọc hiểu tổng hợp **BẮT BUỘC 2 câu**.
3. **Gen bài level N3/N4/N5** — HARD-BLOCKED bởi script. N3 dài → dùng skill `jlpt-reading-long-passage` (Phase 3).
4. **Label khác `question_comprehensive_understanding`** — Script auto-override (warning). Nhưng gen agent nên gen đúng để không gây nhầm.
5. **Bài chỉ 1 đoạn** — SAI, TỔNG HỢP = 2 đoạn A + B (hoặc 3 = 相談+回答A+回答B).
6. **A và B không cùng chủ đề** — SAI, 2 đoạn phải nói về cùng 1 chủ đề X, chỉ quan điểm khác / bổ sung.
7. **A và B nói cùng 1 ý** — SAI, không có gì để compare trong Q2.
8. **A/B imbalance > 30%** — Script báo `AB_IMBALANCE`. Fix bằng thêm/bớt câu ở đoạn ngắn.
9. **Q2 không compare A vs B** — SAI. Q2 LUÔN là compare (đây là linh hồn đọc hiểu tổng hợp).
10. **Q1 và Q2 cùng test 1 ý** — SAI, 2 câu phải test 2 góc khác nhau.
11. **Dùng `<table>` bao quanh đoạn** — SAI (legacy noise 27% N2 data). Dùng `<section class="passage-a|b">`.
12. **Dùng `<br>` giữa câu** — SAI. Dùng `<p>` thuần.
13. **Marker ①② trong Q1 không có trong HTML** — SAI. Nếu Q1 ref marker, HTML phải có `<span class="marker">①</span>`.
14. **Furigana quá nhiều** — data N1 0% ruby, N2 0%. Giới hạn tối đa 3 (N1) / 5 (N2), ưu tiên 0.
15. **Char count dưới target** — chỉ 2-3 paragraph. Phải **2-4 paragraph/đoạn**, tổng ~6 paragraph.
16. **Distractor quá dễ** — distractor phải đánh lừa từ việc hiểu nhầm 1 trong 2 đoạn.
17. **Correct index conversion** — JSON `correctAnswer` là 0-based, CSV `correct_answer_X` là 1-based.
18. **Dạng "Ab" (週かん, 友だち)** — tuyệt đối không. Full kanji + ruby HOẶC full hiragana.
19. **Container width** = **780px** (giống Phase 3). Nhưng layout khác (2-section thay vì 1 essay).
20. **Advice format sai**: dùng `<section class="consultant">` cho 相談者 (label xám), `<section class="passage-a">` và `<section class="passage-b">` cho 回答者Ａ/Ｂ.
21. **Quên label `Ａ` và `Ｂ` (full-width)** trong `<span class="label">` — reader sẽ không biết đâu là A, đâu là B.

## 8. Sample patterns theo data (tóm tắt, chi tiết xem `references/sample-analysis.md`)

| Pattern | N1 (21) | N2 (37) |
|---------|---------|---------|
| Char P25–P75 (tổng A+B) | 626–697 | 615–778 |
| Char Min–Max | 600–804 | 604–1021 |
| Số câu 2 | **95%** (20/21) | 59% (22/37) |
| Số câu 3 | 5% | 38% (legacy noise) |
| Có A/B labels | **100%** | 62% |
| Có `<section>` | 0% → **skill dùng 100%** | 0% → **skill dùng 100%** |
| Có `<table>` (legacy noise) | 0% | 27% (skill KHÔNG mimic) |
| Có `<span>` wrappers | 0% | 45% (legacy, KHÔNG mimic) |
| Có `<ruby>` | 0% | 0% |
| Có `(中略)` | 23% | 10% |
| Có marker ①② | 0% | 24% |
| Có advice format (相談者) | 0% | 5% |
| Có source line | 4% | 0% |

**Key insights**:

- **N1 format CỰC KỲ uniform** — 100% có A/B label, 95% có 2 câu, hầu như luôn compare/common ở Q1+Q2.
- **N2 đa dạng hơn** — có marker (24%), advice format (5%), đôi khi Q1 là single-focus về 1 đoạn.
- **Q2 = compare** ở cả 2 level (N1 90%, N2 59% của Q2 phân bố). Skill rule cứng: Q2 LUÔN compare.
- **Ít visual elements**: 0% ruby cả 2 level, source line gần như 0%. Khác hẳn Phase 4 (N1 ruby 0 nhưng source 64%).
- **Bài ngắn** (600-800) nhưng 2 đoạn → mỗi đoạn ~280-400 chars.

## 9. Status output của process_html.py

Khi chạy `--validate` hoặc `--refresh`, mỗi file được classify:

| Status | Nghĩa | Block commit? |
|--------|-------|---------------|
| `OK` | Trong target range, AB balance OK | ❌ |
| `UNDER_TARGET` | Dưới target nhưng trên 570 | ❌ (warning only) |
| `OVER_TARGET` | Vượt xa target (> hi + 100) | ❌ (warning only) |
| `AB_IMBALANCE` | Chênh A vs B > 30% | ❌ (warning only) |
| `AB_UNDETECTED` | Không phát hiện được A và B trong HTML | ❌ (warning only) |
| `HARD_REJECT` | Dưới 570 ký tự | ✅ (exit 1) |
| `UNSUPPORTED_LEVEL` | Level không phải N1/N2 | ✅ (exit 1) |
| `UNKNOWN_LEVEL` | Tên file không match regex `^N[1-5]_[0-9a-f]{8,}\.html$` | ✅ (exit 1) |

## 10. Tương lai (post-Phase 5)

- Phase 5 là phase cuối của series 5 dạng đọc hiểu.
- Post-pipeline: bổ sung `text_read_vn` / `text_read_en` nếu cần bản dịch
- CSV consolidation: merge CSVs của 5 skill thành 1 `sheets/master.csv` để train
- Có thể thêm dạng mới: 情報検索 (advanced, ads có bảng phức tạp)

## 11. Liên hệ

- Skill owner: Nguyễn Đình Sinh <sinhnd@eupgroup.net>
- Phase trước: `../gen-question-doc-hieu-chu-de/` (đọc hiểu chủ đề, N1+N2, 3 câu)
- Phase 3: `../gen-question-doan-van-dai/` (đoạn văn dài, N1+N3)
- Phase 2: `../gen-question-doan-van-vua/` (đoạn văn vừa, 2-3 câu)
- Phase 1: `../gen-question-doan-van-ngan/` (đoạn văn ngắn, 1 câu)
- Phase 0: `../gen-question-jlpt/` (tìm thông tin, có screenshot)
- Master plan: `../PLAN_5_DANG_DOC_HIEU.md`
