"""Check the stored complete --full run record against the current package files.
Reads validation/full-check.json and validation/full-check-meta.json; runs no energy evaluation."""
import csv,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def require(test,message):
    if not test: raise ValueError(message)
def sha(rel): return hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()
def main():
    record=json.loads((ROOT/"validation/full-check.json").read_text())
    meta=json.loads((ROOT/"validation/full-check-meta.json").read_text())
    for rel,digest in meta["inputs_sha256"].items(): require(sha(rel)==digest,"file changed since the full run: "+rel)
    require(record["status"]=="PASS" and record["mode"]=="full","record is not a passing full run")
    require(record["viennarna"]=="2.7.2","wrong ViennaRNA version in record")
    table={r["id"]:r for r in csv.DictReader((ROOT/"data/results.csv").open())}
    rows={r["id"]:r for r in record["results"]}
    require(len(record["results"])==108 and set(rows)==set(table),"record rows differ from results.csv")
    require(sorted(record["upper_cases_checked"])==sorted(table),"not every upper cover was checked")
    for i,r in rows.items():
        t=table[i]
        require(r["lower"]=="PASS" and r["upper"]=="PASS","row did not pass: "+i)
        require(r["minimum"]==int(t["minimum_rivals"]) and r["candidate_count"]==int(t["candidate_count"]),"row values differ: "+i)
        require(r["upper_sequences_checked"]==r["sequence_count"]==int(t["sequence_count"]),"sequence count differs: "+i)
    require(record["upper_sequences_checked"]==300119040,"wrong total sequences")
    print(json.dumps(dict(status="PASS",rows=108,upper_sequences_checked=record["upper_sequences_checked"],record_elapsed_seconds=round(record["elapsed_seconds"],1))))
if __name__=="__main__":
    try: main()
    except (ValueError,KeyError,FileNotFoundError) as exc: print("FAIL: "+str(exc),file=sys.stderr); sys.exit(1)
