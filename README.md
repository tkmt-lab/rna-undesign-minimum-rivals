# Minimum rival covers for 108 RNA-Undesign motifs

For 108 fixed motif instances, this package records the smallest number of rival structures needed to prevent the target from being the unique minimum-energy structure for every compatible sequence. The minima range from one to six. Their sum over the 108 rows is 310; this is not a set of 310 distinct structures covering every motif at once.

The source instances are the 108 data rows with `N_Rival >= 2` in the 1,805-row `results.uniq.csv` of [RNA-Undesign](https://github.com/shanry/RNA-Undesign/tree/8a8de22). The original CSV and its motif strings are **not bundled**. Users retrieve the pinned input separately. Row numbers count data rows from one, excluding the header.

| Minimum rivals | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---:|---:|---:|---:|---:|---:|
| Instances | 10 | 31 | 40 | 19 | 6 | 2 |

## Model and finite claim

The checker requires **ViennaRNA 2.7.2**, Turner 2004 parameters, 37 C, dangles=2, special hairpins enabled, and isolated and GU pairs allowed. It uses the integer `eval_structure_pt` API, in units of 0.01 kcal/mol. Salt is 1.021 M; circular RNA, G-quadruplexes and logarithmic multiloops are disabled.

In the motif notation, `(*)` is an indivisible boundary pair. For energy evaluation it becomes a three-A hairpin: the structure is `(...)` and the three internal sequence letters are fixed to `AAA`. The outer pair and every boundary pair are retained by the target and all candidate rivals. Every other position may be paired or unpaired in a noncrossing candidate; a terminal hairpin must contain at least three unpaired letters. A boundary pair is already a closed child, not three available letters in the motif grammar. The target itself is excluded from the candidate set.

Target pairs, including the outer and boundary pairs, allow AU, UA, GC, CG, GU or UG. Other unfixed unpaired positions allow A, C, G or U. A rival covers a sequence when every rival pair is compatible and its energy is **at most** the target energy. Ties therefore count: the claim concerns unique-MFE designability. The finite input contains 300,119,040 sequence assignments in total.

Each certificate gives k upper rivals and a nonempty finite set of lower witness sequences. The upper certificate covers the entire specified sequence space. For the lower certificate, no k-1 candidates from the complete boundary-preserving candidate set cover the witnesses. Witness sets and file sizes are not claimed to be minimum.

## Run the checks

Python 3.11 or later is required. From the repository root:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python -B tools/manifest.py
python -B tools/fetch_source.py
python -B checkers/verify.py
python -B checkers/negative_controls.py
```

The input is [`data/motifs_maxlen14_no_external/results.uniq.csv`](https://raw.githubusercontent.com/shanry/RNA-Undesign/8a8de22/data/motifs_maxlen14_no_external/results.uniq.csv). The fetcher downloads this fixed `8a8de22` raw CSV into ignored `work/source/`, and stops unless its SHA-256 is `a06d6cc495c36c50b4292e260ebc89d54d3dbd422b99fd2ebfae66431ff59041`. To use an existing copy instead, pass `--from-file /path/to/results.uniq.csv`. The checker verifies the CSV digest, each row's motif digest and the exact 108 selected row IDs before using them. A motif digest hashes the decoded `Motif` field as UTF-8, without stripping, normalization or an added newline. Stored rivals retain compressed `(*)` boundaries; lower witness sequences use the expanded coordinates with the three internal A letters.

The default smoke check regenerates the candidate grammar and checks **all 108 lower bounds**, then exhaustively checks upper coverage for three cases: m0081 (k=4), m0335 (k=2) and m1780 (k=1), totaling 539,136 sequences. It does not rerun all upper covers. On the assembly machine it took about 6 seconds; timings vary. JSON results go to ignored `work/checks/`.

`tools/manifest.py` checks the supplied `manifest.json`; it does not regenerate expected hashes unless a maintainer explicitly passes `--update`. A successful check prints JSON with `status: PASS` and exits zero. `negative_controls.py` intentionally damages five inputs or certificates and passes only when each is rejected. It prints `status: PASS`, exits zero and records details in `work/checks/negative-controls.json`; unexpected acceptance or another failure exits nonzero.

```sh
# Every upper cover, in addition to all lower bounds:
python -B checkers/verify.py --full --output work/checks/full.json
# Upper cover for a selected row; all lower bounds are still checked:
python -B checkers/verify.py --case m0025 --output work/checks/m0025.json
```

A complete run took about 55 minutes in one process on the assembly machine (Apple silicon); its record is in `validation/`. It runs in one process and does not use the search implementation. A failure reports the row and, for a missed upper cover, a counterexample sequence. Optimized Python (`-O`) is refused. CI is configured for smoke, negative controls and the stored-record check, not the full enumeration.

## Files and verification boundary

- `data/results.csv`: row IDs, counts, minima and motif digests.
- `data/certificates.json`: laboratory-computed rivals and witness sequences, with the same row IDs and digests. See [data/README.md](data/README.md) for encodings.
- `checkers/`: candidate grammar, integer-energy adapter and certificate checks. No search code is imported.
- `paper/report-B-v1.1-en.pdf` and TeX: short mathematical report, Version 1.1 (current). Versions 0 and 1 and the exact diffs `paper/v0-to-v1.diff` and `paper/v1-to-v1.1.diff` are kept.
- `validation/full-check.json`, `validation/full-check-meta.json`: output of one complete `--full` run of this checker on these files, with the SHA-256 of every input file. `checkers/check_full_record.py` confirms that the record covers all 108 rows and 300,119,040 sequences and that the files have not changed since.
- `VERIFICATION-RECORD.md`: previous independent checks and the scope of this package's assembly checks.
- `SOURCE-PERMISSIONS.md`: source-data permission findings and the non-bundling decision.

The earlier full independent certificate check covered 108/108 cases and all 300,119,040 sequences, using ViennaRNA 2.7.2. This package's checker was subsequently assembled from the research-side certificate grammar, so its runs, including the stored complete run, are not a new blind independent review. The code and thermodynamic model are not formally verified, and the report has not undergone human peer review.

These results concern the fixed candidate and sequence spaces above. They make no claim for unrestricted RNA, other thermodynamic parameters, pseudoknots, experimental molecules, or being the first result of this kind.

## Source, credit and permissions

The motif instances and rival-based undesignability framework come from Tianshuo Zhou, Wei Yu Tang, Apoorv Malik, David H. Mathews and Liang Huang' RNA-Undesign work: RIGENDE (RECOMB 2024, [arXiv:2311.08339](https://arxiv.org/abs/2311.08339)) and FastMotif (RECOMB 2025, [arXiv:2402.17206](https://arxiv.org/abs/2402.17206)). ViennaRNA provides the thermodynamic evaluation ([Lorenz et al., 2011](https://doi.org/10.1186/1748-7188-6-26)). Their work made these calculations possible; I am grateful for the public instances, definitions and software.

The included row IDs, minima, rival structures, witness sequences, counts and motif digests are laboratory-computed results obtained by applying the stated procedure to the source instances. The motif strings themselves must be obtained from the original data by the user. No LICENSE file or redistribution grant was identified in the fixed or current RNA-Undesign repository during assembly; this package does not supply a license for those source data. See `SOURCE-PERMISSIONS.md` for remaining derived structural fragments.

The laboratory-authored code is Apache-2.0. The report and laboratory-authored result material are offered under CC-BY-4.0 to the extent of the laboratory's rights; these terms do not grant rights in third-party source material. See `LICENSE` and `licenses/`. Cite this package and the original work using `CITATION.cff`.

Tatsuhiko Takimoto is responsible for this report. AI systems assisted with the calculations, certificate checks, literature comparison, code and writing; the verification record distinguishes their roles and dependencies. This is a local pre-publication draft; no release DOI has been assigned.
