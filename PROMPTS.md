# PROMPTS.md — Đọc Hiểu Tổng Hợp

Prompt templates để gọi LLM gen content cho skill `jlpt-reading-integrated` (統合理解 / đọc hiểu tổng hợp).

**Scope chỉ 2 level**: N1 (2 câu/bài, tổng A+B ~600-750 ký tự) và N2 (2 câu/bài, tổng A+B ~600-800 ký tự). N3/N4/N5 KHÔNG có kind này — đừng gen.

**Đặc trưng**: 2 đoạn A + B độc lập cùng chủ đề nhưng quan điểm khác / bổ sung. Workload gen nhẹ (bài ngắn) nhưng quality control chặt (AB-balance, compare question).

Cách dùng: copy prompt theo level, thay các `{PLACEHOLDER}` bằng giá trị thực tế, feed vào Claude/Gemini.

## 0. Common System Prompt (cả N1 và N2)

```
Bạn là trợ lý chuyên gen dữ liệu JLPT 統合理解 (đọc hiểu tổng hợp).

Rule BẤT BIẾN:
1. Gen đoạn văn tiếng Nhật đúng Target Range (TỔNG A+B):
   - N1: 600-750 ký tự
   - N2: 600-800 ký tự
   (Đếm không whitespace, không tính <rt>, <style>, <script>.)
2. CHỈ gen cho N1 hoặc N2. N3/N4/N5 không có kind này.
3. Bài PHẢI có ĐÚNG 2 đoạn A + B:
   - Cùng chủ đề X
   - 2 quan điểm khác nhau / bổ sung / tranh luận / đối lập
   - A/B balance ≤ 30% (nếu A=300, B ∈ [210, 390])
   - Mỗi đoạn 2-4 paragraph
   - Biến thể (hiếm): 3 sections = 相談者 + 回答者Ａ + 回答者Ｂ (advice format)
4. HTML template: <!DOCTYPE html>, Noto Sans JP qua Google Fonts,
   <div class="container"> max-width 780px chứa:
   - <section class="passage-a"> với <span class="label">Ａ</span> (màu xanh)
   - <section class="passage-b"> với <span class="label">Ｂ</span> (màu đỏ)
   - Biến thể: thêm <section class="consultant"> (màu xám, nằm đầu) cho advice format
   KHÔNG dùng <table> bao đoạn (legacy noise data cũ).
   KHÔNG dùng <br> giữa câu. Dùng <p> thuần trong mỗi section.
5. Furigana RẤT HIẾM:
   - N1: tối đa 3 cặp <ruby>/<rt> (data 0%)
   - N2: tối đa 5 cặp (data 0%)
   Chỉ cho từ vượt level. Cấm dạng "Ab" (nửa kanji nửa hiragana).
6. Mỗi bài có SỐ CÂU HỎI CHÍNH XÁC: 2 câu (cho cả N1 và N2).
7. CẢ 2 CÂU HỎI LUÔN có label = `question_comprehensive_understanding` (cố định).
   Đây là kind duy nhất có 1 label fixed cho mọi câu.
8. Q1 và Q2 KHÔNG trùng nội dung / ý. Test 2 góc khác nhau.
9. CÂU 2 BẮT BUỘC so sánh A vs B:
   - Common (phổ biến): AとBで共通して述べられているのはどれか。
   - Difference: AとBの考え方の違いはどれか。
   - Side-by-side: XについてAとBはどのように述べているか。
   - Which: AとBのどちらが...と述べているか。
   - Advice: 「相談者」に対するＡ、Ｂの回答について、正しいものはどれか。
10. CÂU 1 flexible:
    - Compare (cho N1 uniform): AとBで共通して述べられていることは何か。
    - Single-focus (N2): ①XXXとあるが、どのようなことか。(có marker trong A)
    - About one side: AはXをどう捉えているか。
11. `(中略)` optional — có thể dùng 1 lần trong A hoặc B (giữa 2 khối logic).
    Format: <p class="ellipsis">（中略）</p>
12. Distractor đánh vào việc hiểu nhầm 1 trong 2 đoạn:
    - Đúng về A nhưng sai về B (hoặc ngược lại)
    - Trộn ý A + ý B thành ý sai
    - Paraphrase sai nuance của 1 bên
    - Đảo polarity của 1 bên
13. Giải thích VN + EN cho TỪNG CÂU (tại sao đúng + tại sao 3 đáp án sai,
    chỉ rõ đoạn A hoặc B nào support).
14. KHÔNG dùng tên tác giả / báo có thật. Source line gần như không có ở data Phase 5.
15. Paragraph count:
    - Mỗi section A hoặc B: 2-4 paragraph
    - Tổng paragraph cả bài: 4-8

Output format: JSON với các field:
{
  "id": "{LEVEL}_{uuid32hex}",
  "level": "N1" hoặc "N2",
  "tag": "học tập độc lập vs có giáo viên",
  "html": "<!DOCTYPE html>...",
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

## 1. Prompt N1 — Tổng hợp triết học / phê bình cao cấp, 2 câu compare

```
Gen 1 bài JLPT N1 đọc hiểu tổng hợp về chủ đề {TOPIC} (ví dụ: ý nghĩa nỗi nhớ,
bản chất may mắn vs nỗ lực, định nghĩa thông minh, kinh doanh vs triết lý,
văn hóa truyền thống vs hiện đại, quan niệm sống chết, AI vs trí tuệ con người).

