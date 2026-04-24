# Rules: Nội dung & Chủ đề & Visual (R1, R2, R7, R8)

> **Scope**: Đọc hiểu tổng hợp (統合理解 / integrated / comparative comprehension) — **CHỈ N1 & N2**.
> Mỗi bài có **2 đoạn A và B** cùng chủ đề, quan điểm khác/bổ sung nhau. Mỗi bài **đúng 2 câu hỏi**.

## R1. Scope & Chủ đề

### R1.1 Level scope — CỐ ĐỊNH N1 & N2

| Level | Có "đọc hiểu tổng hợp"? | Spec (`rules/question_format.json`) |
|-------|-------------------------|--------------------------------------|
| N1    | ✅                      | `question_parent=1, question_child=2` — "so sánh và tổng hợp hai quan điểm" |
| N2    | ✅                      | `question_parent=1, question_child=2` — "so sánh và tổng hợp hai quan điểm" |
| N3    | ❌                      | Spec JLPT không có kind này ở N3 |
| N4    | ❌                      | — |
| N5    | ❌                      | — |

Skill **hard-block** N3/N4/N5 tại `EXPECTED_Q_COUNT` (argparse reject).

### R1.2 Nguyên tắc chủ đề (A và B CÙNG topic)

**BẮT BUỘC**: A và B phải bàn về **CÙNG 1 chủ đề / vấn đề**, chỉ khác quan điểm / góc nhìn / nhấn mạnh. Nếu A nói về AI, B cũng phải nói về AI (không được B nói về giáo dục).

Kiểu quan hệ A ↔ B (chọn 1):

| Kiểu | Mô tả | Ví dụ |
|------|-------|-------|
| **Contrast** (đối lập) | A ủng hộ, B phản đối hoặc ngược lại | A: "AI giúp ích giáo dục", B: "AI gây ỷ lại" |
| **Complement** (bổ sung) | A và B cùng quan điểm nhưng nhấn mạnh khía cạnh khác | A: "AI cải thiện hiệu suất", B: "AI mở rộng cơ hội sáng tạo" |
| **Debate** (tranh luận) | A đặt vấn đề, B phản biện trực tiếp với A | A: "đọc sách giấy tốt hơn", B: "đọc sách giấy đã lỗi thời" |
| **Advice** (tư vấn) | 相談者 đặt câu hỏi, 回答者A và 回答者B đưa 2 lời khuyên khác nhau | 相談者: lo lắng về con cái, A: "giới hạn smartphone", B: "tin tưởng con" |

### R1.3 Topic Catalog (cho A và B)

Topic tiếng Việt (dùng trong column `tag`):

| Nhóm | Topic labels | Level phù hợp |
|------|--------------|---------------|
| Văn hóa đời sống | `lối sống hiện đại`, `thế hệ trẻ`, `gia đình`, `văn hóa ăn uống`, `giải trí`, `du lịch` | N1, N2 |
| Công nghệ / AI | `AI và đời sống`, `công nghệ số`, `mạng xã hội`, `làm việc từ xa`, `smartphone` | N1, N2 |
| Giáo dục | `giáo dục trẻ em`, `cải cách giáo dục`, `phương pháp học`, `tiếng Anh vs tiếng Nhật` | N1, N2 |
| Môi trường / sức khỏe | `môi trường`, `ăn chay`, `tập thể dục`, `stress`, `giấc ngủ` | N2 (phổ biến) |
| Kinh tế / lao động | `khởi nghiệp`, `cân bằng công việc`, `tiền lương`, `mua nhà hay thuê` | N1, N2 |
| Tư vấn / quan hệ | `tư vấn tình yêu`, `tư vấn nghề nghiệp`, `相談者`, `ứng xử gia đình` | N2 (advice format) |
| Xã hội / phê bình | `già hóa dân số`, `bình đẳng giới`, `đa văn hóa`, `cộng đồng địa phương` | N1 (phổ biến) |
| Triết học / ngôn ngữ | `bản chất con người`, `ý nghĩa cuộc sống`, `記憶とノスタルジー`, `ngôn ngữ và xã hội` | N1 |

Batch ≥ 3 bài: chọn topic từ ≥ 2 nhóm khác nhau.

### R1.4 Tránh topic

