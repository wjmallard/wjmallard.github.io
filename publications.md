# publications.md — single source of truth for publications.html
# Build:  python3 build_publications.py   (or ./build.sh to regenerate the whole site)
#
# Lines starting with "# " are comments. Format:
#   @subtitle: <page subtitle>
#   @scholar: <url>                (Google Scholar profile; linked from the metrics line)
#   @metric: <label> | <value>     (repeatable; rendered as the Scholar-credited line)
#   @me: <surname>                 (bolded wherever it appears in an authors: list, and
#                                   used to derive the author-position badge)
#   @theme <key> | <chip label>    (declares a Skill chip; order here = chip order)
#   @era <key> | <chip label>      (declares an Era chip; order here = chip order)
#   ## <Section name>
#   ### <Paper title>              (linked to its DOI when doi: is set)
#   authors: <full list>           (required; comma separated, "F.M. Lastname" style)
#   venue: <journal or book>       (required)
#   year: <year>                   (required; entries sort newest-first within a section)
#   detail: <volume(issue), pages> (optional; printed after the venue)
#   doi: <bare DOI>                (optional; e.g. 10.1371/journal.pone.0337820)
#   era: <key>                     (one of the @era keys; unknown key fails the build)
#   themes: key, key, ...          (@theme keys; unknown key fails the build)
#   slug: <anchor id>              (the entry's HTML id; defaults to the slugified title)
#   role: <text>                   (overrides the auto-derived author-position badge —
#                                   use it where the byline is a consortium)
#   page: <dirname under projects/> (adds a "Write-up" link; build fails if
#                                    projects/<dirname>/index.md does not exist)
#   link: <Label> | <url>          (repeatable; extra links — code, data, PDF)
#   note: <text>                   (never reaches the HTML; a reminder for future-us)
#
# Gotcha: same as portfolio.md — an unrecognized "key: value" line is NOT ignored. It
# falls through and gets appended to the entry's authors list verbatim.

@scholar: https://scholar.google.com/citations?user=nspsptcAAAAJ

# No @metric lines by design: h-index, i10-index and citation totals all go stale the
# moment they're written down. The Scholar link above carries them, live, off-site.
# To show the h-index anyway, uncomment the line below -- it renders as a labelled
# figure above the Scholar link, and nothing else needs changing:
# @metric: h-index | 14

@me: Mallard

@theme structbio | Structural Biology
@theme genomics | Genomics
@theme bioinfo | Bioinformatics
@theme microscopy | Microscopy
@theme signal | Signal Processing
@theme instrument | Instrumentation
@theme systems | Systems & Firmware
@theme hpc | HPC
@theme cv | Computer Vision

@era phd | PhD
@era broad | Broad
@era berkeley | Berkeley
@era undergrad | Undergrad


## Bacterial Cell Division

### FtsZ phosphorylation modulates tail-core binding to tune cell division in Bacillus subtilis
authors: W.J. Mallard, V.V. Pham
venue: PLOS ONE
year: 2025
detail: 20(12), e0337820
doi: 10.1371/journal.pone.0337820
era: phd
themes: structbio, bioinfo, microscopy, hpc, cv
role: First and co-corresponding author

### FtsZ phosphorylation modulates tail-core binding to tune cell division in Bacillus subtilis
slug: ftsz-phd-thesis
authors: W.J. Mallard
venue: PhD thesis, Harvard University
year: 2025
detail: ProQuest 32042133
era: phd
themes: structbio, bioinfo, microscopy, hpc, cv
link: ProQuest | https://www.proquest.com/docview/3216865596
note: not indexed by Scholar

## Gene Regulation

### Common variants in signaling transcription-factor-binding sites drive phenotypic variability in red blood cell traits
authors: A. Choudhuri, E. Trompouki, B.J. Abraham, L.M. Colli, K.H. Kock, W. Mallard, M.L. Yang, D.S. Vinjamur, A. Ghamari, A. Sporrij, K. Hoi, B. Hummel, S. Boatman, V. Chan, S. Tseng, S.K. Nandakumar, S. Yang, A. Lichtig, M. Superdock, S.N. Grimes, T.V. Bowman, Y. Zhou, S. Takahashi, R. Joehanes, A.B. Cantor, D.E. Bauer, S.K. Ganesh, J. Rinn, P.S. Albert, M.L. Bulyk, S.J. Chanock, R.A. Young, L.I. Zon
venue: Nature Genetics
year: 2020
detail: 52(12), 1333-1345
doi: 10.1038/s41588-020-00738-2
era: broad
themes: genomics, bioinfo, hpc

