#!/usr/bin/env python3
"""
load_references.py — Load & pretty-print sample JSON của "đọc hiểu tổng hợp" cho AI agent.

Đọc các file `data/doc_hieu_tong_hop_n{1,2}_clean.json` (ở project root) và in ra:
  - Stats tổng quan (count, min/max/p25/p50/p75/avg jp_char_count, phân bố Q count/bài)
  - Random samples theo level (để gen agent calibrate style, 2-đoạn A+B)
  - 1 sample cụ thể theo id

Chỉ có N1 và N2 — các level khác KHÔNG CÓ kind "đọc hiểu tổng hợp".

Usage
-----
python3 load_references.py --stats
python3 load_references.py --level N2 --count 1
python3 load_references.py --level N1 --id 101
python3 load_references.py --level N1 --count 2 --seed 42
python3 load_references.py --data-dir /some/other/data --stats
"""

from __future__ import annotations

import argparse
import json
import os
import random
import statistics
import sys
from collections import Counter
from pathlib import Path


LEVELS = ["N1", "N2"]


def default_data_dir() -> str:
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent.parent.parent.parent
    candidate = project_root / "data"
    if candidate.exists():
        return str(candidate)
    return str(Path.cwd() / "data")


def data_path(data_dir: str, level: str) -> str:
    n = level.lower()
    return os.path.join(data_dir, f"doc_hieu_tong_hop_{n}_clean.json")


def load_level(data_dir: str, level: str) -> list[dict]:
    path = data_path(data_dir, level)
    if not os.path.exists(path):
        print(f"  [warn] Missing file: {path}", file=sys.stderr)
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        print(f"  [warn] {path} root is not a list", file=sys.stderr)
        return []
    return data


def percentile(values: list[int], pct: float) -> int:
    if not values:
        return 0
    s = sorted(values)
    k = (len(s) - 1) * (pct / 100.0)
    lo, hi = int(k), min(int(k) + 1, len(s) - 1)
    if lo == hi:
        return s[lo]
    return int(round(s[lo] + (s[hi] - s[lo]) * (k - lo)))


def print_stats(data_dir: str) -> None:
    print(f"Data dir: {data_dir}\n")
    header = f"{'Level':<6}{'Count':>7}{'Min':>7}{'P25':>7}{'P50':>7}{'P75':>7}{'Avg':>7}{'Max':>7}  Q-dist"
    print(header)
    print("-" * len(header))
    for level in LEVELS:
        samples = load_level(data_dir, level)
        counts = [int(s.get("jp_char_count", 0) or 0) for s in samples]
        counts = [c for c in counts if c > 0]
        qcounts = Counter(len(s.get("content", []) or []) for s in samples)
        q_dist = ", ".join(f"{k}q:{v}" for k, v in sorted(qcounts.items()))
        if not counts:
            print(f"{level:<6}{'0':>7}{'-':>7}{'-':>7}{'-':>7}{'-':>7}{'-':>7}{'-':>7}  -")
            continue
        print(
            f"{level:<6}"
            f"{len(samples):>7}"
            f"{min(counts):>7}"
            f"{percentile(counts, 25):>7}"
            f"{percentile(counts, 50):>7}"
            f"{percentile(counts, 75):>7}"
            f"{int(statistics.mean(counts)):>7}"
            f"{max(counts):>7}  "
            f"{q_dist}"
        )
    print()
    print("Target ranges (từ SKILL.md — tổng A+B):")
    print("  N1: 600-750  |  N2: 600-800")
    print()
    print("Số câu hỏi CHUẨN (từ rules/question_format.json):")
    print("  N1: 2 câu/bài  |  N2: 2 câu/bài")
    print()
    print("Label BẮT BUỘC cho MỌI câu: question_comprehensive_understanding.")
    print("(từ rules/kind_mission_mapping.json — 'required_question_label')")
    print()
    print("Cấu trúc bài: 2 đoạn A + B (cùng chủ đề, quan điểm khác/bổ sung).")
    print("  Biến thể: 相談者 + 回答者A + 回答者B (advice format, <10% data).")
    print()
    print("Lưu ý: N3, N4, N5 KHÔNG có kind 'đọc hiểu tổng hợp'.")


def format_sample(sample: dict) -> str:
    lines = []
    sid = sample.get("id")
    chars = sample.get("jp_char_count")
    kind = sample.get("kind", "?")
    level = sample.get("level", "?")
    content = sample.get("content", []) or []
    lines.append(f"── Sample id={sid} | level=N{level} | kind={kind} | chars={chars} (A+B tổng) | {len(content)} câu ──")
    txt = sample.get("general_text_read", "")
    lines.append(f"\n[general_text_read]")
    lines.append(txt)
    for i, q in enumerate(content, 1):
        lines.append(f"\n[Q{i}] {q.get('question','')}")
        answers = q.get("answers", []) or []
        correct = q.get("correctAnswer", None)
        for j, a in enumerate(answers):
            mark = "  ✅" if correct == j else "   "
            lines.append(f"  {j+1}.{mark} {a}")
        if correct is not None:
            lines.append(f"  → correctAnswer (source, 0-based) = {correct}  ⇒ CSV correct_answer = {correct + 1}")
    return "\n".join(lines) + "\n"


def pick_samples(data_dir: str, level: str, count: int, seed: int | None) -> list[dict]:
    samples = load_level(data_dir, level)
    if not samples:
        return []
    rng = random.Random(seed)
    k = min(count, len(samples))
    return rng.sample(samples, k)


def pick_by_id(data_dir: str, level: str, sid: int) -> dict | None:
    samples = load_level(data_dir, level)
    for s in samples:
        if s.get("id") == sid:
            return s
    return None


def main():
    ap = argparse.ArgumentParser(description="Load JLPT đọc hiểu tổng hợp reference samples (N1, N2 only).")
    ap.add_argument("--data-dir", default=default_data_dir(),
                    help="Thư mục chứa data JSON (default: auto-detect <project-root>/data)")
    ap.add_argument("--stats", action="store_true", help="In stats per level")
    ap.add_argument("--level", choices=LEVELS, help="Level to load (N1 or N2)")
    ap.add_argument("--count", type=int, default=1, help="Số sample random (default 1 — 2-đoạn A+B)")
    ap.add_argument("--id", type=int, help="Cụ thể id của sample")
    ap.add_argument("--seed", type=int, help="Random seed")

    args = ap.parse_args()

    if args.stats:
        print_stats(args.data_dir)
        return

    if not args.level:
        print("Cần --level hoặc --stats.", file=sys.stderr)
        ap.print_help()
        sys.exit(2)

    if args.id is not None:
        sample = pick_by_id(args.data_dir, args.level, args.id)
        if sample is None:
            print(f"Không tìm thấy sample id={args.id} trong {args.level}.", file=sys.stderr)
            sys.exit(1)
        print(format_sample(sample))
        return

    samples = pick_samples(args.data_dir, args.level, args.count, args.seed)
    if not samples:
        print(f"Không có sample ở {args.level}.", file=sys.stderr)
        sys.exit(1)
    print(f"Loaded {len(samples)} random sample(s) from {args.level} (seed={args.seed}):\n")
    for s in samples:
        print(format_sample(s))


if __name__ == "__main__":
    main()