- Topic quá cá nhân / hư cấu thuần ("bạn X của tôi đã...") — đọc hiểu tổng hợp = editorial/opinion, không narrative
- Topic nhạy cảm chính trị / tôn giáo / sắc tộc
- Topic A và B **không** cùng chủ đề (SAI — phải CÙNG topic)

---

## R2. Độ dài bài đọc & Cân bằng A/B

### R2.1 Data gốc tham khảo (`jp_char_count` tổng A + B)

| Level | Samples | Min  | P25 | P50 | P75 | Avg | Max  |
|-------|---------|------|-----|-----|-----|-----|------|
| N1    | 21      | 600  | 626 | 652 | 697 | 665 | 804  |
| N2    | 37      | 604  | 615 | 644 | 778 | 705 | 1021 |

### R2.2 Target Range (BẮT BUỘC)

| Level | Target Range (tổng A+B) | Hard Reject |
|-------|-------------------------|-------------|
| **N1** | **600 – 750** | **< 570** → gen lại |
| **N2** | **600 – 800** | **< 570** → gen lại |

Hard reject = PHẢI gen lại từ đầu, không chỉnh nhỏ.

### R2.3 Cân bằng A/B

Mỗi đoạn A và B nên chiếm **40–60%** tổng chars. Chênh lệch **≤ 30%** (A/B imbalance check):

```
imbalance = |chars_A - chars_B| / max(chars_A, chars_B)
imbalance > 0.30 → REJECT (AB_IMBALANCE)
```

Ví dụ tổng 700 chars:
- ✅ A=330, B=370 (imbalance 11%) — OK
- ✅ A=280, B=420 (imbalance 33%) — **BORDERLINE**, nên cân bằng lại
- ❌ A=200, B=500 (imbalance 60%) — SAI

### R2.4 Paragraph per section

| Level | Paragraph per section | Lý do |
|-------|------------------------|-------|
| N1    | **2 – 4** | 300-375 chars/section, nhiều paragraph fragmented |
| N2    | **2 – 4** | 300-400 chars/section |

Nếu section chỉ 1 paragraph → OK nếu bài ngắn (300 chars), nhưng ưu tiên 2-3 để readability.

### R2.5 Số câu hỏi per bài

Cả N1 và N2 = **đúng 2 câu** (spec JLPT). CSV `question_1`, `question_2` populate; `question_3..5` = "".

**Data vs Spec**:
- N1: 95% có 2 câu (20/21) — khớp spec
- N2: 59% có 2 câu (22/37), 38% có 3 câu (14/37) — **skill FOLLOW SPEC**, bỏ noise 3q

---

## R7. Các format bài (document formats)

Đọc hiểu tổng hợp có **2 format chính**:

### R7.1 Format chuẩn — 2-section A/B (90%+ dữ liệu)

```
<section class="passage-a">
    <span class="label">A</span>
    <p>Quan điểm 1 về topic.</p>
    <p>Lập luận / kết luận của A.</p>
</section>
<section class="passage-b">
    <span class="label">B</span>
    <p>Quan điểm 2 về CÙNG topic.</p>
    <p>Lập luận / kết luận của B — khác hoặc bổ sung A.</p>
</section>
```

Đặc điểm:
- Tác giả **không danh xưng** (không 筆者, không tôi)
- Văn phong luận thuyết ngắn (editorial / opinion piece)
- Mỗi section 2-4 paragraph

### R7.2 Format advice — 相談者 + 回答者A + 回答者B (~5-10% dữ liệu, N2 phổ biến hơn)

3 sections thay vì 2:

```
<section class="consultant">
    <span class="label">相談者</span>
    <p>Mô tả vấn đề / nỗi lo của người hỏi. 2-3 câu.</p>
</section>
<section class="passage-a">
    <span class="label">回答者Ａ</span>
    <p>Lời khuyên 1 từ chuyên gia/người tư vấn A.</p>
</section>
<section class="passage-b">
    <span class="label">回答者Ｂ</span>
    <p>Lời khuyên 2 từ chuyên gia/người tư vấn B — góc nhìn khác.</p>
</section>
```

Khi dùng format này:
- Q1 có thể hỏi về vấn đề của 相談者 hoặc gợi ý của 1 bên
- Q2 BẮT BUỘC so sánh Ａ vs Ｂ

