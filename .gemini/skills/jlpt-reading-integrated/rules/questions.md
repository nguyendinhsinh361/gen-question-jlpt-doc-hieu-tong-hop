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

### R5.8 Văn phong câu hỏi (thể động từ) theo level — BẮT BUỘC

Câu hỏi (`question_X`) và 4 lựa chọn (`answer_X`) phải dùng đúng **thể động từ** theo level:

| Level | Thể bắt buộc | Đặc trưng kết câu |
|-------|--------------|-------------------|
| **N1, N2, N3** | **Thể thường** (普通体 / だ・である調) | `〜か。` / `〜のはどれか。` / `〜と考えられるか。` (KHÔNG dùng です/ます) |
| **N4, N5** | **Thể ます** (です・ます調) | `〜ですか。` / `〜のはどれですか。` / `〜と思いますか。` |

**Quy tắc cứng:**
- Đọc hiểu tổng hợp CHỈ có **N1 và N2** → cả 2 level đều dùng **thể thường**, KHÔNG được dùng です/ます (kể cả các pattern Q2 compare như `AとBで共通して述べられているのはどれか。`, `XについてAとBはどのように述べているか。`)
- Câu hỏi và **cả 4 đáp án** phải nhất quán cùng thể (không trộn lẫn)

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

### ⛔ Phân loại bẫy đáp án — 7 loại tổng (5 chuẩn + bẫy có điều kiện)

> **Nguồn**: rule_doc_hieu.md Phần 5 (5.1–5.7). Áp dụng cho dạng này: **N1 + N2**.
>
> **Quy tắc:** Trong 4 đáp án (1 đúng + 3 sai), 3 distractor PHẢI dùng **≥ 3 loại bẫy khác nhau** từ bảng dưới. Mỗi distractor phải dùng info/ý THẬT từ bài (trừ Fabrication có thể bịa cận-context).

| Loại bẫy | Mô tả | Ví dụ |
|----------|-------|-------|
| **① Reversal** ❌ | Đảo ngược ý nghĩa, kết luận, quan hệ nhân-quả từ bài | Bài: 「Aによって元気になった」 → Bẫy: 「Aの後で体が重くなった」 (đảo ngược) |
| **② Detail Swap** 🔄 | Dùng thông tin đúng nhưng gán sai ngữ cảnh (sai đối tượng/thời điểm/địa điểm) | Bài: 「Aは嵐山, Bは金閣寺」 → Bẫy: 「Aは金閣寺」 (đúng chi tiết, sai ngữ cảnh) |
| **③ Fabrication** 🎭 | Thêm thông tin hoàn toàn KHÔNG CÓ trong bài | Bài không nói X → Bẫy: 「XだからY」 — không kiểm chứng được |
| **④ Scope** 📐 | Đáp án quá RỘNG (over-generalization) hoặc quá HẸP so với ý bài | Bài: 「金閣寺で写真」 → Bẫy rộng: 「京都で写真」 / Bẫy hẹp: 「池のそばで写真」 |
| **⑤ Mixing** 🧩 | Kết hợp 2 thông tin đúng riêng lẻ thành ý sai (không tồn tại trong bài) | A đúng + B đúng nhưng không liên quan → Bẫy: 「AだからB」 |
| **⑥ Single-side** ➕ | Đáp án chỉ khớp với A hoặc chỉ với B nhưng được presented như "cả 2" — bẫy ĐẶC TRƯNG cho 統合理解 | Câu hỏi điểm chung A&B; Bẫy: ý kiến chỉ có trong A, không có trong B (hoặc ngược lại) |
| **⑥b Cross-swap (Role reversal A/B)** 🔀 | Hoán đổi vai trò A và B — A nói X, B nói Y → distractor "A nói Y, B nói X" | Khi câu hỏi compare A vs B, đảo thứ tự chủ thể trong distractor là bẫy chính của Q2 |
| **⑦ Peripheral Source** 📎 | Đáp án lấy từ 注/source line thay vì lập luận của A hay B | Hiếm hơn ở 統合 (vì bài ngắn, 注 ít) nhưng có thể xuất hiện ở N1 |