Yêu cầu cụ thể:
- Tổng độ dài (A+B): 600-750 ký tự (count không whitespace, không <rt>)
- Mỗi đoạn A hoặc B: 300-400 ký tự, balance ≤ 30%
- Thể loại: luận thuyết / tiểu luận / phê bình cao cấp — CÓ ý kiến/lập trường
  KHÔNG kể chuyện thuần
- Văn phong: rất formal, luận thuyết cao cấp
  (～いかんによらず, ～をもって, ～に先立ち, ～をものともせず, ～にほかならない,
   ～というものだ, ～ざるを得ない, ～に足る, ～にたえない, ～というほかない)
- Cấu trúc mỗi section: 2-4 paragraph (KHÔNG dùng <br>)
- Furigana: tối đa 3 cặp <ruby>/<rt>, chỉ cho từ vượt N1 (data 0% — ưu tiên 0)
- Annotation 注: data 4% — thường không cần
- Source line: data 4% — KHÔNG cần
- Marker ①②: data 0% — ưu tiên 0
- `(中略)` optional (data 23%) — có thể dùng giữa đoạn A hoặc B

Quan hệ A ↔ B (chọn 1):
  - Bổ sung (complement): A nói mặt X, B nói mặt Y, cùng hỗ trợ 1 ý
  - Trái chiều (contrast): A ủng hộ, B phản biện (hoặc ngược)
  - Tranh luận (debate): A + B tranh luận trực tiếp về 1 ý kiến
  - Góc nhìn khác (different angle): A từ góc học giả, B từ góc thực tế

BẮT BUỘC: Đúng 2 câu hỏi, cả 2 có label = question_comprehensive_understanding.

Combo câu hỏi đề xuất (chọn 1):
  A. (phổ biến nhất — 80%+ data N1)
     Q1: AとBで共通して述べられているのはどれか。 (common/chung)
     Q2: XについてAとBはどのように述べているか。 (side-by-side compare)
  B. (đối lập rõ ràng)
     Q1: XについてAとBはどのように述べているか。
     Q2: AとBの考え方の違いはどれか。 (difference)
  C. (single Q1 + compare Q2)
     Q1: AはXをどう捉えているか。 (about only A)
     Q2: AとBの主張の違いはどれか。

**Rule cứng**: Q2 LUÔN compare A vs B. Q1 flexible nhưng ưu tiên cũng compare.

Distractor N1 TINH VI — đánh vào:
  - Paraphrase sai nuance của A hoặc B
  - Đúng 1 bên, sai 1 bên (common / difference dễ nhầm)
  - Trộn ý A và ý B thành ý sai
  - Đảo polarity 1 bên (A ủng hộ → distractor nói A phản đối)
  - Tuyệt đối hoá 1 bên (どちらも, すべて)
  - Attribution sai (ý của A gán cho B)

**Balance đoạn**: Nếu A dài, B phải cũng đủ dài. Tránh A=400, B=200.
Tốt: A=340-370, B=330-360 (gần như 50-50).

