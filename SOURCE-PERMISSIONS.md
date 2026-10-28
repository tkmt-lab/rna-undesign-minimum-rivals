# Source-data permissions

The source is shanry/RNA-Undesign, fixed input commit 8a8de22. Both that tree and the current e53130be6135caa85dc173bc5545708af149dd68 tree were inspected on 2026-10-28, together with their README files and GitHub repository metadata. No LICENSE/COPYING/COPYRIGHT file or explicit README redistribution terms were found; the repository API license field was null. This is an observation about available permission information, not a legal finding about the data.

The assembly decision is to exclude the original CSV and its Motif strings. Users obtain the pinned source separately and the checker verifies its exact SHA-256 before reconstructing motifs by row number. The mathematical report follows the same policy.

The package includes laboratory-computed row IDs, counts, minima, upper rival structures, lower witness sequences and motif digests. The rivals preserve boundary notation and may share structural substrings with the original motifs; witness sequences reflect their fixed boundaries. These derived fragments have not been represented as independently licensed by the source authors. No source author has endorsed or reviewed this work, and no external permission request was sent during assembly. The full-source and substring audit is recorded internally for the publication decision. Laboratory licensing applies only to rights the laboratory holds.
