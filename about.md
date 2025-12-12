---
title: William Mallard, Ph.D.
photo: portrait.jpg
---

I am a biologist and engineer with two decades of experience working across hardware, software, and the lab bench. I hold a PhD in Biochemistry from Harvard University, and a BSc in Engineering Physics from UC Berkeley, with minors in Computer Science and Mathematics.

I work on computational biology for target discovery -- integrating structure, omics, and imaging to find and prioritize targets, and to trace how they work from molecule to phenotype. I also build high-performance computational systems to make that integration work at scale.

## PhD: Structural & Cell Biology

[PhD projects →](portfolio.html?era=phd)

My research focused on the disordered tail of FtsZ, the protein that builds the bacterial division ring. I combined structural modeling, protein biophysics, and live-cell microscopy to uncover a novel phospho-switch: FtsZ's disordered tail binds its folded core on a polymerization surface, and phosphorylation of the tail disrupts this binding -- encouraging FtsZ polymerization and shortening cells.

I predicted the tail-core interaction computationally, generating 5,000 AlphaFold-Multimer structures and clustering their contact maps to identify binding modes. I tested these predictions at the bench via NMR and ITC, and then mapped the structural mechanism by which phosphorylation disrupts binding.

I then traced the effects of binding disruption across scales -- from residues to filaments to cells. I developed an *in vitro* assay to measure changes in FtsZ polymerization, and I designed microscopy experiments and computer vision pipelines to quantify the impact on cell size.

## Broad: Genomics & Infrastructure

[Broad projects →](portfolio.html?era=broad)

Before my PhD, I spent four years at the Broad Institute. I started as a software engineer in the Cancer Genome Atlas, where I helped keep a production genomics platform running across tens of thousands of tumor samples. I triaged pipeline failures and rewrote memory-intensive R scripts into streaming Python. At one point, I traced one such failure to an issue in the Python standard library and contributed an upstream fix to CPython.

I then worked as a computational biologist in the Rinn Lab. I built custom pipelines for more than twenty genomics projects -- using RNA-seq, ChIP-seq, ATAC-seq, and bisulfite sequencing to measure changes in expression, transcription factor binding, histone modification, and chromatin compaction. I contributed to thirteen papers on lncRNAs, stem-cell biology, and developmental epigenetics.

## Berkeley: Signal Processing & Astronomy

[Berkeley projects →](portfolio.html?era=berkeley)

Before the Broad, I was a systems engineer at Berkeley building real-time signal-processing systems for radio telescopes. I started in CASPER, where I contributed DSP blocks to an open-source FPGA toolkit. I also wrote a 10 Gbps network receiver used in the transport layer of the Square Kilometre Array, and I helped build and deploy a spectrometer at Arecibo Observatory.

In the Townes Lab, I then built a digital correlator for an infrared telescope array used to image the dust shell of Betelgeuse. The system spec demanded clocking the FPGAs at nearly double the rate of any prior CASPER design. To achieve this, I refactored all FFT arithmetic onto hardened DSP48E blocks and hand-guided logic placement on an FPGA fabric packed to near-full capacity. I built the instrument end-to-end and deployed it at Mount Wilson Observatory.

## College: Instrumentation & Networking

[College projects →](portfolio.html?era=college)

I started building physics instrumentation in college. I wrote a control system for a helium dilution fridge cooling bolometers to sub-kelvin temperatures for experimental cosmologists. I also built a pulse sequencer to shuttle particles around a planar ion trap for quantum computing.

In parallel, I fell in with the systems crowd at Berkeley, learning networking and Linux sysadmin from housemates. For three years, I ran the network in my 125-person student co-op, pulling cable, building servers, and tuning firewall and QoS rules. This steered me to CS systems coursework, and to a stint as a sysadmin for Berkeley's HPC cluster. After college, I briefly worked for a startup writing network software.