Output JSON theo Common System Prompt, mảng "questions" có ĐÚNG 2 phần tử,
cả 2 label = question_comprehensive_understanding.
```

## 2. Prompt N2 — Tổng hợp văn hóa/công nghệ/tư vấn trung cấp, 2 câu compare

```
Gen 1 bài JLPT N2 đọc hiểu tổng hợp về chủ đề {TOPIC} (ví dụ: cách học ngoại ngữ,
AI trong giáo dục, tiết kiệm vs tiêu dùng, du lịch cá nhân vs tour, làm việc từ xa,
quà tặng sinh nhật, ăn sáng vs không ăn, SNS với trẻ em, xe điện vs xe xăng).

Yêu cầu cụ thể:
- Tổng độ dài (A+B): 600-800 ký tự
- Mỗi đoạn A hoặc B: 300-420 ký tự, balance ≤ 30%
- Thể loại: ý kiến / bình luận / tư vấn trung cấp — CÓ 2 quan điểm
- Văn phong: formal văn viết trung cấp
  (～に伴い, ～に基づき, ～を踏まえて, ～に限り, ～とはいえ, ～からこそ, ～わけで,
   ～ないではいられない, ～ずにはいられない, ～に応じて, ～において)
- Cấu trúc mỗi section: 2-4 paragraph
- Furigana: tối đa 5 cặp (data 0% — ưu tiên 0)
- Marker ①② (data 24%) — optional, chỉ khi Q1 ref 1 cụm cụ thể trong A
- `(中略)` optional (data 10%)
- Advice variant (data 5%): dùng format 相談者 + 回答者A + 回答者B

Quan hệ A ↔ B (chọn 1):
  - Bổ sung: A tip 1, B tip 2 cho cùng 1 vấn đề
  - Trái chiều: A nên làm X, B không nên
  - Tranh luận: A + B đưa ý kiến trái ngược về 1 công nghệ/xu hướng
  - Advice dual: 1 consultant hỏi, 2 respondents (A, B) đưa lời khuyên khác nhau

BẮT BUỘC: Đúng 2 câu hỏi, cả 2 có label = question_comprehensive_understanding.

Combo câu hỏi đề xuất (chọn 1):
  A. (phổ biến)
     Q1: AとBで共通して述べられていることは何か。
     Q2: XについてAとBはどのように述べているか。
  B. (marker + compare)
     Q1: ①「XXX」とあるが、どのようなことか。 (hỏi cụm trong A, có marker)
     Q2: AとBに共通する考えはどれか。
  C. (advice format — dùng khi có 相談者)
     Q1: ①XXX(=悩み)とは、どんな気持ちか。
     Q2: 「相談者」に対するＡ、Ｂの回答について、正しいものはどれか。
  D. (which-side)
     Q1: AはXについてどう述べているか。
     Q2: AとBのどちらが...を重視しているか。

**Rule cứng**: Q2 LUÔN compare A vs B. Q1 có thể là single-focus (có marker) hoặc compare.

Distractor N2 sai ở:
  - Đúng A sai B (hoặc ngược)
  - Trộn nuance A với B
  - Paraphrase sai 1 đoạn
  - Attribution đảo ngược
  - Tuyệt đối hoá / cắt xén điều kiện

**Advice format template** (cho combo C):
  HTML có 3 sections:
  <section class="consultant">
    <span class="label label-gray">相談者</span>
    <p>...nội dung câu hỏi/nỗi niềm của 相談者...</p>
  </section>
  <section class="passage-a">
    <span class="label">Ａ</span> <!-- 回答者Ａ -->
    <p>...lời khuyên Ａ...</p>
  </section>
  <section class="passage-b">
    <span class="label">Ｂ</span> <!-- 回答者Ｂ -->
    <p>...lời khuyên Ｂ...</p>
  </section>

Output JSON theo Common System Prompt, mảng "questions" có ĐÚNG 2 phần tử,
cả 2 label = question_comprehensive_understanding.
```

## 3. Batch Prompt — Gen nhiều bài 1 lần

```
Gen {N} bài JLPT {LEVEL} đọc hiểu tổng hợp. Yêu cầu đa dạng:

