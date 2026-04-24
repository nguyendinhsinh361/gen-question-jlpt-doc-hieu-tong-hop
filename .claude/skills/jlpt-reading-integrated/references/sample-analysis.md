# Sample Analysis — Đọc Hiểu Tổng Hợp Reference Data

Phân tích định lượng dữ liệu mẫu thực tế ở `data/doc_hieu_tong_hop_n{1,2}_clean.json` để gen agent biết **chính xác** độ dài, số câu hỏi, và pattern HTML cho N1/N2.

Số liệu chạy bằng `load_references.py --stats` + phân tích regex HTML của `general_text_read`.

## 0. Scope — CHỈ N1 & N2

| Level | Có "đọc hiểu tổng hợp"? | Spec (từ `question_format.json`) |
|-------|-------------------------|----------------------------------|
| N1    | ✅                      | `question_parent=1, question_child=2` — test comparison and integration |
| N2    | ✅                      | `question_parent=1, question_child=2` — test comparison and integration |
| N3    | ❌                      | Spec JLPT không có `đọc hiểu tổng hợp` ở N3 |
| N4    | ❌                      | — |
| N5    | ❌                      | — |

Skill này chỉ handle N1 và N2.

## 1. Phân Bố Độ Dài (`jp_char_count` — tổng A + B)

| Level | Samples | Min | P25 | P50 | P75 | Avg | Max  |
|-------|---------|-----|-----|-----|-----|-----|------|
| N1    | 21      | 600 | 626 | 652 | 697 | 665 | 804  |
| N2    | 37      | 604 | 615 | 644 | 778 | 705 | 1021 |

**Kết luận**:
- **N1 target** = 600–750 (P25-P75 = 626-697, bao hơn 50% data; leave buffer up to P75+50)
- **N2 target** = 600–800 (P25-P75 = 615-778, bao > 50% data)
- **Hard reject**: Cả 2 level `< 570` (dưới min data 600/604 có buffer 30+)
- N1 max=804, N2 max=1021 là outlier — skill cho phép đến HI+100 = 850 (N1) / 900 (N2), quá nữa = OVER_TARGET

## 2. Số Câu Hỏi Per Sample

| Level | 1q | 2q | 3q | Dominant vs Spec |
|-------|-----|-----|-----|------------------|
| N1    | 0  | **20 (95%)** | 1 (5%) | Khớp spec — 2q |
| N2    | 1 (3%) | **22 (59%)** | 14 (38%) | Data mixed; spec = 2q, skill FOLLOW SPEC |

**Mismatch giữa data & spec**:
- `rules/question_format.json` spec: **Cả N1 và N2 = 2 câu**
- N1 data khớp spec (95%)
- N2 data có noise 3q (legacy dataset — đề cũ ghép thêm câu). **Skill FOLLOW SPEC**.

## 3. Pattern HTML Phổ Biến

| Pattern | N1 (21) | N2 (37) |
|---------|---------|---------|
| Có A/B labels | **100%** | 62% |
| Có `<p>` | ~100% | ~95% |
| Có `<br>` | 28% | 13% |
| Có `<span>` | 0% | **45%** |
| Có `<u>` underline | 0% | 5% |
| Có `<ruby>` | **0%** | **0%** |
| Có `(中略)` | 23% | 10% |
| Có source `(...による)` | 4% | 0% |
| Có `<table>` | 0% | **27%** |
| Có 相談者 | 0% | 5% |
| Có 回答者 | 0% | 5% |
| Có ①② marker | 0% | 24% |
| Có 注1/2 | 4% | 0% |

### Nhận Xét Quan Trọng

1. **A/B labels 100% N1** — N1 hầu như luôn chỉ là `<p>A</p><p>...text A...</p><p>B</p><p>...text B...</p>`. Cực kỳ uniform.

2. **`<table>` N2 = 27%** — legacy noise. Bài N2 cũ export bọc từng đoạn trong `<table><tbody><tr><td>`. Skill KHÔNG dùng `<table>` — thay bằng `<section>` + CSS border.

