# Rules: Câu hỏi, Đáp án & Explain (R5, R6)

> **Scope**: Đọc hiểu tổng hợp (統合理解 / integrated) — **CHỈ N1 & N2**, mỗi bài **đúng 2 câu**.
> **Label CỐ ĐỊNH**: cả 2 câu đều dùng `question_comprehensive_understanding`.

## R5. Câu hỏi — Label CỐ ĐỊNH & Patterns

### R5.1 Label duy nhất

Đọc hiểu tổng hợp có **1 label DUY NHẤT** được phép cho toàn bộ câu hỏi:

| Label | Khi nào dùng |
|-------|--------------|
| `question_comprehensive_understanding` | **BẮT BUỘC cho CẢ Q1 và Q2** — theo `kind_mission_mapping.json` `required_question_label` |

> **⛔ QUAN TRỌNG**: Mọi label khác (reason_explanation, reference, author_opinion, content_match, meaning_interpretation, content_mismatch, fill_in_the_blank) **KHÔNG được dùng** cho đọc hiểu tổng hợp. Pipeline sẽ warn và tự override về `question_comprehensive_understanding`.

### R5.2 Rule cứng Q2 (BẮT BUỘC cả N1 và N2)

Cả 2 level: **Q2 PHẢI là câu hỏi so sánh A vs B** (compare/integrate viewpoints).

**Cấm** Q2:
- Chỉ hỏi về A (không đề cập B)
- Chỉ hỏi về B (không đề cập A)
- Hỏi về kiến thức nền không có trong bài
- Test detail 1 cụm nhỏ ở 1 section

**Khuyến nghị mạnh**: Q2 phải có cụm `AとB`, `AもBも`, `AとBで共通`, `AとBの違い`, hoặc tương đương — kiểm tra được so sánh/tích hợp 2 đoạn.

### R5.3 Distribution combo 2 câu

Cả N1 và N2 đều **2 câu/bài** với cùng distribution. Các combo gợi ý:

#### 4 combo phổ biến

| # | Combo | Q1 | Q2 (BẮT BUỘC compare) |
|---|-------|----|-----------------------|
| 1 | **Common + Compare** (50%+ dùng) | `AとBで共通して述べられているのはどれか。` | `XについてAとBはどのように述べているか。` |
| 2 | **Compare + Compare** (bài đối lập) | `XについてAとBはどのように述べているか。` | `YについてAとBはどのように述べているか。` |
| 3 | **A-focus + Compare** (có marker ① ở A) | `①XXXとあるが、どのようなことか。` | `AとBに共通する考え方はどれか。` |
| 4 | **Advice — focus + Compare** (相談者+回答者) | `①XXX(=悩み)とは、どんな気持ちか。` | `「相談者」の相談に対するＡ、Ｂの回答について、正しいものはどれか。` |

> **Diversity rule**: Q1 và Q2 phải test **2 khía cạnh khác nhau** của bài. Q1 common → Q2 compare difference; Q1 compare → Q2 common / specific compare khác.

### R5.4 Q2 = compare A vs B (chi tiết)

Q2 phải **kiểm tra tích hợp**, không chỉ 1 đoạn. Đáp án đúng phải dựa trên cả A và B.

**Ví dụ Q2 phổ biến (Nhật)**:
- `AとBで共通して述べられているのはどれか。` (A và B có điểm chung gì?)
- `XについてAとBはどのように述べているか。` (A và B nói thế nào về X?)
- `AとBの考え方の違いはどれか。` (Sự khác nhau của A và B?)
- `AもBも〜と述べているが、異なる点はどれか。` (Cả A và B đều nói ~, nhưng khác ở điểm gì?)
- `AはX、BはYと考えているが、正しいのはどれか。` (A nghĩ X, B nghĩ Y — câu nào đúng?)
- Advice: `「相談者」の相談に対するＡ、Ｂの回答について、正しいものはどれか。`

Q2 **KHÔNG** được bám marker 1 section duy nhất (marker ① chỉ ở A) — vì test tổng thể 2 đoạn.

### R5.5 Q1 — linh hoạt nhưng trong bài

Q1 có thể:
- **Common** (điểm chung) — test đã tìm được "common thread" giữa A và B
- **A-focus** (hỏi về A) — thường kèm marker ①
- **B-focus** (hỏi về B) — ít dùng hơn
- **相談者-focus** (advice format) — hỏi về vấn đề của người hỏi

Q1 **KHÔNG** được trùng nội dung với Q2. Nếu Q2 là "common" thì Q1 nên "focus 1 đoạn" hoặc ngược lại.

### R5.6 Question quality rules

1. Câu hỏi answer được **trong bài**, không kiến thức nền
2. Mỗi câu có **4 đáp án plausible**, 1 đúng
3. **Q1 và Q2 KHÔNG test cùng 1 ý** — phải test 2 khía cạnh khác nhau
4. Marker `①②` trong HTML **phải match** câu hỏi (nếu Q1 hỏi `①...` thì bài phải có `<span class="marker">①</span>` trong section A hoặc B)
5. `question_image_X` **luôn empty** (đọc hiểu tổng hợp là văn thuần)
6. **Q2 LUÔN compare A vs B** — hard rule
7. **Q1 và Q2 KHÔNG trùng nhau** (spec JLPT: 各問題は重複しない)

### R5.7 Paraphrasing rule

Distractor **không được copy nguyên đoạn từ bài**:

| Level | Max chuỗi copy liên tục |
|-------|-------------------------|
| **N1** | 4 từ |
| **N2** | 5 từ |

