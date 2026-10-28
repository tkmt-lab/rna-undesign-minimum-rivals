"""Fetch the source CSV into ignored work/, checking its exact SHA-256."""
import argparse,hashlib,json,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EXPECTED="a06d6cc495c36c50b4292e260ebc89d54d3dbd422b99fd2ebfae66431ff59041"
URL="https://raw.githubusercontent.com/shanry/RNA-Undesign/8a8de22/data/motifs_maxlen14_no_external/results.uniq.csv"
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument("--from-file",type=Path);args=ap.parse_args()
    data=args.from_file.read_bytes() if args.from_file else urllib.request.urlopen(URL,timeout=60).read()
    digest=hashlib.sha256(data).hexdigest()
    if digest!=EXPECTED: raise ValueError("source SHA-256 mismatch: "+digest)
    out=ROOT/"work/source/results.uniq.csv";out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
    print(json.dumps(dict(source=str(out.relative_to(ROOT)),sha256=digest,bytes=len(data))))
if __name__=="__main__":main()