3. **`<span>` N2 = 45%** — phần lớn là span wrappers trong JSON export (từng từ bọc trong `<span>`), không phải styling. Skill chỉ dùng `<span class="label">` và `<span class="marker">`.

4. **`<ruby>` furigana 0% cả 2 level** — bài ngắn, ít từ khó. Skill hạn chế tối đa (N1: 0-3, N2: 0-5).

5. **`相談者` / `回答者` N2 = 5%** — advice format xuất hiện ở N2, rất hiếm ở N1 (0%). Đây là biến thể hợp lệ (3 sections).

6. **Marker ①② N2 = 24%** — đôi khi N2 có câu hỏi trỏ đến 1 cụm cụ thể trong đoạn A. Skill cho phép 0-1 marker (chỉ khi Q1 cần reference cụ thể).

7. **`(中略)` N1 = 23%, N2 = 10%** — optional, có thể dùng khi muốn lược đoạn trung của A hoặc B.

8. **Source line gần như không có** — N1 4%, N2 0%. Skill KHÔNG dùng source line.

9. **`<br>` 13-28% data** — KHÔNG bắt chước. Dùng `<p>` thuần.

## 4. Phân Tích Cấu Trúc Q1 vs Q2

### Q1 Pattern Distribution

| Type | N1 | N2 |
|------|----|----|
| Compare AB (`AとBで共通` / `AとBはどのように`) | 19/21 (90%) | 20/37 (54%) |
| About one section only (Q1 về A hoặc B cụ thể) | 2/21 (10%) | 15/37 (41%) |
| Which (どちら) | 0 | 2/37 (5%) |

### Q2 Pattern Distribution

| Type | N1 | N2 |
|------|----|----|
| Compare AB | 19/21 (90%) | 22/37 (59%) |
| Shared/common | 1/21 (5%) | 0 |
| Which (どちら) | 0 | 4/37 (11%) |
| About one section | 1/21 (5%) | 11/37 (30%) |

### Kết Luận Về Q Pattern

- **N1 format rất uniform**: Q1 common/compare + Q2 compare — hầu như 100% bài compare
- **N2 đa dạng hơn**: Q1 có thể là single-focus (với marker ①), Q2 compare
- **Spec & skill rule**: **Q2 BẮT BUỘC compare A vs B** (cả 2 level). Q1 flexible (common hoặc single-focus với marker).

## 5. Distribution Đề Xuất Per Level

### N1 (2 câu/bài) — spec "comparison and integration"

**Combo 1** (phổ biến nhất — 80%+ nên dùng):
- Q1: `AとBで共通して述べられているのはどれか。` — điểm chung
- Q2: `XについてAとBはどのように述べているか。` — so sánh góc nhìn

**Combo 2** (đối lập rõ ràng):
- Q1: `XについてAとBはどのように述べているか。`
- Q2: `AとBの考え方の違いはどれか。`

### N2 (2 câu/bài) — spec identical N1

**Combo 1** (phổ biến nhất):
- Q1: `AとBで共通して述べられていることは何か。`
- Q2: `XについてAとBはどのように述べているか。`

**Combo 2** (marker + compare):
- Q1: `①XXXとあるが、どのようなことか。` (hỏi một cụm trong đoạn A)
- Q2: `AとBに共通する考えはどれか。` (so sánh tổng thể)

**Combo 3** (advice format — 5% data):
- Q1: `①XXX(=悩み)とは、どんな気持ちか。`
- Q2: `「相談者」に対するＡ、Ｂの回答について、正しいものはどれか。`

### Rule cứng

- **Q2 BẮT BUỘC compare A vs B** (cả 2 level). Được phép chỉ 1 bên nếu Q1 là single-focus.
- **Cả Q1 và Q2 = label `question_comprehensive_understanding`** (fixed, không exception).
- **Q1 và Q2 KHÔNG trùng nội dung** (theo spec "Các câu gen ra không được trùng nhau").

## 6. Topic Distribution Theo Data

### N1 topic phổ biến (tự phân nhóm từ 21 samples):

