"""Create or verify the file-integrity manifest; excludes local runtime files."""
import argparse,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def inventory():
    out={}
    for p in sorted(ROOT.rglob("*")):
        rel=p.relative_to(ROOT)
        if any(x in {".git",".venv","work","__pycache__"} for x in rel.parts) or p.name=="manifest.json" or p.suffix==".pyc":continue
        if p.is_file():
            if p.is_symlink():raise ValueError("symlinks not allowed: "+str(rel))
            data=p.read_bytes();out[rel.as_posix()]=dict(bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
    return out
if __name__=="__main__":
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument("--update",action="store_true");args=ap.parse_args();actual=inventory();path=ROOT/"manifest.json"
    if args.update:path.write_text(json.dumps(dict(schema="sha256-files-v1",files=actual),indent=2)+"\n")
    else:
        expected=json.loads(path.read_text())["files"]
        if actual!=expected:raise SystemExit("FAIL: files differ from manifest")
    size=sum(x["bytes"] for x in actual.values())
    if size>30_000_000:raise SystemExit("FAIL: package exceeds 30 MB")
    print(json.dumps(dict(status="PASS",files=len(actual),bytes=size,updated=args.update)))
