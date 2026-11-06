# Minimum rival covers for 108 RNA-Undesign motifs

Package **v1.0.0 — 2026-11-11**. [Repository](https://github.com/tkmt-lab/rna-undesign-minimum-rivals). DOI: none recorded.

For 108 fixed RNA-Undesign motif instances, the minimum number of rival structures needed to rule out a unique minimum-energy target for every target-compatible sequence ranges from one to six.
The values apply to fixed boundaries, fixed AAA boundary interiors and the candidate set below, using ViennaRNA 2.7.2 with Turner 2004 parameters at 37 C.
Researchers studying RNA undesignability can use the upper-cover and lower-witness certificates to check these finite optima.

## First check

Requires Python 3.11 or later. From the repository root:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python -B tools/manifest.py
python -B tools/fetch_source.py
python -B checkers/verify.py
```

Expected: JSON with `"status": "PASS"`, 108 lower bounds and 3 upper cases covering 539,136 sequences. This is the smoke check; the complete check is described below.

## Instances and results

The instances are the 108 data rows with `N_Rival >= 2` in the 1,805-row `results.uniq.csv` of [RNA-Undesign](https://github.com/shanry/RNA-Undesign/tree/8a8de22). Row numbers count data rows from one, excluding the header. Users retrieve the pinned input separately with the fetcher below.

| Minimum rivals | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---:|---:|---:|---:|---:|---:|
| Instances | 10 | 31 | 40 | 19 | 6 | 2 |

The sum of the instance-specific minima is 310. The instance-specific candidate sets contain 12,235 candidates in total, and the sequence spaces contain 300,119,040 assignments. [data/results.csv](data/results.csv) lists all 108 row IDs, minima, candidate and sequence counts, and motif digests.

## Model and candidate set

The checker uses **ViennaRNA 2.7.2** and the Turner 2004 parameter set shipped with that version, loaded by `RNA.params_load_RNA_Turner2004()`. It sets temperature 37 C, `dangles=2`, `special_hp=1`, `noLP=0`, `noGU=0`, `noGUclosure=0`, `min_loop_size=3`, `circ=0`, `gquad=0`, `logML=0`, salt 1.021 M and `energy_set=0`; other settings are the ViennaRNA 2.7.2 defaults. It checks the installed version and all these values. Energies come from the integer `eval_structure_pt` API in units of 0.01 kcal/mol, with an exact integer comparison.

In motif notation, `(*)` is an indivisible boundary pair. For energy evaluation it becomes a three-A hairpin: the structure is `(...)` and the three internal sequence letters are fixed to `AAA`. Target pairs, including the outer and boundary pairs, allow AU, UA, GC, CG, GU or UG. Other unfixed unpaired positions allow A, C, G or U. With p target pairs and u unfixed unpaired positions, the sequence space X(m) has size 6^p 4^u.

For the candidate grammar, compress each boundary `(*)` to a single atomic `*`. Let t be the compressed target of length n. A candidate string s has the same length and satisfies four rules:

1. Positions 0 and n−1 are `(` and `)` paired with each other, preserving the outer pair.
2. The positions occupied by `*` are exactly those in t. Each `*` is an indivisible closed child; its three internal A letters exist only in the expanded coordinates used for energy evaluation.
3. The remaining symbols are `(`, `)` or `.`, forming a balanced, noncrossing bracket structure.
4. Every pair, including the outer pair, encloses at least one direct child or at least three directly enclosed `.` symbols. A direct child is a pair or a `*` immediately inside that loop.

R(m) consists of these strings other than t itself. New pairs may enclose boundaries, so their containment can change while the outer and boundary pairs remain fixed. A terminal hairpin therefore requires three unpaired letters in compressed coordinates. For example, the synthetic motif `(.(*)...)` compresses to `(.*...)` and has exactly three candidates: `((*)..)`, `((*.).)` and `((*..))`. Rule 4 excludes `(.*(.))`. The checker regenerates R(m) with a stack automaton and expands each `*` back to `(...)` with internal AAA for energy evaluation.

## Why the certificates establish each minimum

A rival r covers a sequence x when every pair of r is compatible with x and E(x,r) ≤ E(x,m). Ties count: the target then fails to be the unique minimum-free-energy structure. The reported minimum k*(m) is the least size of a subset C of R(m) such that every x in X(m) is covered by some r in C.

An upper certificate supplies k distinct rivals covering all of X(m). A lower certificate supplies a nonempty finite witness set W contained in X(m) that cannot be covered by at most k−1 candidates from R(m). The upper certificate gives k*(m) ≤ k; any cover of X(m) also covers W, so the lower certificate gives k*(m) ≥ k. For k=1, a nonempty sequence space excludes an empty cover.

For the lower check, the checker evaluates every candidate on W and represents its coverage by a bit mask. Starting with S₀={0}, it computes S_d = S_(d−1) ∪ {a OR c : a in S_(d−1), c a candidate mask}, retaining all earlier states. S_d therefore contains exactly the unions of at most d candidate masks. The lower bound holds when the full witness mask is absent from S_(k−1). Reusing a mask leaves a union unchanged. The witness sets contain one to six sequences.

For the upper check, the checker enumerates all 6^p 4^u compatible sequences and requires one of the supplied rivals to cover each sequence. Candidate sets are regenerated from the four rules; the certificates supply the upper rivals and lower witnesses.

## Run the checks

After the first check, run the five negative controls and check the stored complete-run record:

```sh
python -B checkers/negative_controls.py
python -B checkers/check_full_record.py
```

Both print JSON with `"status": "PASS"` and exit zero. The negative controls damage five inputs or certificates and pass only when each is rejected; details go to `work/checks/negative-controls.json`. The stored-record check confirms the 108 rows, 300,119,040 sequences and input hashes of the saved run. The distinction between checking a saved record and rerunning the calculation is described in Scope.

The input is [`data/motifs_maxlen14_no_external/results.uniq.csv`](https://raw.githubusercontent.com/shanry/RNA-Undesign/8a8de22/data/motifs_maxlen14_no_external/results.uniq.csv). The fetcher downloads this fixed `8a8de22` raw CSV into ignored `work/source/`, and stops unless its SHA-256 is `a06d6cc495c36c50b4292e260ebc89d54d3dbd422b99fd2ebfae66431ff59041`. To use an existing copy instead:

```sh
python -B tools/fetch_source.py --from-file work/source/results.uniq.csv
```

Substitute the path to your copy for `work/source/results.uniq.csv`. The checker verifies the CSV digest, each row's motif digest and the exact 108 selected row IDs. A motif digest hashes the exact decoded `Motif` field encoded as UTF-8, without stripping, normalization or an added newline. Stored rivals retain compressed `(*)` boundaries; lower witness sequences use the expanded coordinates with fixed AAA.

The default smoke check regenerates the candidate grammar and checks all candidate/sequence counts and **all 108 lower bounds**, then exhaustively checks upper coverage for m0081 (k=4), m0335 (k=2) and m1780 (k=1): 539,136 sequences. It took about 6 seconds on the assembly machine; timings vary. JSON results go to ignored `work/checks/`.

`tools/manifest.py` verifies the sizes and SHA-256 digests in [manifest.json](manifest.json). It prints `"status": "PASS"` and exits zero on success. The maintainer option `--update` regenerates the manifest after an intentional package change.

```sh
# Every upper cover, in addition to all lower bounds:
python -B checkers/verify.py --full --output work/checks/full.json
# Upper cover for a selected row; all lower bounds are still checked:
python -B checkers/verify.py --case m0025 --output work/checks/m0025.json
```

Expected: `"status": "PASS"` in both runs. The full run checks 108 lower bounds and 108 upper covers over 300,119,040 sequences; m0025 checks all 108 lower bounds and one upper cover over 5,308,416 sequences. A complete run took about 55 minutes in one process on the assembly machine (Apple silicon). The checker runs in one process, using the certificate grammar and ViennaRNA energy evaluator. A failure reports the row and, for a missed upper cover, a counterexample sequence. Optimized Python (`-O`) is refused. CI is configured for smoke, negative controls and the stored-record check.

## Files and verification

- [data/results.csv](data/results.csv): all 108 row IDs, counts, minima and motif digests.
- [data/certificates.json](data/certificates.json): laboratory-computed rivals and witness sequences with matching row IDs and digests. [data/README.md](data/README.md) explains the encodings.
- `checkers/`: candidate grammar, integer-energy adapter and certificate checks.
- [validation/full-check.json](validation/full-check.json) and [validation/full-check-meta.json](validation/full-check-meta.json): output and input hashes of a complete run of this checker. `checkers/check_full_record.py` checks their consistency with the supplied inputs.
- [SOURCE-PERMISSIONS.md](SOURCE-PERMISSIONS.md): source-data permission findings and the treatment of derived structural fragments.

A separately written certificate checker verified all 108 minima and all 300,119,040 sequences using ViennaRNA 2.7.2. The packaged checker shares its candidate grammar with the research implementation and uses the same thermodynamic backend. Verification methods, stored run records and dependencies are documented in [VERIFICATION-RECORD.md](VERIFICATION-RECORD.md).

## Scope

These are finite optima for the specified candidate and sequence spaces, fixed outer and boundary pairs, AAA boundary interiors and energy settings. They do not establish minima over unconstrained rivals or arbitrary RNA motifs, robustness to other boundary interiors or parameters, results for pseudoknots or experimental molecules, or priority. The sum 310 is not a count of distinct structures forming one cover for all motifs. Witness-set cardinalities and certificate byte sizes are not claimed to be minimum. The source CSV's rival counts are search outputs, not minimum-cardinality claims being corrected here; inclusion-minimal motifs and the minimum number of rivals for a fixed motif are different notions.

The smoke check does not recompute all upper covers. Checking a saved record's hashes does not establish that a run occurred or repeat that run; `--full` performs the calculation. Package runs are not a new blind independent review. The software and thermodynamic model are not formally verified, and this work has not undergone human peer review.

The original CSV and its motif strings are not redistributed. No redistribution grant was identified in the source repository during the permission review. This package's licenses do not grant rights in third-party source material.

## Authorship, source credit and licenses

Tatsuhiko Takimoto is responsible for this dataset and software. AI systems assisted with the calculations, certificate checks, literature comparison, code and writing. Research contact: [research@tatsuhikotakimoto.com](mailto:research@tatsuhikotakimoto.com).

The motif instances and rival-based undesignability framework come from Tianshuo Zhou, Wei Yu Tang, Apoorv Malik, David H. Mathews and Liang Huang's RNA-Undesign work: RIGENDE (RECOMB 2024, [arXiv:2311.08339](https://arxiv.org/abs/2311.08339)), FastMotif (RECOMB 2025, [arXiv:2402.17206](https://arxiv.org/abs/2402.17206)) and the [2026 journal account](https://doi.org/10.1177/15578666251398551). ViennaRNA provides the thermodynamic evaluator ([Lorenz et al., 2011](https://doi.org/10.1186/1748-7188-6-26); [Python distribution 2.7.2](https://pypi.org/project/ViennaRNA/2.7.2/)). I am grateful for their public instances, definitions and software.

The included row IDs, minima, rival structures, witness sequences, counts and motif digests are laboratory-computed results obtained by applying the stated procedure to the source instances. Laboratory-authored code is Apache-2.0; documentation and computed results are CC-BY-4.0 to the extent of the laboratory's rights. See [LICENSE](LICENSE) and `licenses/`. [CITATION.cff](CITATION.cff) supplies citation metadata for this dataset and its sources.
