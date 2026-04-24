# HTML Patterns — Đọc Hiểu Tổng Hợp

Template HTML + CSS + convention cho "đọc hiểu tổng hợp" (N1/N2). Mục tiêu: 2 đoạn A + B (tổng 600–800 chars) với layout rõ ràng, dễ đọc, phù hợp spec "so sánh và tổng hợp".

## 1. Base Template (Preferred — Section Format)

```html
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JLPT {N1|N2} 統合理解</title>
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
            max-width: 780px;   /* bài ngắn, layout gọn */
            margin: 0 auto;
        }
        .passage-a, .passage-b {
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 6px;
            padding: 40px 48px 36px 48px;
            font-size: 16px;
            position: relative;
        }
        .passage-a { margin-bottom: 24px; }
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
        .passage-a p, .passage-b p {
            margin: 0 0 0.9em 0;
            text-indent: 1em;
        }
        .passage-a p:last-child, .passage-b p:last-child { margin-bottom: 0; }
        .ellipsis {
            text-align: center;
            font-size: 0.9em;
            color: #6b7280;
            margin: 0.8em 0;
            text-indent: 0;
        }
        .marker { font-weight: bold; color: #1e40af; }
        ruby { ruby-align: center; ruby-position: over; vertical-align: baseline; }
        ruby rt { font-size: 0.55em; color: #374151; letter-spacing: 0.02em; line-height: 1; vertical-align: top; }
        u { text-decoration: underline; text-decoration-thickness: 1.5px; }
    </style>
</head>
<body>
<div class="container">
    <section class="passage-a">
        <span class="label">A</span>
        <p>[Đoạn A — quan điểm 1 về topic]</p>
        <p>[tiếp lập luận / kết luận của A]</p>
    </section>
    <section class="passage-b">
        <span class="label">B</span>
        <p>[Đoạn B — quan điểm 2 về CÙNG topic, khác / bổ sung]</p>
        <p>[tiếp lập luận / kết luận của B]</p>
    </section>
</div>
</body>
</html>
```

### Điểm Chính

- **Container `max-width: 780px`** — layout gọn cho bài ngắn 600-800 chars.
- **2 sections stack dọc** — A ở trên, B ở dưới, giữa có `margin-bottom: 24px`.
- **Border + background trắng** — 2 card visually distinct.
- **`<span class="label">A|B</span>`** — nhãn nổi bật (blue background) đầu mỗi section.
- **Padding 40px 48px 36px** — rộng rãi, không quá chặt.
- **Line-height 1.9** — mật độ phù hợp bài ngắn.
- **Font-size 16px** — chuẩn đọc.

## 2. Template Biến Thể — Advice Format (3 sections)

Cho chủ đề tư vấn (悩み相談 / 人生相談) — phổ biến ở N2.

```html
<div class="container">
    <section class="consultant">
        <span class="label">相談者</span>
        <p>[Mô tả vấn đề / nỗi lo của người hỏi]</p>
    </section>
    <section class="passage-a">
        <span class="label">回答者Ａ</span>
        <p>[Lời khuyên 1 — góc nhìn A]</p>
    </section>
    <section class="passage-b">
        <span class="label">回答者Ｂ</span>
        <p>[Lời khuyên 2 — khác góc nhìn A]</p>
    </section>
</div>
```

CSS thêm vào `<style>`:

```css
.consultant {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 6px;
    padding: 40px 48px 36px 48px;
    font-size: 16px;
    margin-bottom: 24px;
}
.consultant .label {
    background: #4b5563;    /* gray — phân biệt với A/B blue */
}
.consultant p {
    margin: 0 0 0.9em 0;
    text-indent: 1em;
}
.consultant p:last-child { margin-bottom: 0; }
```

### Ghi Chú Advice Format

- Section `consultant` tổng ~100-150 chars (đặt vấn đề ngắn gọn)
- 回答者Ａ và 回答者Ｂ mỗi section ~200-280 chars
- Tổng 500-700 chars (thấp hơn tổng bình thường nhưng vẫn phải ≥ 600)
- Ký tự `相談者` + `回答者Ａ` + `回答者Ｂ` dùng full-width letters (Ａ/Ｂ) theo data gốc
- Q1 thường hỏi về 相談者 (với marker ① trong đó nếu cần)
- Q2 BẮT BUỘC so sánh Ａ vs Ｂ

## 3. Paragraph Rules

### Per Section

