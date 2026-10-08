"""
Chay lai V2 tu file da luu + ghi report + tao bang so sanh.
Tai su dung: evidence/03_rag_outputs_v1.json, evidence/03_rag_outputs_v2.json
"""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import warnings
warnings.filterwarnings("ignore")

import numpy as np
from ragas import evaluate, EvaluationDataset, SingleTurnSample
from ragas.metrics import faithfulness, answer_relevancy, context_recall, context_precision

from utils.llm_factory import get_llm, get_embeddings

EVIDENCE = Path(__file__).parent.parent / "evidence"

# Load V1 outputs da luu
v1_results = json.loads((EVIDENCE / "03_rag_outputs_v1.json").read_text(encoding="utf-8"))
v2_results = json.loads((EVIDENCE / "03_rag_outputs_v2.json").read_text(encoding="utf-8"))
print(f"[OK] Loaded: {len(v1_results)} V1 + {len(v2_results)} V2 samples")

# Build dataset
def build_dataset(results):
    samples = [
        SingleTurnSample(
            user_input=r["question"],
            response=r["answer"],
            retrieved_contexts=r["contexts"],
            reference=r["reference"],
        )
        for r in results
    ]
    return EvaluationDataset(samples=samples)

# Rerun V2 (V1 da co chi tiet)
print("\n[STEP] Dang cham V2 (tu file da luu)...")
v2_ds = build_dataset(v2_results)
llm_eval = get_llm(temperature=0)
emb_eval = get_embeddings()

result_v2 = evaluate(
    v2_ds,
    metrics=[faithfulness, answer_relevancy, context_recall, context_precision],
    llm=llm_eval,
    embeddings=emb_eval,
    raise_exceptions=True,
)

# Luu chi tiet V2
result_v2.to_pandas().to_json(
    EVIDENCE / "03_ragas_v2_details.json",
    orient="records", force_ascii=False, indent=2,
)

v2_scores = {}
for key in ["faithfulness", "answer_relevancy", "context_recall", "context_precision"]:
    raw = result_v2[key]
    v2_scores[key] = float(np.mean([v for v in raw if v is not None]))

print(f"V2 scores: {v2_scores}")

# Tinh V1 scores tu file chi tiet da luu
v1_details = json.loads((EVIDENCE / "03_ragas_v1_details.json").read_text(encoding="utf-8"))
v1_scores = {
    "faithfulness":      float(np.mean([s["faithfulness"]       for s in v1_details])),
    "answer_relevancy":  float(np.mean([s["answer_relevancy"]   for s in v1_details])),
    "context_recall":    float(np.mean([s["context_recall"]      for s in v1_details])),
    "context_precision":  float(np.mean([s["context_precision"]   for s in v1_details])),
}

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

# Luu report JSON
report = {
    "prompt_v1_scores": v1_scores,
    "prompt_v2_scores": v2_scores,
    "target_met": bool(best_faith >= 0.8),
}
report_path = Path(__file__).parent.parent / "data" / "ragas_report.json"
report_path.parent.mkdir(exist_ok=True)
report_path.write_text(json.dumps(report, indent=2, allow_nan=False), encoding="utf-8")
print(f"[SAVE] Da luu: {report_path}")

# Copy sang evidence
(EVIDENCE / "03_ragas_report.json").write_text(
    json.dumps(report, indent=2, allow_nan=False), encoding="utf-8"
)
print(f"[SAVE] Da copy: {EVIDENCE / '03_ragas_report.json'}")
