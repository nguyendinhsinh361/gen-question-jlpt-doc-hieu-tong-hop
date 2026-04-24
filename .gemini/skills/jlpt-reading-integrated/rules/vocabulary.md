# Rules: Từ vựng, Ngữ pháp & Furigana (R3, R4)

> **Scope**: Đọc hiểu tổng hợp (統合理解 / integrated) — **CHỈ N1 & N2**.

## R3. Trình độ kiến thức (Kanji, Từ vựng, Ngữ pháp)

### Nguyên tắc tổng quát

| Level | Kanji/Từ vựng cốt lõi | Ngữ pháp cốt lõi |
|-------|----------------------|-------------------|
| **N2** | ~1000 kanji + ~6000 từ | ～に伴い, ～に基づき, ～を踏まえて, ～に限り, ～とはいえ, ～からこそ, ～かねる, ～ずにはいられない, ～について |
| **N1** | ~2000 kanji + ~10000 từ | ～いかんによらず, ～をもって, ～に先立ち, ～にほかならない, ～というものだ, ～ざるを得ない, ～に足る, keigo văn viết cao |

### Golden principle — "THAY TỪ, KHÔNG RẮC FURIGANA"

Nếu bài N2 dùng quá nhiều kanji N1 → **viết lại bằng từ N2**, không phải rắc furigana bừa bãi.

**Furigana dùng khi không có cách nào thay thế khác** — ví dụ thuật ngữ chuyên môn không có từ level phù hợp.

### Văn phong luận thuyết ngắn (BẮT BUỘC)

Đọc hiểu tổng hợp = 2 opinion piece ngắn, mỗi đoạn súc tích:

- **N1**: luận thuyết cao cấp (keigo văn viết `～であろう`, `～にほかならない`, `～ざるを得ない`). Câu tập trung, lập luận chặt.
- **N2**: formal trung cấp (`～に伴い`, `～を踏まえて`, `～とはいえ`, `～からこそ`). Câu vừa phải, có dùng `である` thay `だ`.

**Đặc thù 2-section**: văn phong A và B có thể **khác nhau chút** (VD A cautious, B assertive) để tăng độ đối lập nhưng vẫn trong cùng level.

### Cấu trúc A và B nhất quán trong 1 bài

- A và B nên dùng **cùng level kanji/ngữ pháp** (không được A quá khó hơn B rõ ràng)
- Cả A và B cùng là văn luận thuyết (không 1 bên kể chuyện, 1 bên editorial)

### Ruby count density per level (đọc hiểu tổng hợp)

| Level | Above-level words | Ruby `<ruby>` expected |
|-------|-------------------|------------------------|
| **N2** | 0–3               | 0–5                    |
| **N1** | 0–2               | 0–3                    |

> **Lưu ý đặc thù**: Data gốc **cả N1 và N2 đều = 0% ruby**. Bài ngắn (300-400 chars/section) ít cần từ chuyên môn đến mức phải furigana.
>
> **Khuyến nghị mạnh**: 0 ruby mỗi bài. Chỉ dùng khi thực sự không thể thay từ khác.

> **Nguyên tắc**: ≥ 90% từ vựng/ngữ pháp phải ở đúng level. Ruby chỉ cho phần vượt level không thể tránh.

---

## R4. Furigana — Quy tắc & Kanji lookup

### R4.1 Compound Word Rule — CẤM dạng "Ab"

**LUÔN viết nguyên bộ kanji** rồi đặt furigana bao toàn bộ. **TUYỆT ĐỐI KHÔNG** tách nửa kanji nửa hiragana.

Chỉ chọn 1 trong 2:

1. **Full kanji + furigana**: `<ruby>構築<rt>こうちく</rt></ruby>`
2. **Full hiragana** (khi ở level thấp): `こうちく`

**❌ CẤM**: `構ちく`, `友だち`, `拠てん`, `経けん`

**✅ Ngoại lệ Okurigana**: `<ruby>届<rt>とど</rt></ruby>く` — furigana chỉ phủ kanji, okurigana đứng riêng ngoài ruby.

### R4.2 Furigana Lookup Procedure

Bước 1: **Xác định level kanji** bằng `rules/jlpt_kanji.csv` (2150 kanji).

Bước 2: **Nếu kanji > level bài** → thêm furigana:

```html
<ruby>構築<rt>こうちく</rt></ruby>
```

Bước 3: **Nếu kanji ≤ level bài** → KHÔNG thêm furigana.

### R4.3 Ví dụ áp dụng

| Từ | Level kanji | Bài N2 | Bài N1 |
|----|-------------|--------|--------|
| 構築 (こうちく) | N1 | `<ruby>構築<rt>こうちく</rt></ruby>` | 構築 (không furigana) |
| 普遍的 (ふへんてき) | N2 | 普遍的 (không furigana) | 普遍的 (không furigana) |
| 経験 (けいけん) | N3 | 経験 (không furigana) | 経験 (không furigana) |
| 社会 (しゃかい) | N4 | 社会 (không furigana) | 社会 (không furigana) |

### R4.4 Số lượng ruby cho đọc hiểu tổng hợp

Bài ngắn 600-800 chars (300-400/section), data thực tế **cả 2 level = 0% ruby** — skill giữ ruby cực ít.

**Dấu hiệu rắc furigana sai**:
- Bài N1 có > 3 ruby tag → quá nhiều — viết lại bằng từ N1 level
- Bài N2 có > 5 ruby tag → quá nhiều — viết lại bằng từ N2 level
- Có ruby cho từ cơ bản như `社会`, `問題`, `考える`, `人間` ở bài N2 → thừa
- Ruby tag kéo dài hơn 6 ký tự hiragana → từ quá vượt level, nên thay từ khác

### R4.5 Không dùng `注` annotation

Data N1=4%, N2=0% — đọc hiểu tổng hợp bài ngắn **không có** annotation. Nếu từ khó đến mức cần giải thích → **thay từ đơn giản hơn** thay vì thêm 注.

### R4.6 Tên riêng (name)

Đọc hiểu tổng hợp **không có** source line, nên không có tên tác giả riêng lẻ. Format advice có thể có 相談者/回答者Ａ/回答者Ｂ — đây là **nhãn vai trò**, không phải tên người — không cần furigana.

Nếu bài có dẫn ví dụ tên người (hiếm): dùng tên đơn giản (田中, 山本) — không cần furigana ở level N1/N2.
