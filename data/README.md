# Laboratory results

The JSON and CSV contain computed results for 108 data rows of the pinned RNA-Undesign CSV. They contain row identifiers, counts, minimum cover sizes, upper rival structures, lower witness sequences and SHA-256 digests of the source motif strings. The original CSV and its Motif strings are not included. Each row number is one-based, excluding the CSV header.

The upper structures and lower sequences were computed from the source motifs. They retain boundary notation and structural fragments derived from those motifs. This package does not grant a license to the source data. See SOURCE-PERMISSIONS.md.

## Encodings

The motif hash is SHA-256 of the decoded CSV `Motif` field encoded as UTF-8, with no stripping, normalization or added newline. Upper rivals use the original compressed motif coordinates and `(*)` notation. Lower witness sequences are full expanded A/C/G/U strings; the internal three letters of each expanded boundary hairpin are fixed AAA. The checker expands rival boundaries to `(...)` before evaluating energies against these full sequences.
