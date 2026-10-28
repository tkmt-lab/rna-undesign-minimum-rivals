# Verification record

## Scope of the existing complete check

On 2026-10-23 an independent certificate checker, written without reading the research-side implementation or its results, checked all 108 source instances. It enumerated all 300,119,040 compatible sequences for upper coverage and regenerated every candidate and lower witness cover. All 108 minima passed. This was a certificate verification with the claimed optima and certificates known, not a blind rediscovery of the optima. It used the shared ViennaRNA 2.7.2 thermodynamic backend. The internal record is R004/r017-b-independent/report.md at research input commit 2ceb0de04c6cd68cfba7671a960bf35eef31e1e2.

The research-side checks additionally used ViennaRNA 2.5.1 and a separate Python energy evaluator. Shared model assumptions and parameter tables mean these are not three completely independent proofs. The software and its link to physical RNA are not formally verified.

## Package assembly

The package was assembled from claims-B/claims-108.json at the same research input commit. The motif field was removed; row number and SHA-256 were added. Counts, minimum sizes, upper rivals and lower sequences were preserved. The code adapts the research certificate-side grammar; it does not import search code. This assembly is not a new blind independent review.

The PyPI requirement is ViennaRNA==2.7.2, tested in CPython 3.11.14. An assembly smoke check passed every candidate/sequence count and all 108 lower bounds, plus three full upper covers (m0081, m0335, m1780; 539,136 sequences) in 6.0703 seconds. Five negative controls were rejected: inflated minimum with an added valid rival, changed fixed AAA, removed outer pair, an insufficient actual upper cover, and damaged source CSV. A complete new Python upper enumeration has not been run. Linear extrapolation from smoke suggests roughly an hour; the old independent all-instance run used a different implementation and took about 30 minutes with two workers.

The five-page report was rendered and visually inspected on every page before and after the minor revisions; the advisory writing scan reported no issues. A separate fresh-reader pass reviewed only the draft PDF/TeX, README and file list. Its overall verdict was MINOR, with no MAJOR issue; five documentation findings were addressed. The reviewer did not inspect data, certificates or code. No second reader pass was performed. No human peer review has taken place.

A fresh local clone of assembly commit 501339ade2ce7fc9f4fd17dcbcd5e485fc88214e installed only the pinned PyPI ViennaRNA package, fetched the fixed CSV from its raw URL and passed manifest, all 108 lower bounds, the three complete upper covers and all five negative controls. The smoke took 5.9250 seconds with maximum resident size 52,510,720 bytes. The final documentation receipt and refreshed manifest are checked again for delivery. The CI workflow is supplied but has not been run on GitHub: nothing has been pushed. The original CSV and Motif strings are excluded under the source-permission decision; derived rival fragments are listed in the internal audit. No remote repository, tag, DOI or publication has been created.

The original claims JSON was byte-identical to the input preserved for the earlier independent check. The package preserves each minimum, candidate/sequence count, upper rival and lower witness, removes the motif field, and adds its digest and row number. See data/provenance.json. An audit found no complete source motif string occurring in the 310 computed upper rivals, while boundary and structural fragments remain; these derived fields have been retained under the non-bundling decision.

CITATION.cff passes the official CFF 1.2.0 schema. The release payload is about 210 KB before Git metadata, below the 30 MB bound. Package-scientific fields match the prior independent input byte-for-byte except for removal of motif strings and addition of row numbers/digests; the energy model is explicitly checked against the fixed settings including energy_set=0. No optimized-Python result is accepted.
