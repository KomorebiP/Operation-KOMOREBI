from am_spd import AMSpdConfig, AMSpdModel, load_image, reconstruct, save_image

image = load_image("input.png")
initial = reconstruct(image, AMSpdConfig.quick("core"))
initial.save_model(
    "checkpoint.amspd",
    residual_storage="sparse",
    include_input=True,
)

checkpoint = AMSpdModel.load("checkpoint.amspd")
refined = checkpoint.resume(target_packet_budget=32, method="portfolio")
refined.save_model("refined.amspd", residual_storage="sparse")
save_image("refined.png", refined.bounded_reconstruction())
print(refined.summary())
