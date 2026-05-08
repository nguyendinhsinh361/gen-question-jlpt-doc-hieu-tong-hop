# Prompt — Gen bài Đọc Hiểu Tổng Hợp (JLPT 統合理解)

## Cách dùng

Copy prompt bên dưới, thay `{số}` rồi paste vào Claude hoặc Gemini.

**⛔ Scope chỉ 2 level**: **N1** (2 câu, A+B ~600–750 chars) và **N2** (2 câu, A+B ~600–800 chars). 2 đoạn A và B cùng topic, khác quan điểm. Q2 BẮT BUỘC compare A vs B. Label CỐ ĐỊNH `question_comprehensive_understanding` cho cả 2 câu.

> **🚨 ZERO-TOLERANCE WORKFLOW**: SKILL.md có **5 GATE bắt buộc** (0→1, 1→2, 2→3, 3→4, 4→5). Mỗi gate phải log `GATE X→Y PASSED`. **1 mục FAIL = sửa/gen lại → QC TỪ ĐẦU**, đến khi 34/34 PASS mới hoàn thành.

---

## Prompt

```
Đọc .claude/skills/jlpt-reading-integrated/SKILL.md rồi gen bài đọc hiểu tổng hợp:
- N2: {số} bài (2 câu, A+B ~600–800 chars)
- N1: {số} bài (2 câu, A+B ~600–750 chars)

⛔ CHỈ N1 và N2. Lưu CSV: sheets/samples_v1.csv. HTML: assets/html/doc_hieu_tong_hop/{LEVEL}_{uuid}.html.

🔒 5 GATE bắt buộc — KHÔNG QUA = KHÔNG SANG BƯỚC TIẾP. Log explicit GATE X→Y PASSED.

═══ BƯỚC 0 — CHUẨN BỊ (1 lần) → GATE 0→1 ═══
Đọc đầy đủ:
- rules/rule_doc_hieu.md (Phần 2.4 thể chia toàn 普通形 cả A+B, Phần 5 — 7 loại bẫy + **Single-side ĐẶC TRƯNG cho 統合 + Cross-swap A/B + Peripheral Source cho N1**, Phần 9.3 N2 統合 + Phần 10.4 N1 統合)
- rules/{content,vocabulary,technical,questions}.md + rules/kanji_jlpt_sensei.csv
- Load 2 sample/level: scripts/load_references.py --level {LEVEL} --count 2
- Scan sheets/samples_v1.csv
GATE 0→1: tick 6/6 → log "GATE 0→1 PASSED".

═══ BƯỚC 1 — GEN HTML A+B + 2 Q+A → GATE 1→2 ═══
1. _id = {LEVEL}_{uuid32}
2. Chọn relationship: contrast / complement / debate / advice (3-section 相談者+回答者Ａ+Ｂ, ~5% N2)
3. Tag = **tiếng Anh** từ rules/topic.json
4. Gen HTML: container 780px, <p> thuần (KHÔNG <br>, KHÔNG <table>)
   - 2 sections: <section class="passage-a"> + <section class="passage-b">, mỗi section <span class="label">A|B</span>; 2–4 <p>/section
   - Mỗi đoạn 40–60% tổng chars; chênh lệch ≤ 30%. **Toàn 普通形 cả A và B**
   - Furigana chỉ vượt level (cấm "Ab"); ưu tiên 0 ruby (data thực tế = 0%)
   - Marker ①② chỉ Q1 A-focus (Combo 3); Q2 KHÔNG có marker
5. Gen 2 Q + 4 đáp án (newline \n, KHÔNG prefix); **label CỐ ĐỊNH question_comprehensive_understanding cho Q1+Q2**
   - Q2 BẮT BUỘC compare A vs B (dùng AとB / AもBも / AとBで共通 / AとBの違い). Đáp án Q2 PHẢI cần info CẢ A+B
   - Distractor Q2 BẮT BUỘC ≥ 2: **Single-side** (chỉ khớp A hoặc B) + **Cross-swap** (A nói X→Y, B nói Y→X)
   - Đa dạng 7 loại bẫy: Reversal/Detail Swap/Fabrication/Scope/Mixing/Single-side/Cross-swap
6. Tạo CSV bằng process_html.py + fill_qa.py (label cố định auto-fill)
GATE 1→2: tick 5/5 → log "GATE 1→2 PASSED".

═══ BƯỚC 2-3 — QC 34 MỤC → GATE 2→3 + GATE 3→4 ═══
GATE 2→3: cam kết check ĐẦY ĐỦ 34 mục → log "GATE 2→3 PASSED".
Đánh giá 34 mục: A. HTML+AB balance 13 + B. Content 6 (toàn 普通形 cả A và B) + C. Q&A 11 (label cố định, paraphrase ≥4 từ N1 / ≥5 N2, explain VN+EN trích cả A+B cho Q2, self-solve khớp, **đặc biệt check Cross-swap**) + D. Compare coverage 4.
**Cross-swap check**: thứ tự "A nói X, B nói Y" trong distractor có ngược với bài không? Nếu ngược → đó là Cross-swap (sai).
GATE 3→4: liệt kê FAIL + diagnosis → log "GATE 3→4 PASSED".

═══ BƯỚC 4-5 — SỬA + LẶP → GATE 4→5 ═══
- Fix HTML → `--refresh`. Fix Q&A → fill_qa.py
- ≥ 50% FAIL / self-solve FAIL / Q2 không compare A vs B / A-B balance vỡ / char Hard Reject → **GEN LẠI** (giữ _id)
- Quay lại GATE 2→3 → QC 34/34 TỪ ĐẦU
- Tối đa 5 vòng → báo user
GATE 4→5: 34/34 PASS + --validate clean → log "🎉 ALL PASSED (34/34) + GATE 4→5 PASSED" → bài tiếp.

═══ HARD REJECT (gen lại ngay) ═══
- Q count khác 2 (slot 3-5 phải empty); label khác question_comprehensive_understanding
- Q2 không compare A vs B (chỉ về A, chỉ về B, hoặc kiến thức ngoài)
- A/B balance vỡ: 1 đoạn < 40% hoặc > 60% tổng chars
- Char range ngoài: N1 600–750 | N2 600–800
- HTML thiếu <section class="passage-a/b"> hoặc <span class="label">A|B</span>; có <table> hoặc <br>
- <ruby> thiếu <rt>; furigana "Ab"; thể chia có です・ます (cả A và B phải toàn 普通形)
- Q2 distractor không có Single-side hoặc Cross-swap
- Tag tiếng Việt/Nhật; trùng topic; <2 relationship type khác nhau (khi N≥2 bài)

═══ CUỐI BATCH ═══
python3 .claude/skills/jlpt-reading-integrated/scripts/process_html.py --validate --html-dir assets/html/doc_hieu_tong_hop --csv sheets/samples_v1.csv
```
