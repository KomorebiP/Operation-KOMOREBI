from am_spd import (
    AMSpdConfig,
    fit_packet_core,
    fit_singular_packets,
    load_image,
    optimize_trees,
    save_image,
)

image = load_image("input.png")
config = AMSpdConfig.quick("tree")
core = fit_packet_core(image, config)
spd = fit_singular_packets(image, core, config)
trees = optimize_trees(image, core, spd, config)

save_image("tree-reconstruction.png", trees.reconstruction)
print(trees.selected_name)
print(trees.candidate_rmse)
print(len(trees.exact.frontier))
