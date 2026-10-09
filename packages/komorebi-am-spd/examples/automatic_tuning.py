from am_spd import AMSpdConfig, auto_tune, load_image, save_image, tuning_candidates

image = load_image("input.png")
candidates = tuning_candidates(
    AMSpdConfig.quick(),
    methods=("core", "spd", "tree", "portfolio"),
    packet_budgets=(8, 12, 16),
)
result = auto_tune(image, candidates, objective="rate-distortion", rate_weight=0.01)
result.save_report("tuning.json")
result.save_csv("tuning.csv")
result.best_result.save_model("best.amspd", residual_storage="sparse")
save_image("best.png", result.best_result.bounded_reconstruction())
print(result.summary())