1. Topic: chọn từ {N_TOPIC} nhóm khác nhau:
   N1:
   - Triết học / tâm lý (ý nghĩa cuộc sống, bản chất thông minh, nostalgia)
   - Văn hóa truyền thống vs hiện đại
   - Xã luận chính sách / kinh tế cao cấp
   - Khoa học / công nghệ cao cấp (AI vs con người)
   - Giáo dục / lý luận học thuật
   - Văn học / phê bình
   N2:
   - Học tập / ngoại ngữ (tự học vs có giáo viên, app vs offline)
   - Công nghệ / AI (smartphone có tốt, SNS với trẻ)
   - Đời sống / sức khỏe (ăn sáng, ngủ sớm, tập thể dục)
   - Công việc / kinh tế (từ xa vs văn phòng, tiết kiệm)
   - Du lịch / giải trí (tour vs tự túc)
   - Tư vấn tình cảm / xã hội (advice format — 5%)

2. Số câu hỏi per bài: BẮT BUỘC ĐÚNG 2 câu cho cả N1 và N2

3. question_label: 100% = question_comprehensive_understanding (cố định)

4. Mỗi bài có _id riêng: {LEVEL}_{uuid32hex}.

5. Tổng độ dài (A+B) trong Target Range:
   - N1: 600-750
   - N2: 600-800

6. Q2 BẮT BUỘC compare A vs B (common / difference / side-by-side / which).

7. Visual elements:
   - N1: uniform A/B structure, hầu như không cần marker/annotation/source
   - N2: có thể dùng marker (24%), advice format (5%) cho đa dạng

8. Quan hệ A ↔ B đa dạng: có bài bổ sung, có bài trái chiều, có bài tranh luận.

9. A/B balance: chênh lệch ≤ 30% trong mọi bài.

Batch size khuyến nghị: **5-8 bài/lần** (bài ngắn nên gen nhanh hơn Phase 4).

Output: array của {N} JSON objects theo Common System Prompt.
```

## 4. Fix Prompt — Khi bài fail validate

### Case: UNDER_TARGET (trên HARD_REJECT nhưng dưới TARGET)

```
Bài {ID} có {CHARS} ký tự (A+B), dưới Target Range của {LEVEL} ({LO}-{HI}).

Bổ sung thêm {NEEDED} ký tự. Chia đều 2 đoạn để giữ balance:
1. Thêm 1 câu vào mỗi đoạn (A + B, mỗi bên ~NEEDED/2 ký tự)
2. Thêm 1 paragraph nuance vào đoạn ngắn hơn
3. Thêm ví dụ cụ thể trong đoạn yếu hơn

KHÔNG phá balance A vs B (giữ chênh lệch ≤ 30%).
Giữ nguyên: _id, cả 2 questions, đáp án đúng, quan hệ A ↔ B.
Marker ①② đã dùng phải giữ nguyên vị trí.

Output: JSON object mới (cùng schema, cùng _id, cùng questions), đã chỉnh độ dài.
```

### Case: OVER_TARGET (> HI + 100)

```
Bài {ID} có {CHARS} ký tự (A+B), vượt xa Target Range của {LEVEL} ({LO}-{HI}).

Rút ngắn còn {LO}-{HI} ký tự bằng cách:
1. Rút gọn câu dài thành 1-2 câu ngắn trong cả 2 đoạn (giữ balance)
2. Bỏ nội dung tangential (không liên quan đến 2 câu hỏi)
3. Thêm `(中略)` thay cho 1 khối dài mà ý đã rõ

KHÔNG được xoá đoạn chứa marker ①② nếu Q1 reference marker đó.
KHÔNG phá balance A vs B.

Giữ nguyên: _id, cả 2 questions, đáp án đúng.

Output: JSON object mới.
```

### Case: HARD_REJECT (< 570)

```
Bài {ID} có {CHARS} ký tự, DƯỚI Hard Reject của {LEVEL} (570).
KHÔNG chỉnh sửa — GEN LẠI TỪ ĐẦU.

Yêu cầu:
  {LEVEL} Target Range {LO}-{HI} ký tự (tổng A+B).
  Mỗi đoạn A, B: 300-400 ký tự.
  Số câu: 2.
  Label: question_comprehensive_understanding (cả 2 câu).
  Q2: compare A vs B.
  Topic: {TOPIC}.
  Combo câu: {LABEL_COMBO}.

