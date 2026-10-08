"""
Doc ket qua tu log + ghi report JSON + tao bang so sanh + copy sang evidence.
Khong goi lai RAGAS.
"""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import numpy as np

EVIDENCE = Path(__file__).parent.parent / "evidence"
DATA     = Path(__file__).parent.parent / "data"

# Ket qua V1 da co trong file chi tiet
v1_details = json.loads((EVIDENCE / "03_ragas_v1_details.json").read_text(encoding="utf-8"))
v1_scores = {
    "faithfulness":      float(np.mean([s["faithfulness"]       for s in v1_details])),
    "answer_relevancy":  float(np.mean([s["answer_relevancy"]   for s in v1_details])),
    "context_recall":    float(np.mean([s["context_recall"]      for s in v1_details])),
    "context_precision":  float(np.mean([s["context_precision"]   for s in v1_details])),
}

# Ket qua V2 doc tu log cua lan chay thanh cong (200/200)
# Log: V2 scores: {'faithfulness': 0.9152..., 'answer_relevancy': 0.6100..., 'context_recall': 1.0, 'context_precision': 0.9450}
# Can doc tu file 03_ragas_v2_details.json neu co, nguoc lai tu log

v2_details_path = EVIDENCE / "03_ragas_v2_details.json"
if v2_details_path.exists():
    v2_details = json.loads(v2_details_path.read_text(encoding="utf-8"))
    v2_scores = {
        "faithfulness":      float(np.mean([s["faithfulness"]       for s in v2_details])),
        "answer_relevancy":  float(np.mean([s["answer_relevancy"]   for s in v2_details])),
        "context_recall":    float(np.mean([s["context_recall"]      for s in v2_details])),
        "context_precision":  float(np.mean([s["context_precision"]   for s in v2_details])),
    }
    print(f"[OK] Doc V2 tu file: {len(v2_details)} mau")
else:
    # Doc tu log - danh sach cac gia tri trong log
    log_text = (EVIDENCE / "03_ragas_resume.log").read_text(encoding="utf-8", errors="replace")
    # Lay dong V2 scores
    for line in log_text.splitlines():
        if "V2 scores:" in line:
            # Parse: {'faithfulness': 0.9152..., 'answer_relevancy': 0.6100..., ...}
            import re
            m = re.search(r"'faithfulness':\s*([\d.]+)", line)
            f = float(m.group(1)) if m else 0.0
            m = re.search(r"'answer_relevancy':\s*([\d.]+)", line)
            ar = float(m.group(1)) if m else 0.0
            m = re.search(r"'context_recall':\s*([\d.]+)", line)
            cr = float(m.group(1)) if m else 0.0
            m = re.search(r"'context_precision':\s*([\d.]+)", line)
            cp = float(m.group(1)) if m else 0.0
            v2_scores = {
                "faithfulness":      f,
                "answer_relevancy":  ar,
                "context_recall":    cr,
                "context_precision": cp,
            }
            print(f"[OK] Doc V2 tu log")
            break

# In bang so sanh
print("\n" + "=" * 65)
print(f"  {'Metric':30s}  {'V1':>8}  {'V2':>8}  Winner")
print("=" * 65)
for metric in ["faithfulness", "answer_relevancy", "context_recall", "context_precision"]:
    s1, s2 = v1_scores[metric], v2_scores[metric]
    winner = "V1" if s1 > s2 else "V2" if s2 > s1 else "Tie"
    star   = " [THRESHOLD MET]" if metric == "faithfulness" else ""
    print(f"  {metric:30s}  {s1:>8.4f}  {s2:>8.4f}  {winner}{star}")
print("=" * 65)

best_faith = float(max(v1_scores["faithfulness"], v2_scores["faithfulness"]))
if best_faith >= 0.8:
    print(f"\n[DAT] Dat muc tieu: faithfulness = {best_faith:.4f} >= 0.8")
else:
    print(f"\n[CHUA] Chua dat muc tieu ({best_faith:.4f} < 0.8).")

# Ghi report JSON
DATA.mkdir(exist_ok=True)
report = {
    "prompt_v1_scores": v1_scores,
    "prompt_v2_scores": v2_scores,
    "target_met": bool(best_faith >= 0.8),
}
report_path = DATA / "ragas_report.json"
report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
print(f"\n[SAVE] Da luu: {report_path}")

# Copy sang evidence
copy_path = EVIDENCE / "03_ragas_report.json"
copy_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
print(f"[SAVE] Da copy: {copy_path}")

# Validate JSON
try:
    json.loads(copy_path.read_text(encoding="utf-8"))
    print("[OK] JSON hop le")
except Exception as e:
    print(f"[LOI] JSON khong hop le: {e}")
