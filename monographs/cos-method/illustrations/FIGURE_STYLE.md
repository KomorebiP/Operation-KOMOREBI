# Figure production system

Every chart is an independent 6.37-inch-wide canvas, matching the book's text
block. PDF and SVG are the vector masters. PNG is a preview. Titles are 12 pt,
axis labels 9.4 pt, ticks 8.5 pt, evidence kickers 7.1 pt, and scope notes 7.8 pt.
Legends reserve measured space below the title. Long labels are wrapped rather
than shrunk into unreadable text. Fonts are named dependencies, not bundled files.

The palette uses plum (#403348) for primary/exact objects, teal (#34777A) for
represented or approximate objects, ochre (#9D742D) for bounds, and rust
(#A24E46) for failure. Categorical measurements use explicit labels and markers.
Do not use color as the only indication of a scientific distinction.

Keep zeros at zero, label infinite values, show every retained observation in
the selected data series, and distinguish a mathematical bound from a directed
numerical enclosure. Do not smooth experimental curves or invent unavailable
raw vectors. Scope notes identify model predictions and historical timings.

The generator checks figure text bounds and finite line/scatter data against
axis limits. These checks supplement rendered inspection. They do not detect
all possible overlap or independently validate numerical measurements.