Output: JSON object mới hoàn toàn.
```

### Case: AB_IMBALANCE (chênh > 30%)

```
Bài {ID} có A = {A_CHARS} chars, B = {B_CHARS} chars, chênh lệch {RATIO}%.

Fix (giữ question + đoạn dài):
1. Nếu A quá ngắn: thêm câu/paragraph vào A để cân với B
2. Nếu B quá ngắn: thêm câu/paragraph vào B để cân với A
3. Nếu 1 đoạn quá dài: rút gọn đoạn dài thay vì kéo dài đoạn ngắn
4. Target: A/B ∈ [0.7, 1.4] (chênh ≤ 30%)

KHÔNG đổi chủ đề của đoạn được thêm — phải nối tiếp logic đoạn gốc.

Giữ nguyên: _id, cả 2 questions, đáp án đúng, quan hệ A ↔ B.

Output: JSON object mới.
```

### Case: AB_UNDETECTED (script không detect được A và B)

```
Bài {ID} không có A/B labels trong HTML. Script không phân biệt được 2 đoạn.

Fix HTML template:
- Bọc đoạn A trong: <section class="passage-a"><span class="label">Ａ</span>...</section>
- Bọc đoạn B trong: <section class="passage-b"><span class="label">Ｂ</span>...</section>
- HOẶC dùng: <p>Ａ</p><p>text A...</p><p>Ｂ</p><p>text B...</p> (legacy fallback)

Các <p> nội dung phải nằm BÊN TRONG đúng <section>.
Dùng full-width Ａ (U+FF21), KHÔNG half-width A.

Giữ nguyên: _id, cả 2 questions, đáp án đúng, nội dung chính.

Output: JSON object mới với HTML đã chuẩn format.
```

### Case: UNSUPPORTED_LEVEL

```
Bài {ID} có level {LEVEL} nhưng kind "đọc hiểu tổng hợp" CHỈ dành cho N1 và N2.

Xử lý:
1. Nếu nội dung phù hợp N1/N2 → sửa _id thành {N1|N2}_{uuid_mới},
   điều chỉnh độ dài + văn phong theo level mới.
2. Nếu không phù hợp N1/N2 → chuyển sang skill khác:
   - Essay/thư dài → jlpt-reading-long-passage (Phase 3)
   - Xã luận 1 tác giả → jlpt-reading-thematic (Phase 4)

Không commit vào CSV đọc hiểu tổng hợp cho đến khi level chuẩn hoá.
```

### Case: Sai số câu hỏi (warning)

```
Bài {ID} đang có {ACTUAL_Q} câu hỏi, nhưng đọc hiểu tổng hợp yêu cầu ĐÚNG 2 câu.

Fix:
- Nếu dư câu (≥ 3): giữ 1 câu chung/single-focus + 1 câu compare.
  Bỏ câu lặp ý hoặc câu không test 2 đoạn.
  **BẮT BUỘC** giữ 1 câu compare A vs B ở vị trí Q2.
- Nếu thiếu câu (1): thêm 1 câu compare A vs B làm Q2.
  (Nếu câu hiện tại đã là compare → thêm câu Q1 single-focus hoặc common.)

Giữ nguyên: _id, HTML, đáp án các câu còn lại.

Output: JSON object mới, "questions" có ĐÚNG 2 phần tử.
```

### Case: Q2 không compare A vs B (warning)

```
Bài {ID} là {LEVEL} đọc hiểu tổng hợp, nhưng câu 2 không so sánh A vs B
(hiện: "{Q2_TEXT}").

**Đây là vi phạm RULE CỨNG** — Q2 LUÔN phải compare A vs B (common / difference /
side-by-side / which-side). Đó là linh hồn của đọc hiểu tổng hợp.

Fix (giữ Q1 nguyên):
1. Chuyển Q2 sang 1 trong 5 pattern compare:
   - Common: AとBで共通して述べられているのはどれか。
   - Difference: AとBの考え方の違いはどれか。
   - Side-by-side: XについてAとBはどのように述べているか。
   - Which-side: AとBのどちらが...と述べているか。
   - Advice: 「相談者」に対するＡ、Ｂの回答について、正しいものはどれか。
2. 4 đáp án phải cover được cả A lẫn B:
   - Đáp án đúng = tóm tắt đúng quan hệ A-B
   - Distractor: đúng A sai B, đúng B sai A, trộn 2 đoạn, đảo polarity