- **2–4 paragraph per section** (tránh section quá dày đặc)
- Mỗi para = 2–5 câu tiếng Nhật
- Không `<br>` giữa câu trong 1 paragraph
- Paragraph đầu = topic sentence / hook
- Paragraph cuối = kết luận / ý chính của section đó

### Text Indent

- `text-indent: 1em` cho `<p>` trong passage
- KHÔNG indent cho `.label`, `.ellipsis`, `.annotations`

## 4. Marker Strategies

### Strategy A — Không marker (phổ biến N1, 80%+)

2 passages thuần, không có marker. Q1 + Q2 đều là compare/common.

```html
<section class="passage-a">
    <span class="label">A</span>
    <p>現代では、AI技術の発展により...</p>
    <p>しかし、これにはリスクも伴う...</p>
</section>
<section class="passage-b">
    <span class="label">B</span>
    <p>AI技術について、筆者は...</p>
    <p>特に注意すべきは...</p>
</section>
```

→ Q1: `AとBで共通して述べられているのはどれか。`
→ Q2: `AI技術についてAとBはどのように述べているか。`

### Strategy B — Marker ① trong đoạn A (N2 ~24%)

Để Q1 hỏi về một cụm cụ thể trong đoạn A.

```html
<section class="passage-a">
    <span class="label">A</span>
    <p>最近、<span class="marker">①</span><u>このような変化</u>に気づく人が増えてきた...</p>
</section>
```

→ Q1: `①「このような変化」とあるが、どのような変化か。`
→ Q2: `XについてAとBはどのように述べているか。` (so sánh tổng thể)

### Strategy C — Advice với marker ① trong 相談者

```html
<section class="consultant">
    <span class="label">相談者</span>
    <p>...彼のことはとても好きだし、<span class="marker">①</span><u>私の本当の気持ち</u>を言い出しにくい...</p>
</section>
```

→ Q1: `①「私の本当の気持ち」とは、どんな気持ちか。`
→ Q2: `「相談者」の相談に対するＡ、Ｂの回答について、正しいものはどれか。`

## 5. `(中略)` Usage (Optional)

Khi muốn biểu thị đoạn gốc dài bị lược bớt. Dùng với `<p class="ellipsis">（中略）</p>`.

```html
<section class="passage-a">
    <span class="label">A</span>
    <p>[Para 1]</p>
    <p class="ellipsis">（中略）</p>
    <p>[Para 2 — sau đoạn lược]</p>
</section>
```

Ít khi cần vì bài vốn ngắn. Dùng khi topic yêu cầu skip background dài.

## 6. Source Line (Rarely Used)

Đọc hiểu tổng hợp **thường không có source line**. Data N1 = 4%, N2 = 0%.

Nếu hiếm hoi dùng, đặt ở cuối section A hoặc section B (không phải cuối container):

```html
<section class="passage-a">
    <span class="label">A</span>
    <p>[text]</p>
    <p class="source">（[fake author]「[fake title]」による）</p>
</section>
```

Tuy nhiên **khuyến nghị KHÔNG DÙNG** — bài đọc hiểu tổng hợp thường là "quan điểm độc lập" không gắn tác giả cụ thể.

## 7. Annotation 注1/注2 (Hiếm)

Data N1 = 4%, N2 = 0%. Rất ít dùng. Nếu bài có từ chuyên môn cần giải thích:

```html
<section class="passage-b">
    <span class="label">B</span>
    <p>[text có thuật ngữ cần chú thích]</p>
    <div class="annotations">
        <p>注1 xxx ： yyy</p>
    </div>
</section>
```

CSS thêm:

```css
.annotations {
    margin-top: 1.2em;
    padding-top: 0.8em;
    border-top: 1px dashed #d1d5db;
    font-size: 0.9em;
    color: #374151;
    line-height: 1.7;
}
.annotations p { margin: 0.2em 0; text-indent: 0; }
```

Thường không cần — bài đọc hiểu tổng hợp dùng vocabulary phổ thông của level.

## 8. Visual Elements Summary