| Nhóm | Tỷ lệ | Ví dụ |
|------|-------|-------|
| Triết học / tâm lý / ngôn ngữ | ~40% | ノスタルジー, 運, 頭脳明晰, 「無理を承知で」, 死生観, 人間とは何か |
| Kinh tế / xã hội | ~25% | 資金調達, 起業, モノづくり, 平凡な日々 |
| Văn hóa / lịch sử | ~20% | 「令和」元号, 「バベルの塔」, 文化 |
| Khoa học / công nghệ | ~15% | — |

### N2 topic phổ biến (tự phân nhóm từ 37 samples):

| Nhóm | Tỷ lệ | Ví dụ |
|------|-------|-------|
| Văn hóa đời sống / tư vấn | ~30% | 相談 (bạn trai chọn quà), ăn uống, du lịch |
| Công nghệ / AI | ~25% | ドアの改良, 電車, スマートフォン |
| Kinh tế / công việc | ~20% | 賞味期限, 販売, 値引き |
| Giáo dục | ~15% | 学習, 勉強法 |
| Môi trường / sức khỏe | ~10% | 地球環境問題 |

**Nhận xét**: N1 thiên về abstract/triết học; N2 gần gũi đời sống hơn, có format tư vấn (相談者+回答者).

## 7. Style Cheatsheet Cho Gen Agent

```
N1 cheatsheet (21 samples):
  - Char target (tổng A+B): 600-750 (P25-P75: 626-697)
  - Mỗi đoạn: ~280-380 chars (40-60% của tổng)
  - Paragraph per section: 2-4
  - 2 câu, label cố định = question_comprehensive_understanding
  - Q1 + Q2 pattern: common/compare + compare (combo 1)
  - Pattern HTML:
    * A/B labels: 100% (BẮT BUỘC)
    * <p> only: 100%
    * marker ①②: 0% (hiếm khi dùng)
    * <ruby>: 0% (tránh tối đa)
    * (中略): 23% (optional)
    * source line: 4% (thường không cần)
    * KHÔNG dùng <br>, <table>, <span class>
  - Văn phong: formal cao, luận thuyết/phê bình,
    grammar ～いかんによらず / ～をもって / ～にほかならない / ～ざるを得ない
  - Topic: triết học, tâm lý, phê bình xã hội/văn hóa cao, kinh tế

N2 cheatsheet (37 samples):
  - Char target (tổng A+B): 600-800 (P25-P75: 615-778)
  - Mỗi đoạn: ~280-400 chars
  - Paragraph per section: 2-4
  - 2 câu, label cố định = question_comprehensive_understanding
  - Q1 + Q2 pattern: common/single-focus + compare
  - Pattern HTML:
    * A/B labels: 62% nhưng skill ALWAYS dùng (hoặc advice format)
    * marker ①②: 24% (optional — khi Q1 cần reference)
    * <ruby>: 0% (tránh tối đa)
    * (中略): 10% (optional)
    * 相談者/回答者: 5% (advice format variant)
    * KHÔNG dùng <br>, <table>, <span class> (ngoại trừ .label/.marker)
  - Văn phong: formal văn viết trung cấp, 2 ý kiến đối lập/bổ sung,
    grammar ～に伴い / ～を踏まえて / ～に限り / ～とはいえ
  - Topic: văn hóa đời sống, tư vấn, công nghệ vừa, giáo dục, môi trường
```

## 8. Key Takeaways

- **Đọc hiểu tổng hợp = bài ngắn (600-800 chars)** nhưng yêu cầu **2 passages có quan điểm khác nhau / bổ sung**
- **Label cố định `question_comprehensive_understanding`** — không đa dạng
- **Q2 BẮT BUỘC compare A vs B** — linh hồn của dạng này
- **N1 format rất uniform** — Q1+Q2 đều là compare
- **N2 format đa dạng** — có thêm marker ①, advice format 相談者+回答者A+B
- **A/B balance ≤ 30%** — 2 đoạn phải cân đối
- **N3/N4/N5 không có kind này** — skill hard-block các level đó
- **`<table>` N2 = 27% là legacy noise** — skill dùng `<section>` thay