Giữ nguyên: _id, HTML, Q1.

Output: JSON object mới.
```

### Case: Q1 và Q2 trùng ý (warning)

```
Bài {ID} có Q1 và Q2 test cùng 1 ý / góc.

Fix (giữ Q2 compare A vs B):
Chuyển Q1 sang test:
- Single-focus: ①「XXX」とあるが、... (về 1 cụm trong A)
- About-one-side: AはXをどう捉えているか。
- Common (nếu Q2 là difference): AとBで共通するのはどれか。

Q1 và Q2 phải test 2 góc KHÁC NHAU của mối quan hệ A-B:
- Q1 = common, Q2 = difference
- Q1 = single-focus A, Q2 = compare A-B
- Q1 = common, Q2 = side-by-side

Giữ nguyên: _id, HTML, Q2.

Output: JSON object mới.
```

### Case: Label khác question_comprehensive_understanding

```
Bài {ID} có label = "{ACTUAL_LABEL}" cho 1 hoặc 2 câu, không phải
question_comprehensive_understanding.

Đây là kind đặc biệt — MỌI câu hỏi đọc hiểu tổng hợp đều dùng label cố định
question_comprehensive_understanding (theo rules/kind_mission_mapping.json).

Fix: đơn giản đổi tất cả label sang question_comprehensive_understanding.
Script process_html.py sẽ auto-override, nhưng gen agent nên gen đúng từ đầu.

Nội dung câu hỏi giữ nguyên.

Output: JSON object mới với "label": "question_comprehensive_understanding"
ở cả 2 questions.
```

### Case: A và B cùng ý (không compare được)

```
Bài {ID} có A và B nói cùng 1 ý, không có compare-able relationship.
Không có gì để compare trong Q2.

Fix: GEN LẠI 1 trong 2 đoạn với quan điểm KHÁC:
- Nếu A và B đều ủng hộ X → giữ A, rewrite B phản biện X
- Nếu cả 2 nói cùng cách → giữ 1, rewrite 1 theo góc nhìn khác

Quan hệ A ↔ B phải là 1 trong:
- Complement (A + B cùng hỗ trợ ý nhưng từ 2 góc khác)
- Contrast (A đồng ý, B không)
- Debate (A + B tranh luận)
- Dual-advice (2 lời khuyên khác nhau)

Giữ nguyên: _id, đoạn còn lại, có thể phải update Q1/Q2 để phù hợp.

Output: JSON object mới.
```

### Case: Dùng <table> bao đoạn (legacy noise)

```
Bài {ID} dùng <table><tbody><tr><td>... để bao đoạn A/B.
Đây là legacy noise của data cũ (27% N2 samples), skill KHÔNG dùng.

Fix HTML:
Thay:
  <table><tbody><tr><td><p>Ａ</p><p>...</p></td></tr></tbody></table>
Thành:
  <section class="passage-a">
    <span class="label">Ａ</span>
    <p>...</p>
  </section>

Giữ nguyên nội dung text, chỉ đổi wrapper HTML.

Output: JSON object mới với HTML đã chuẩn format section.
```

### Case: Dạng "Ab"

```
Bài {ID} có dạng "Ab" (nửa kanji nửa hiragana) sai quy tắc furigana.

Cụm vi phạm: "{VIOLATION}" (ví dụ: 週かん, 友だち)

Fix: chọn 1 trong 2 cách:
1. Full kanji + <ruby>: <ruby>週間<rt>しゅうかん</rt></ruby>
2. Full hiragana: しゅうかん

Giữ nguyên phần còn lại, chỉ sửa cụm vi phạm.

Output: JSON object mới (cùng _id, cùng questions, HTML đã fix).
```

### Case: Marker ①② không match câu hỏi

```
Bài {ID} có câu hỏi「{Q_NUM}」tham chiếu marker {MARKER} nhưng HTML không có marker đó
trong section tương ứng.

Fix: thêm marker vào HTML trong section đúng:
  <span class="marker">{MARKER}</span><u>{PHRASE}</u>
ngay trước hoặc bao quanh cụm từ được hỏi.

Hoặc: đổi câu hỏi không dùng marker, chỉ quote cụm từ:
  「{PHRASE}」とあるが、〜