Chú ý: dùng **full-width Ａ / Ｂ** (not half-width) cho format này (matching data gốc).

### R7.3 Style văn

- Văn **ngắn, súc tích** — mỗi đoạn 2-5 câu
- **Không kể chuyện / thuật sự** — đọc hiểu tổng hợp = opinion/editorial/advice
- A và B dùng first-person viewpoint implicit hoặc câu văn luận thuyết, **không có tên tác giả**
- Không có `（...による）` source line (data N1=4%, N2=0% — rare)

---

## R8. Visual Elements Rates

| Element | N1 rate | N2 rate | Khi nào dùng |
|---------|---------|---------|--------------|
| `<section class="passage-a\|b">` | **100%** | **100%** | **BẮT BUỘC** — cấu trúc A/B |
| `<span class="label">A\|B</span>` | **100%** | **100%** | **BẮT BUỘC** — nhãn A/B/相談者/回答者 |
| `<p>` | 100% | ~95% | **BẮT BUỘC** cho nội dung |
| `<u>` underline | 0% | 5% | Optional — chỉ N2 đôi khi underline 1 cụm key |
| marker `①②③` | 0% | 24% | Optional — chỉ khi Q1 tham chiếu cụm cụ thể |
| `(中略)` | 23% | 10% | **Optional** — có thể dùng trong 1 section để lược đoạn |
| 注 annotation | 4% | 0% | **Hiếm** — bài ngắn ít từ khó |
| source line | 4% | 0% | **KHÔNG nên dùng** — đọc hiểu tổng hợp không có source |
| `<ruby>/<rt>` | 0% | 0% | **Hạn chế tối đa** — chỉ cho từ vượt level |
| `<br>` | 28% | 13% | **KHÔNG dùng** (data noise) |
| `<table>` | 0% | 27% | **KHÔNG dùng** (data N2 27% là legacy noise) |
| `<span>` (ngoài marker/label) | 0% | 45% | **KHÔNG dùng** — data noise |
| `相談者/回答者` | 0% | 5% | Advice format (optional) |

### R8.1 Label mandatory

100% bài có label A và B (hoặc 相談者 + 回答者A + 回答者B). **BẮT BUỘC**:

```html
<span class="label">A</span>
<span class="label">B</span>
```

Hoặc cho advice:
```html
<span class="label">相談者</span>
<span class="label">回答者Ａ</span>
<span class="label">回答者Ｂ</span>
```

### R8.2 Marker `①②` — rất hiếm

Chỉ dùng khi Q1 cần trỏ đến 1 cụm cụ thể trong 1 section (thường ở đoạn A). Data N2=24% có nhưng N1=0%. Khuyến nghị **ưu tiên không marker** (câu hỏi compare không cần marker).

Nếu dùng: chỉ 1 marker `①` trong đoạn A (hoặc đoạn B), không 2 markers.

### R8.3 `(中略)` — optional

Data N1=23%, N2=10%. Dùng khi muốn lược 1 phần trong section (mô phỏng bản gốc editorial dài hơn). Tối đa 1 `(中略)` mỗi section, tổng cả bài ≤ 2.

### R8.4 Source line — KHÔNG dùng

Data 0-4% có. Đọc hiểu tổng hợp **không** có source line như `（...による）`. Hai đoạn là 2 opinion piece ngắn không kèm source.

### R8.5 Furigana — hạn chế tối đa

Data cả N1 và N2 = **0% ruby**. Bài ngắn ít từ chuyên môn khó đến mức cần furigana. **Chỉ dùng khi thực sự không thể thay từ khác**.

---

## Checklist nội dung per bài

- [ ] Level = N1 hoặc N2 (không N3/N4/N5)
- [ ] A và B **CÙNG topic** (chủ đề chung)
- [ ] Quan hệ A↔B rõ: contrast / complement / debate / advice
- [ ] Tổng chars trong Target Range (600-750 N1, 600-800 N2)
- [ ] Không dưới Hard Reject (570)
- [ ] A/B balance ≤ 30% (mỗi đoạn 40-60%)
- [ ] 2-4 paragraph per section
- [ ] Có label A và B (hoặc 相談者+回答者A+回答者B)
- [ ] Không `<br>`, không `<table>`, không source line
- [ ] Văn phong luận thuyết ngắn — không kể chuyện
