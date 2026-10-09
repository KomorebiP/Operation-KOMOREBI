"""Select a method and budget from a declared finite grid."""

from am_spd import auto_tune, load_image, tuning_candidates

image = load_image("input.png")
candidates = tuning_candidates(
    methods=("core", "spd", "portfolio"),
    packet_budgets=(8, 12, 16),
)
result = auto_tune(
    image,
    candidates,
    objective="rate-distortion",
    rate_weight=0.01,
)
result.save_report("tuning.json")
result.save_csv("tuning.csv")
result.best_result.save_model("best.amspd", include_input=True)

print(result.best_config)
print(result.best_result.summary())
