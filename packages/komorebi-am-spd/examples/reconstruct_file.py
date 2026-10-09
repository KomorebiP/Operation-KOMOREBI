from pathlib import Path

from am_spd import AMSpdConfig, load_image, reconstruct, save_image

input_path = Path("input.png")
output_path = Path("output.png")

image = load_image(input_path)
result = reconstruct(image, AMSpdConfig.quick(method="spd"))
save_image(output_path, result.bounded_reconstruction())
result.save_archive(output_path.with_suffix(".npz"))