| Element | Status | Data N1 | Data N2 | Skill guidance |
|---------|--------|---------|---------|----------------|
| A/B labels `<span class="label">` | **BẮT BUỘC** | 100% | 62% | Mọi bài phải có |
| `<section class="passage-a|b">` | **BẮT BUỘC** | — | — | Cấu trúc đúng spec |
| `<p>` cho text | **BẮT BUỘC** | 100% | 95% | Không dùng `<br>` |
| `<br>` giữa câu | KHÔNG dùng | 28% noise | 13% noise | Skill từ chối |
| `<table>` layout | KHÔNG dùng | 0% | 27% legacy | Thay bằng section |
| `<span>` wrappers | KHÔNG dùng | 0% | 45% legacy | Chỉ cho `.label` và `.marker` |
| `<u>` underline | Optional | 0% | 5% | Hiếm, chỉ khi cần emphasize |
| marker ①②③ | Optional | 0% | 24% | 0-1 marker (chỉ khi Q1 reference) |
| `<ruby>` furigana | Hạn chế | 0% | 0% | 0-3 (N1) / 0-5 (N2) cặp |
| `(中略)` | Optional | 23% | 10% | Chỉ khi cần lược đoạn dài |
| Source line | Hiếm | 4% | 0% | Thường không cần |
| Annotation 注1/2 | Hiếm | 4% | 0% | Thường không cần |

## 9. Thesis & Viewpoint Relationship Between A and B

### Possible Relationships

| Relationship | Đặc điểm | Tần suất | Ví dụ |
|--------------|----------|----------|-------|
| **Complement (bổ sung)** | A và B đồng ý cơ bản, chỉ khác chi tiết/khía cạnh | Phổ biến nhất | A: ưu điểm của AI; B: ứng dụng của AI |
| **Contrast (đối lập)** | A và B trái quan điểm | Phổ biến N1 | A: nên ủng hộ; B: nên phản đối |
| **Debate (tranh luận)** | A đề xuất ý X, B phản bác/đáp lại | Ít phổ biến | A: X là đúng; B: X có vấn đề vì... |
| **Advice dual (2 lời khuyên)** | 回答者Ａ và 回答者Ｂ đưa 2 cách giải quyết | N2 advice | Ａ: gián tiếp; Ｂ: trực tiếp |

### Quy Tắc Viết A và B

1. **A và B PHẢI cùng topic** — cùng chủ đề, cùng vấn đề đang bàn luận
2. **Khác ít nhất 1 khía cạnh** — góc nhìn, lý do, hoặc kết luận
3. **Có overlap để hỏi "common"** — nếu Q1 = common, cần có ít nhất 1 điểm trùng
4. **Có contrast để hỏi "khác"** — nếu Q2 = compare/difference, phải có điểm khác rõ
5. **Độ dài cân đối** — mỗi đoạn 40-60% tổng, chênh lệch ≤ 30%

## 10. Common Mistakes (Tóm Tắt)

1. **Dùng `<table>`/`<tbody>`** cho layout → sai. Dùng `<section class="passage-a|b">`.
2. **Quên `<span class="label">A|B</span>`** → sai. Bài PHẢI có nhãn A/B (hoặc 相談者/回答者Ａ/Ｂ).
3. **Dùng `<br>` giữa câu** → sai. Dùng `<p>` thuần.
4. **A và B nói chủ đề khác nhau** → sai. Cùng topic, khác góc nhìn.
5. **Bài quá dài (> 800 N1, > 900 N2)** → OVER_TARGET. Cân nhắc giảm.
6. **1 đoạn quá dài (>60%) / đoạn kia quá ngắn (<40%)** → AB_IMBALANCE. Cân bằng.
7. **Q1 + Q2 đều về 1 đoạn, không compare** → sai. Q2 BẮT BUỘC compare.
8. **Dùng label khác `question_comprehensive_understanding`** → sai. Label cố định.
9. **Dùng tên báo/tác giả thật** → sai. Mọi tên trong bài phải fake.
10. **Advice format viết A và B lời khuyên không khác nhau** → sai. 2 lời khuyên phải có dư địa compare rõ.

## 11. Quick Cheatsheet

```
🎯 Đọc hiểu tổng hợp cheatsheet:
  - 2 đoạn A + B (hoặc 相談者 + 回答者Ａ + 回答者Ｂ)
  - Tổng 600-800 chars
  - Mỗi đoạn ~40-60% tổng (2-4 paragraph)
  - 2 câu, label CỐ ĐỊNH = question_comprehensive_understanding
  - Q2 BẮT BUỘC so sánh A vs B

🎨 Template:
  - Container 780px
  - 2 section .passage-a và .passage-b
  - Label .label (background blue) ở đầu mỗi section
  - <p> thuần, text-indent: 1em
  - Line-height 1.9, font 16px Noto Sans JP

🚫 Tránh:
  - <table>, <br>, <span> lặt vặt
  - A và B khác chủ đề
  - Q1 + Q2 cùng về 1 đoạn
  - Label khác question_comprehensive_understanding
  - Quá 30% chênh lệch A/B
```
