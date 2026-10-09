from pathlib import Path

from am_spd import AMSpdConfig, reconstruct, save_image
from am_spd.atlas import synthetic_geometry

output = Path("am_spd_example")
output.mkdir(exist_ok=True)

image = synthetic_geometry(32)
result = reconstruct(image, AMSpdConfig.quick(method="portfolio"))

save_image(output / "input.png", image)
save_image(output / "reconstruction.png", result.bounded_reconstruction())
result.save_archive(output / "reconstruction.npz")
print(result.summary())
