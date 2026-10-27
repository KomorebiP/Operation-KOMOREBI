CLAIM_STATUS = [
    {
        "statement": "Exact packet block reconstruction",
        "status": "proved",
        "scope": "finite matrices with a declared complete projector family",
    },
    {
        "statement": "Block, block-sparse, and BDLR apply/storage formulas",
        "status": "proved",
        "scope": "arithmetic and representation counts",
    },
    {
        "statement": "Woodbury packet solve and exact compressed BDLR product",
        "status": "proved",
        "scope": "when the stated inverses exist",
    },
    {
        "statement": "Packet preconditioner condition-number bound",
        "status": "proved",
        "scope": "SPD diagonal packet part and normalized coupling norm below one",
    },
    {
        "statement": "Packet mixed-precision error certificate",
        "status": "proved",
        "scope": "operator-norm block errors with declared packet inputs",
    },
    {
        "statement": "GPU and CPU timings in the supplied corpus",
        "status": "measured",
        "scope": "reported Windows/PyTorch/OpenBLAS environment only",
    },
    {
        "statement": "A packet method is universally faster",
        "status": "false as a universal claim",
        "scope": "negative controls and crossover cases are retained",
    },
    {
        "statement": "Packet structure improves the generic matrix-multiplication exponent",
        "status": "not claimed",
        "scope": "structure-sensitive and generic dense problems are separated",
    },
    {
        "statement": "An automatic compiler can always find the optimal packet decomposition",
        "status": "conjectural",
        "scope": "requires discovery, cost, and stability guarantees",
    },
    {
        "statement": "A packet-native accelerator is asymptotically optimal",
        "status": "conjectural",
        "scope": "hardware co-design proposal only",
    },
]
