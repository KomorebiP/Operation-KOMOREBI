from am_spd import reproduce_paper_case

result = reproduce_paper_case(
    "synthetic_geometry",
    output_dir="paper-replay",
    strict_reference=True,
)

print(result.summary)
print(result.comparison)