### A distant trophoblast-specific enhancer controls HLA-G expression at the maternal-fetal interface
authors: L.M.R. Ferreira, T.B. Meissner, T.S. Mikkelsen, W. Mallard, C.W. O'Donnell, T. Tilburgs, H.A.B. Gomes, R. Camahort, R.I. Sherwood, D.K. Gifford, J.L. Rinn, C.A. Cowan, J.L. Strominger
venue: PNAS
year: 2016
detail: 113(19), 5364-5369
doi: 10.1073/pnas.1602886113
era: broad
themes: genomics, bioinfo, hpc

### Dissecting neural differentiation regulatory networks through epigenetic footprinting
authors: M.J. Ziller, R. Edri, Y. Yaffe, J. Donaghey, R. Pop, W. Mallard, R. Issner, C.A. Gifford, A. Goren, J. Xing, H. Gu, D. Cacchiarelli, A.M. Tsankov, C. Epstein, J.L. Rinn, T.S. Mikkelsen, O. Kohlbacher, A. Gnirke, B.E. Bernstein, Y. Elkabetz, A. Meissner
venue: Nature
year: 2015
detail: 518(7539), 355-359
doi: 10.1038/nature13990
era: broad
themes: genomics, bioinfo, hpc


## Stem Cells & Epigenomics

### Defective insulin receptor signaling in hPSCs skews pluripotency and negatively perturbs neural differentiation
authors: A.K.K. Teo, L. Nguyen, M.K. Gupta, H.H. Lau, L.S.W. Loo, N. Jackson, C.S. Lim, W. Mallard, M.A. Gritsenko, J.L. Rinn, R.D. Smith, W.J. Qian, R.N. Kulkarni
venue: Journal of Biological Chemistry
year: 2021
detail: 296, 100495
doi: 10.1016/j.jbc.2021.100495
era: broad
themes: genomics, bioinfo, hpc

### Targeted disruption of DNMT1, DNMT3A and DNMT3B in human embryonic stem cells
authors: J. Liao, R. Karnik, H. Gu, M.J. Ziller, K. Clement, A.M. Tsankov, V. Akopian, C.A. Gifford, J. Donaghey, C. Galonska, R. Pop, D. Reyon, S.Q. Tsai, W. Mallard, J.K. Joung, J.L. Rinn, A. Gnirke, A. Meissner
venue: Nature Genetics
year: 2015
detail: 47(5), 469-478
doi: 10.1038/ng.3258
era: broad
themes: genomics, bioinfo, hpc

### A comparison of genetically matched cell lines reveals the equivalence of human iPSCs and ESCs
authors: J. Choi, S. Lee, W. Mallard, K. Clement, G.M. Tagliazucchi, H. Lim, I.Y. Choi, F. Ferrari, A.M. Tsankov, R. Pop, G. Lee, J.L. Rinn, A. Meissner, P.J. Park, K. Hochedlinger
venue: Nature Biotechnology
year: 2015
detail: 33(11), 1173-1181
doi: 10.1038/nbt.3388
era: broad
themes: genomics, bioinfo, hpc


## Long Noncoding RNAs

### Rroid2 regulates effector-to-memory CD8+ T cell differentiation during infection in vivo
authors: J. Erber, C. Stecher, V. Plajer, N. Braun, W. Mallard, L.A. Goff, I. Barozzi, T. Mohr, J.L. Rinn, R.A. Flavell, D. Herndler-Brandstetter
venue: PNAS
year: 2025
detail: 122(48), e2503450122
doi: 10.1073/pnas.2503450122
era: broad
themes: genomics, bioinfo, hpc

### The Firre locus produces a trans-acting RNA molecule that functions in hematopoiesis
authors: J.P. Lewandowski, J.C. Lee, T. Hwang, H. Sunwoo, J.M. Goldstein, A.F. Groff, N.P. Chang, W. Mallard, A. Williams, J. Henao-Meija, R.A. Flavell, J.T. Lee, C. Gerhardinger, A.J. Wagers, J.L. Rinn
note: "Henao-Meija" is how the paper printed it; the author's name is actually Henao-Mejia
venue: Nature Communications
year: 2019
detail: 10(1), 5137
doi: 10.1038/s41467-019-12970-4
era: broad
themes: genomics, bioinfo, hpc

### Chromatin environment, transcriptional regulation, and splicing distinguish lincRNAs and mRNAs
authors: M. Melé, K. Mattioli, W. Mallard, D.M. Shechner, C. Gerhardinger, J.L. Rinn
venue: Genome Research
year: 2017
detail: 27(1), 27-37
doi: 10.1101/gr.214205.116
era: broad
themes: genomics, bioinfo, hpc