**📊 Phân bổ thực tế per level (từ data đề thi):**
- **N5–N4**: Reversal (cảm xúc/hành động) + Detail Swap đơn giản + Fabrication thông tin ngoài bài
- **N3**: Detail Swap (hoán đổi nhân vật/thời điểm) + Mixing (trộn lý do) + Fabrication tinh tế hơn
- **N2**: Scope (quá rộng/hẹp) + Reversal logic (concede trap: ý nhượng bộ vs ý chính) + Mixing (evidence + opinion)
- **N1**: Peripheral Source (nếu 注 dài) + Reversal sâu (premise vs conclusion) + Scope cực tinh tế (1 từ điều kiện) + Mixing phức tạp (2+ bước lập luận)

> **Áp dụng:** 5 loại chuẩn áp dụng cho cả N1 và N2. Single-side + Cross-swap ĐẶC BIỆT phổ biến cho Q2 (compare). Peripheral Source hiếm.

> **🔍 Single-side & Cross-swap — bẫy ĐẶC TRƯNG dạng 統合理解**:
> - **Single-side**: distractor đúng với A hoặc B (không phải cả 2) → câu hỏi điểm chung A&B sẽ rơi vào bẫy này
> - **Cross-swap (Role reversal)**: đảo thứ tự "A nói X, B nói Y" → "A nói Y, B nói X". Đặc biệt cho Q2 compare.
> - Q2 BẮT BUỘC ≥ 2 distractor là Single-side hoặc Cross-swap.


### R6.3 Explanation format — 3 phần BẮT BUỘC (VN + EN)

> **Explanation không chỉ "có nội dung" — nó phải CHỨNG MINH câu hỏi + đáp án đúng có logic.**
> Đọc hiểu tổng hợp = 2 đoạn A + B (hoặc 3 sections advice). Explanation PHẢI **trích dẫn rõ ràng từ A và từ B** (đặc biệt với Q2 compare), nêu thứ tự chủ thể để loại trừ distractor đảo vai.

#### Phần 1 — Đáp án đúng (BẮT BUỘC trích cả A và B cho Q2)
- Nêu rõ "Đáp án đúng: (X)" + nội dung paraphrase
- **Trích dẫn từ A** (vd: "Trong A, tác giả viết: `「...」`")
- **Trích dẫn từ B** (vd: "Trong B, tác giả viết: `「...」`") — BẮT BUỘC cho Q2 compare
- Cho Q1 focus 1 đoạn: chỉ cần trích đoạn tương ứng + nêu rõ đoạn nào (A hay B)
- Cho Q2 compare: phải so 2 trích dẫn → kết luận điểm chung / điểm khác / cách tích hợp

#### Phần 2 — Đáp án sai (TỪNG đáp án + loại bẫy đặc thù tổng hợp)
- Đi qua **TẤT CẢ 3 đáp án sai** (1 đáp án 1 dòng), không bỏ sót
- Mỗi đáp án sai phải nêu:
  1. **Loại bẫy** (Role reversal A/B / Single-side / Mix A+B / Scope / Extreme / Extraneous)
  2. **Trích cụ thể** từ A hoặc B chứng minh sai (vd: "A thực ra nói X, không phải Y như đáp án")
- **Role reversal** đặc thù dạng này: phải nêu rõ "Đáp án nói A → X, B → Y nhưng thực ra A → Y, B → X" (đảo thứ tự chủ thể)
- **Single-side**: phải nêu rõ "Chỉ khớp A (hoặc B) nhưng đáp án presented như cả 2"
- **Extraneous**: phải nêu rõ "Cả A và B đều không nói ý này"
- KHÔNG dùng câu chung chung — phải chỉ rõ A hay B, ý nào trong đoạn đủ để bác bỏ

#### Phần 3 — Tóm tắt chiến lược
- 1-2 câu: chiến lược giải Q1/Q2 (vd: "Q2 compare → đọc kỹ thesis A và thesis B, kiểm tra thứ tự chủ thể trong đáp án để loại role reversal")

### R6.4 Ví dụ explain VN cho Q2 compare — BÀI N1 mẫu

**Bài N1** (giả tưởng — topic AI và sáng tạo):
- **A**: AI là công cụ hỗ trợ, không thể thay thế sáng tạo con người vì AI không có "động cơ ý thức". Cuối A: 「AIはあくまで道具にすぎず、人間の創造性を代替するものではない」.
- **B**: AI có thể tạo ý tưởng mới qua kết hợp dữ liệu, nhưng cần con người đánh giá để chọn ý tưởng có giá trị. Cuối B: 「AIは新しい着想を生み出すが、それを意味あるものに育てるのは人間である」.

**Question 2** (Q2 compare):
> AとBのAIに対する考え方について、最も適切なものはどれか。