Quá giới hạn → distractor quá dễ hoặc đáp án đúng bị lộ vì copy.

---

## R6. Định dạng câu trả lời & Explanation

### R6.1 Answer format — NO prefix

**4 options** tách nhau bằng `\n` (newline), **KHÔNG** có prefix `1.`, `2.`, `①`, `1)`:

**✅ ĐÚNG:**
```
AもBも新しい技術を慎重に受け入れるべきだと考えている
AもBも新しい技術は人々の生活を豊かにすると考えている
AもBも技術革新の速度が速すぎると批判している
AもBも技術の恩恵は一部の人にしか届かないと述べている
```

**❌ SAI → REJECT:**
```
1. AもBも新しい技術を...
2. AもBも新しい技術は...
...
```

Khi lưu vào CSV column `answer_X`, option tách nhau bằng `\n`.

**Column `correct_answer_X`** = chuỗi `"1"`, `"2"`, `"3"`, `"4"` (1-based, match vị trí trong `answer_X`).

> **CHÚ Ý**: Data gốc JSON dùng `correctAnswer` 0-based. Khi convert sang CSV phải **+1** để thành 1-based.

### R6.2 Distractor trap types (đặc thù đọc hiểu tổng hợp)

Đọc hiểu tổng hợp yêu cầu distractor **đặc thù compare/integrate**. 6 trap type phải có:

1. **Role reversal (đảo vai A/B)** — đặc trưng của dạng này: A nói X, B nói Y → distractor: "A nói Y, B nói X"
2. **Single-side only** — chỉ khớp A hoặc chỉ khớp B, nhưng được presented như "cả 2"
3. **Mix A+B** — trộn 1 câu nửa đúng A / nửa đúng B
4. **Scope** — quá rộng ("AもBも絶対反対") hoặc quá hẹp so với ý thật
5. **Extreme nuance** — thêm từ extreme (必ず, 絶対, すべて, 全く) → trái ý 1 hoặc cả 2 tác giả
6. **Extraneous fact** — thêm ý ngoài bài (cả A và B đều không nói)

**Bắt buộc ≥ 2 distractor dạng 1 hoặc 2** (role reversal / single-side) cho Q2 compare.

### R6.3 Explanation format (3 phần BẮT BUỘC)

Mỗi câu hỏi có 2 cột: `explain_vn_X` (tiếng Việt) và `explain_en_X` (tiếng Anh). Mỗi explain **3 phần** rõ ràng:

#### Phần 1 — Đáp án đúng
- Đáp án số mấy
- Trích dẫn **câu trong A và B** (cả 2 cho Q2 compare)
- Paraphrase lại ý đáp án nói gì

#### Phần 2 — Đáp án sai + bẫy
- Từng đáp án sai (3 options còn lại), nêu rõ:
  - Bẫy gì (Role reversal / Single-side / Mix / Scope / Extreme / Extraneous)
  - Vì sao sai (trích dẫn cụ thể A hoặc B phản bác)

#### Phần 3 — Tóm tắt chiến lược
- 1-2 câu tổng kết: "Phải đọc kỹ cả A và B, đặc biệt là [X]..." / "Cẩn thận distractor đảo vai A/B..."

### R6.4 Ví dụ explain VN cho Q2 compare

```
Đáp án đúng: 2. A nói "AI là công cụ hỗ trợ chứ không thể thay thế sáng tạo con người", B nói "AI có thể tạo ra ý tưởng mới nhưng cần con người đánh giá". Cả 2 đều xem AI như công cụ hỗ trợ — thesis chung.

Đáp án sai:
- 1. Role reversal — đảo vai: nói A quan tâm tốc độ, B quan tâm chất lượng, nhưng thực ra A nói về "giới hạn AI" và B nói về "tiềm năng AI".
- 3. Single-side — chỉ khớp B ("AI tạo ý tưởng mới") nhưng A không nói ý này.
- 4. Extreme — dùng từ "AI phải bị cấm hoàn toàn" — cả A và B đều không phủ nhận AI.

→ Chiến lược: Q2 compare → kiểm tra cả đoạn A và đoạn B. Loại distractor đảo vai bằng cách đọc lại thứ tự chủ thể trong đáp án, so với thứ tự trong bài.
```

### R6.5 Câu hỏi Nhật phổ biến (form chuẩn JLPT đọc hiểu tổng hợp)

**Q1 (focus hoặc common)**:
- `AとBで共通して述べられているのはどれか。`
- `AとBでは、Xについてどのように述べているか。`
- `①〇〇とあるが、どのような〇〇か。` (khi có marker ① ở A/B)
- `「相談者」の悩みはどのようなものか。` (advice)

**Q2 (BẮT BUỘC compare)**:
- `AとBの考え方の違いはどれか。`
- `XについてAとBはどのように述べているか。`
- `AもBも〇〇と述べているが、異なる点はどれか。`
- `AはX、BはYと考えているが、正しいのはどれか。` (N1)
- `「相談者」の相談に対するＡ、Ｂの回答について、正しいものはどれか。` (advice)

### R6.6 Q2 KHÔNG test 1 đoạn (CẤM tuyệt đối)

```
❌ SAI: Q2 hỏi "Aのみで述べられているのはどれか" (chỉ A)
❌ SAI: Q2 hỏi "①とあるが、何を指すか" (chỉ trong 1 section)
❌ SAI: Q2 hỏi về kiến thức nền không có trong A và B
✅ ĐÚNG: Q2 hỏi "AとBの違いはどれか" — compare tổng thể
```
