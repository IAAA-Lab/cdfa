#!/usr/bin/env python3
import argparse
from collections import defaultdict

def parse_file(path):
    data = defaultdict(set)
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or ":" not in line:
                continue
            sec_part, labels_part = line.split(":", 1)
            sec = sec_part.replace("Section", "").strip()
            labels = [x.strip() for x in labels_part.split(",") if x.strip()]
            for lab in labels:
                data[lab].add(sec)
    return data

def safe_div(a, b):
    return a / b if b else 0.0

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--subjects", required=True)
    ap.add_argument("--results", required=True)
    args = ap.parse_args()

    subjects = parse_file(args.subjects)
    results = parse_file(args.results)

    concepts = sorted(subjects.keys())
    p_list, r_list, f1_list = [], [], []

    for c in concepts:
        relevant = subjects[c]
        retrieved = results.get(c, set())

        tp_set = relevant & retrieved
        fp_set = retrieved - relevant
        fn_set = relevant - retrieved

        tp = len(tp_set)
        fp = len(fp_set)
        fn = len(fn_set)

        precision = safe_div(tp, tp + fp)
        recall = safe_div(tp, tp + fn)
        f1 = safe_div(2 * precision * recall, precision + recall)

        p_list.append(precision)
        r_list.append(recall)
        f1_list.append(f1)

        print(f"\nConcept: {c}")
        print(f"  Relevant sections (TP+FN): {sorted(relevant)}")
        print(f"  Retrieved sections (TP+FP): {sorted(retrieved)}")
        print(f"  TP sections: {sorted(tp_set)}")
        print(f"  FP sections: {sorted(fp_set)}")
        print(f"  FN sections: {sorted(fn_set)}")
        print(f"  TP={tp}, FP={fp}, FN={fn}")
        print(f"  Precision={precision:.4f}")
        print(f"  Recall={recall:.4f}")
        print(f"  F1={f1:.4f}")

    # Macro averages
    macro_precision = sum(p_list) / len(p_list) if p_list else 0.0
    macro_recall = sum(r_list) / len(r_list) if r_list else 0.0
    macro_f1 = sum(f1_list) / len(f1_list) if f1_list else 0.0

    print("\n===== FINAL MACRO SCORES =====")
    print(f"Macro Precision: {macro_precision:.4f}")
    print(f"Macro Recall:    {macro_recall:.4f}")
    print(f"Macro F1:        {macro_f1:.4f}")

if __name__ == "__main__":
    main()

# Usage:
# python eval_sections.py --subjects subjects.txt --results results.txt