**Answers** (4 options, no prefix):
```
AはAIの速度を重視し、Bは品質を重視している
AもBもAIを人間の創造性を支える道具として位置づけている
AはAIが新しい着想を生み出すと述べ、Bはそれを否定している
AもBもAIを完全に否定し、人間だけで創造すべきだと主張している
```

**correct_answer**: 2

**explain_vn**:
```
ĐÁP ÁN ĐÚNG (2): AもBもAIを人間の創造性を支える道具として位置づけている (Cả A và B đều xác định AI là công cụ hỗ trợ sáng tạo của con người).
Trong A, tác giả viết: 「AIはあくまで道具にすぎず、人間の創造性を代替するものではない」 (AI suy cho cùng chỉ là công cụ, không thể thay thế sáng tạo con người).
Trong B, tác giả viết: 「AIは新しい着想を生み出すが、それを意味あるものに育てるのは人間である」 (AI tạo ý tưởng mới, nhưng nuôi nó thành thứ có ý nghĩa là việc của con người).
Tích hợp: Dù góc nhìn khác (A nhấn "công cụ thuần", B nhấn "AI có ý tưởng nhưng cần người đánh giá"), CẢ HAI đều xem AI như công cụ hỗ trợ con người — thesis chung của 2 đoạn.

ĐÁP ÁN SAI:
(1) AはAIの速度を重視し、Bは品質を重視している — Role reversal A/B: Bài KHÔNG nói A quan tâm tốc độ hay B quan tâm chất lượng. Thực tế A bàn về "giới hạn của AI" còn B bàn về "tiềm năng của AI" — đảo vai chủ đề.
(3) AはAIが新しい着想を生み出すと述べ、Bはそれを否定している — Role reversal: ĐẢO NGƯỢC. Thực ra B mới là người nói AI tạo ý tưởng mới (「新しい着想を生み出す」), A nói AI không thay thế sáng tạo con người. Đáp án gán đảo phát ngôn của A và B.
(4) AもBもAIを完全に否定し... — Extreme/Extraneous: Cả A và B đều KHÔNG phủ nhận AI hoàn toàn. A nói AI "あくまで道具" (vẫn là công cụ), B đề cao AI tạo ý tưởng. Đáp án dùng từ extreme "完全に否定" sai trầm trọng.

Tóm tắt: Q2 compare → đọc kỹ thesis cuối A và thesis cuối B, kiểm tra THỨ TỰ chủ thể trong đáp án so với bài để loại role reversal (1, 3). Loại đáp án dùng từ extreme (4) — cả A và B đều có quan điểm trung dung.
```

**explain_en**:
```
CORRECT ANSWER (2): AもBもAIを人間の創造性を支える道具として位置づけている (Both A and B position AI as a tool supporting human creativity).
In A, the author writes: 「AIはあくまで道具にすぎず、人間の創造性を代替するものではない」 (AI is ultimately just a tool, not a replacement for human creativity).
In B, the author writes: 「AIは新しい着想を生み出すが、それを意味あるものに育てるのは人間である」 (AI generates new ideas, but humans cultivate them into something meaningful).
Integration: Despite different angles (A emphasizes "pure tool," B emphasizes "AI generates but needs human judgment"), BOTH view AI as a tool supporting humans — the shared thesis.

WRONG ANSWERS:
(1) AはAIの速度を重視し、Bは品質を重視している — Role reversal A/B: Article does NOT discuss A on speed or B on quality. A actually discusses AI's "limits" while B discusses AI's "potential" — fabricated topic reversal.
(3) AはAIが新しい着想を生み出すと述べ、Bはそれを否定している — Role reversal: REVERSED. B is the one stating AI generates new ideas (「新しい着想を生み出す」); A states AI doesn't replace human creativity. Option swaps A's and B's claims.
(4) AもBもAIを完全に否定し... — Extreme/Extraneous: Neither A nor B fully rejects AI. A says AI is "still a tool" while B emphasizes AI's idea generation. The extreme word "完全に否定" is severely incorrect.

Summary: For Q2 compare → read A's closing thesis and B's closing thesis carefully, check SUBJECT ORDER in options vs article to eliminate role reversal (1, 3). Eliminate extreme-word options (4) — both A and B hold moderate views.
```

**Explanation phải bằng cả 2 ngôn ngữ (VN + EN)** với cùng nội dung logic — không phải dịch máy.

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