### Multiple knockout mouse models reveal lincRNAs are required for life and brain development
authors: M. Sauvageau, L.A. Goff, S. Lodato, B. Bonev, A.F. Groff, C. Gerhardinger, D.B. Sanchez-Gomez, E. Hacisuleyman, E. Li, M. Spence, S.C. Liapis, W. Mallard, M. Morse, M.R. Swerdel, M.F. D'Ecclessis, J.C. Moore, V. Lai, G. Gong, G.D. Yancopoulos, D. Frendewey, M. Kellis, R.P. Hart, D.M. Valenzuela, P. Arlotta, J.L. Rinn
venue: eLife
year: 2013
detail: 2, e01749
doi: 10.7554/eLife.01749
era: broad
themes: genomics, bioinfo, hpc


## Cancer Genomics

### Comprehensive molecular profiling of lung adenocarcinoma
authors: The Cancer Genome Atlas Research Network
venue: Nature
year: 2014
detail: 511(7511), 543-550
doi: 10.1038/nature13385
era: broad
themes: genomics, hpc
role: TCGA Research Network -- listed contributor
note: byline is the consortium; W. Mallard is #175 of 383 in the PubMed collaborator list

### The somatic genomic landscape of glioblastoma
authors: The Cancer Genome Atlas Research Network
venue: Cell
year: 2013
detail: 155(2), 462-477
doi: 10.1016/j.cell.2013.09.034
era: broad
themes: genomics, hpc
role: TCGA Research Network -- listed contributor
note: 59-name byline + consortium; W. Mallard is #153 of 242 in the PubMed collaborator list

### Comprehensive molecular characterization of clear cell renal cell carcinoma
authors: The Cancer Genome Atlas Research Network
venue: Nature
year: 2013
detail: 499(7456), 43-49
doi: 10.1038/nature12222
era: broad
themes: genomics, hpc
role: TCGA Research Network -- listed contributor
note: byline is the consortium; W. Mallard is #164 of 346 in the PubMed collaborator list

### Integrated genomic characterization of endometrial carcinoma
authors: The Cancer Genome Atlas Research Network
venue: Nature
year: 2013
detail: 497(7447), 67-73
doi: 10.1038/nature12113
era: broad
themes: genomics, hpc
role: TCGA Research Network -- listed contributor
note: printed byline is the consortium plus 18 named authors (Levine et al.), elided here to match the other three; W. Mallard is #116 of 313 in the PubMed collaborator list


## Technology Development

### Live-cell mapping of organelle-associated RNAs via proximity biotinylation combined with protein-RNA crosslinking
authors: P. Kaewsapsak, D.M. Shechner, W. Mallard, J.L. Rinn, A.Y. Ting
venue: eLife
year: 2017
detail: 6, e29224
doi: 10.7554/eLife.29224
era: broad
themes: genomics, bioinfo, hpc


## Physics & Astronomy Instrumentation

### Current and nascent SETI instruments in the radio and optical
authors: A. Siemion, H. Chen, J. Cobb, J. Cordes, T. Filiba, A. Fries, A. Howard, J. von Korff, E. Korpela, M. Lebofsky, W. Mallard, P. McMahon, A. Parsons, L. Spitler, M. Wagner, D. Werthimer
venue: Communication with Extraterrestrial Intelligence (CETI)
year: 2011
detail: pp. 19-36
doi: 10.2307/jj.18254198.7
era: berkeley
themes: instrument, signal, systems

### Mid-infrared interferometry with high spectral resolution
authors: E.H. Wishnow, W. Mallard, V. Ravi, S. Lockwood, W. Fitelson, D. Werthimer, C.H. Townes
venue: Optical and Infrared Interferometry II (Proc. SPIE)
year: 2010
detail: 7734, 773409
doi: 10.1117/12.857656
era: berkeley
themes: instrument, signal, systems
link: Code | https://github.com/wjmallard/isi-digital-backend

### Experimental investigation of planar ion traps
authors: C.E. Pearson, D.R. Leibrandt, W.S. Bakr, W.J. Mallard, K.R. Brown, I.L. Chuang
venue: Physical Review A
year: 2006
detail: 73(3), 032307
doi: 10.1103/PhysRevA.73.032307
era: undergrad
themes: instrument, systems


## Conference Proceedings & Abstracts

### Long noncoding RNA-124 regulates CD8+ T cell response to infection
authors: J. Erber, C. Stecher, V. Plajer, N. Braun, W. Mallard, L. Goff, J. Zhao, et al.
venue: European Journal of Immunology
year: 2024
detail: 54, 263
era: broad
themes: genomics, hpc
role: Co-author
note: meeting abstract; no DOI, and Scholar truncates the author list

