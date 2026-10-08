import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

scores = {
    "faithfulness":       (0.9530, 0.9152),
    "answer_relevancy":   (0.9164, 0.6100),
    "context_recall":     (1.0000, 1.0000),
    "context_precision":  (0.9450, 0.9450),
}
metrics = list(scores.keys())
v1_vals = [v[0] for v in scores.values()]
v2_vals = [v[1] for v in scores.values()]

fig, ax = plt.subplots(figsize=(10, 5))
ax.axis("off")

col_labels = ["Metric", "V1", "V2", "Winner"]
table_data = []
for m in metrics:
    s1, s2 = scores[m]
    winner = "V1" if s1 > s2 else "V2" if s2 > s1 else "Tie"
    flag   = " <-- WINNER" if m == "faithfulness" else ""
    table_data.append([m, f"{s1:.4f}", f"{s2:.4f}", winner + flag])

table = ax.table(
    cellText=table_data,
    colLabels=col_labels,
    cellLoc="center",
    loc="center",
)
table.auto_set_font_size(False)
table.set_fontsize(12)
table.scale(1.2, 2.0)

# Style header
for j in range(4):
    table[(0, j)].set_facecolor("#2C3E50")
    table[(0, j)].set_text_props(color="white", fontweight="bold")

# Style rows
for i in range(1, 5):
    bg = "#E8F4F8" if i % 2 == 0 else "white"
    for j in range(4):
        table[(i, j)].set_facecolor(bg)

# Highlight winner column
for i in range(1, 5):
    cell = table[(i, 3)]
    val  = cell.get_text().get_text()
    if "WINNER" in val:
        cell.set_facecolor("#D5F5E3")
        cell.set_text_props(fontweight="bold", color="#1E8449")

ax.set_title(
    "RAGAS Evaluation Results — V1 vs V2\n"
    "faithfulness >= 0.8 threshold MET (V1: 0.9530, V2: 0.9152)",
    fontsize=13, fontweight="bold", pad=15,
)

plt.tight_layout()
out = __file__.parent.parent / "evidence" / "03_ragas_scores.png"
plt.savefig(out, dpi=150, bbox_inches="tight", facecolor="white")
print(f"[SAVE] {out}")
