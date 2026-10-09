from pathlib import Path

from am_spd import AMSpdConfig, AMSpdModel, load_image, reconstruct, save_image

image = load_image("input.png")
result = reconstruct(image, AMSpdConfig.quick("portfolio"))
model_path = result.save_model("image.amspd", residual_storage="sparse")

model = AMSpdModel.load(model_path)
save_image("approximation.png", model.decode("bounded"))

Path("inspection.json").write_text(
    __import__("json").dumps(
        {
            "summary": model.summary(),
            "packets": model.packet_table(),
            "trees": model.tree_table(),
        },
        indent=2,
    )
    + "\n",
    encoding="utf-8",
)