Đọc hiểu tổng hợp N1 data = 0% marker, N2 = 24%.
Nếu không cần thiết, bỏ marker đi cho cleaner.

Giữ nguyên các phần còn lại.

Output: JSON object mới.
```

## 5. Quality Check Prompt (gọi sau batch)

```
Kiểm tra chất lượng batch {N} bài JLPT {LEVEL} đọc hiểu tổng hợp. Cho mỗi bài:

1. Level = N1 hoặc N2:                           PASS / FAIL
2. Tổng độ dài (target {LO}-{HI}):               PASS / FAIL ({CHARS} chars)
3. Số câu hỏi = 2:                               PASS / FAIL ({ACTUAL_Q})
4. Bài có ĐÚNG 2 section A + B:                  PASS / FAIL
5. A/B labels hiển thị rõ (Ａ, Ｂ):              PASS / FAIL
6. A/B balance ≤ 30%:                            PASS / FAIL (A={A_CHARS}, B={B_CHARS})
7. Mỗi section 2-4 paragraph:                    PASS / FAIL
8. A và B cùng chủ đề X, khác quan điểm:         PASS / FAIL
9. Cả 2 label = question_comprehensive_understanding: PASS / FAIL
10. Q2 compare A vs B:                           PASS / FAIL
11. Q1 và Q2 KHÔNG trùng ý:                      PASS / FAIL
12. Marker ①② match câu hỏi (nếu có):            PASS / FAIL
13. Furigana đúng quy tắc (không "Ab"):          PASS / FAIL
14. Mỗi câu chỉ 1 đáp án đúng:                   PASS / FAIL
15. Distractor tinh vi level-phù hợp:            PASS / FAIL
16. Distractor cover cả A lẫn B:                 PASS / FAIL
17. Câu hỏi answer được từ 2 đoạn:               PASS / FAIL
18. explain_vn + explain_en non-empty + ref:     PASS / FAIL
19. KHÔNG dùng <table> / <br>:                   PASS / FAIL

Batch-level:
- Tất cả 100% label = question_comprehensive_understanding? YES / NO
- Tất cả 100% Q2 là compare A vs B?              YES / NO
- ≥ 2 tag (topic) khác nhau?                     YES / NO
- Tất cả _id unique?                             YES / NO
- {N} bài × 2 = {TOTAL_Q} câu hỏi — đúng?        YES / NO
- Đa dạng quan hệ A ↔ B (≥ 2 loại khác nhau)?   YES / NO

Output: bảng markdown 1 row per bài + summary batch-level.
```

## 6. Variables reference

| Placeholder | Giá trị mẫu |
|-------------|-------------|
| `{LEVEL}`   | N1 hoặc N2 (CHỈ 2 level) |
| `{TOPIC}`   | học tập độc lập vs có giáo viên, AI giáo dục vs truyền thống... |
| `{N}`       | Số bài (khuyến nghị 5-8) |
| `{N_TOPIC}` | Số nhóm topic (thường 2-4) |
| `{LO}, {HI}` | Target Range tổng A+B (N1: 600-750, N2: 600-800) |
| `{THRESHOLD}` | Hard Reject (570 cho cả 2 level) |
| `{CHARS}`   | Char count thực tế (tổng A+B) |
| `{A_CHARS}` / `{B_CHARS}` | Char count riêng A và riêng B |
| `{RATIO}` | Phần trăm chênh lệch A vs B |
| `{NEEDED}`  | Số ký tự cần bổ sung |
| `{ID}`      | `{LEVEL}_{uuid32hex}` |
| `{VIOLATION}` | Cụm vi phạm rule furigana |
| `{ACTUAL_Q}` | Số câu thực tế (spec luôn 2) |
| `{ACTUAL_LABEL}` | Label thực tế (spec cố định question_comprehensive_understanding) |
| `{Q2_TEXT}` | Nội dung Q2 thực tế (nếu không compare) |
| `{LABEL_COMBO}` | Combo câu hỏi đề xuất (xem section level) |
| `{Q_NUM}` | 1 hoặc 2 |
| `{MARKER}` | ①, ②, ③ |
| `{PHRASE}` | Cụm từ được quote/underline |
| `{TOTAL_Q}` | Tổng câu hỏi kỳ vọng cả batch (N × 2) |