### Transcriptional signaling centers govern human erythropoiesis and harbor genetic variations of red blood cell traits
authors: A. Choudhuri, E. Trompouki, B.J. Abraham, L. Colli, W. Mallard, M.L. Yang, D. Vinjamur, A. Ghamari, S. Nandakumar, K. Hoi, B. Hummel, S. Boatman, V. Chan, T.V. Bowman, S. Yang, Y. Zhou, S. Takahashi, A.B. Cantor, V.G. Sankaran, S. Ganesh, D.E. Bauer, J. Rinn, S.J. Chanock, R.A. Young, L.I. Zon
venue: Blood
year: 2018
detail: 132(Suppl 1), 1277
doi: 10.1182/blood-2018-99-118637
era: broad
themes: genomics, hpc

### Distinct signaling centers define stages of human erythropoiesis and harbor common variations of red blood cell traits
authors: A. Choudhuri, E. Trompouki, B.J. Abraham, W. Mallard, M.L. Yang, A. Ghamari, K. Hoi, B. Hummel, S. Boatman, V. Chan, T.V. Bowman, S. Yang, Y. Zhou, S. Takahashi, A.B. Cantor, S. Ganesh, J. Rinn, R.A. Young, L.I. Zon
venue: Blood
year: 2017
detail: 130(Suppl 1), 773
doi: 10.1182/blood.V130.Suppl_1.773.773
era: broad
themes: genomics, hpc

### Long-range chromatin interactions control trophoblast-restricted HLA-G expression during pregnancy
authors: L. Ferreira, T. Meissner, T. Mikkelsen, C. O'Donnell, R. Sherwood, W. Mallard, J. Rinn, C. Cowan, J. Strominger
venue: The Journal of Immunology
year: 2015
detail: 194(1 Suppl), 60.7
doi: 10.4049/jimmunol.194.supp.60.7
era: broad
themes: genomics, hpc

### Lineage regulators and signaling transcription factors during erythropoiesis
authors: A. Choudhuri, B. Abraham, W. Mallard, B. Hummel, S. Boatman, T. Bowman, A. DiBiase, J. Rinn, R. Young, L. Zon, E. Trompouki
venue: Experimental Hematology
year: 2014
detail: 42(8), S63
doi: 10.1016/j.exphem.2014.07.239
era: broad
themes: genomics, hpc

### Long non-coding RNA expression in normal and leukemic human blood samples
authors: B. Lehnertz, G. Boucher, W. Mallard, P. Gendron, J. Hebert, S. Lemieux, J. Rinn, G. Sauvageau
venue: Experimental Hematology
year: 2014
detail: 42(8), S45
doi: 10.1016/j.exphem.2014.07.166
era: broad
themes: genomics, hpc

### Developments in the radio search for extraterrestrial intelligence
authors: A.P.V. Siemion, D. Werthimer, D. Anderson, H. Chen, J. Cobb, J. Cordes, T. Filiba, G. Foster, S. Gowda, E. Korpela, M. Lebofsky, A. Little, W. Mallard, L. Spitler, M. Wagner
venue: URSI General Assembly and Scientific Symposium
year: 2011
detail: pp. 1-4
doi: 10.1109/ursigass.2011.6051263
era: berkeley
themes: instrument, signal, systems
note: found via a Crossref author sweep; Scholar does not index it at all

### Advanced multi-beam spectrometer for the Green Bank Telescope
authors: D.A. Roshi, M. Bloss, P. Brandt, S. Bussa, H. Chen, P. Demorest, G. Desvignes, T. Filiba, R.J. Fisher, J. Ford, D. Frayer, R. Garwood, S. Gowda, G. Jones, W. Mallard, J. Masters, R. McCullough, G. Molera, K. O'Neil, J. Ray, S. Scott, A. Shelton, A. Siemion, M. Wagner, G. Watts, D. Werthimer, M. Whitehead
venue: URSI General Assembly and Scientific Symposium
year: 2011
doi: 10.1109/ursigass.2011.6051280
era: berkeley
themes: instrument, signal, systems
note: printed byline reads "Billy Mallard"; normalized here to W. Mallard

### Wideband FPGA spectrometers and correlators
authors: T. Filiba, H. Chen, S. Gowda, W. Mallard, J. Manley, P. McMahon, A. Siemion, L. Spitler, M. Wagner, D. Werthimer
venue: USNC/URSI National Radio Science Meeting
year: 2009
detail: p. 32
era: berkeley
themes: instrument, signal, systems
note: meeting abstract, no DOI; Scholar truncates this author list, so it was filled in by hand
