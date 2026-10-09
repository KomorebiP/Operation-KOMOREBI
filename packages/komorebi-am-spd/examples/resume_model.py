"""Create and resume a schema-2 AM-SPD packet checkpoint."""

from pathlib import Path

from am_spd import AMSpdConfig, AMSpdModel, load_image, reconstruct, save_image

image = load_image("input.png")
initial = reconstruct(image, AMSpdConfig.quick(method="core"))
initial.save_model(
    "checkpoint.amspd",
    include_input=True,
    include_atoms=True,
    residual_storage="sparse",
)

checkpoint = AMSpdModel.load("checkpoint.amspd")
continued = checkpoint.resume(target_packet_budget=32)
continued.save_model("continued.amspd", include_input=True)
save_image(Path("continued.png"), continued.bounded_reconstruction())

print(checkpoint.resume_state_quality)
print(continued.summary())
