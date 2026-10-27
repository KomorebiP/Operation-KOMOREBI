# Technical basis

## Internal algorithmic basis

- Dense Transfer Algebra supplies PMR-GEMM, compatible middle bases, Kronecker rules, sparse factor chains, transform-domain planning, and the generic fallback.
- Projector-Resolved Seed Calculus VIII supplies exact block and BDLR formulas, compressed products, Woodbury solves, packet Krylov methods, mixed-precision bounds, amortization rules, CUDA Graph replay, and the measured structured-operator corpus.
- The packet CUDA backend supplies the working software route through grouped matrix kernels, FFT and sparse libraries, asynchronous transfers, graph replay, compressed output, and packetwise certification.

These algorithms are architecture inputs. PRISM does not claim them as consequences of the chip.

## External interface baseline

The reference package uses public primary specifications and product information:

- UCIe Consortium, UCIe 3.0 specification information
- PCI-SIG, PCI Express 7.0 specification information
- Micron, HBM4 product information
- RISC-V International, ratified V Standard Extension for Vector Operations, Version 1.0

The public baselines support 48 and 64 GT/s UCIe 3.0 package links, 128 GT/s PCIe 7.0, 36 GB HBM4 with a 2048-bit interface and more than 2.8 TB/s per stack, and the ratified RISC-V Vector 1.0 programming model.

These sources support the interface assumptions only. PRISM performance figures come from the included architecture model or from the separately identified packet CUDA measurements.
