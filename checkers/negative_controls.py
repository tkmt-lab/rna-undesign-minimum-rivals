"""Reject broken certificates and a damaged external input."""
import copy,hashlib,json,sys,time
from pathlib import Path
from verify import ROOT,Energy,load_cases,preflight,upper_check
from geometry import all_candidates,fixed_layout

def main():
    cases=load_cases(ROOT/"work/source/results.uniq.csv");backend=Energy();base=next(c for c in cases if c["id"]=="m0081");results=[]
    def reject(name,fn,needle):
        try:fn()
        except ValueError as exc:
            if needle not in str(exc):raise
            results.append(dict(name=name,result="REJECTED",reason=str(exc)));return
        raise ValueError("negative control unexpectedly passed: "+name)
    c=copy.deepcopy(base);c["claimed_minimum"]+=1;used={r.replace("(*)","*") for r in c["upper_rivals"]};extra=next(x for x in all_candidates(c["motif"]) if x not in used);c["upper_rivals"].append(extra.replace("*","(*)"));reject("inflated minimum with valid added rival",lambda:preflight(c,backend),"lower bound fails")
    c=copy.deepcopy(base);seq=list(c["lower_witnesses"][0]);fill=sorted(fixed_layout(c["motif"])[3]);seq[fill[0]]="C";c["lower_witnesses"][0]="".join(seq);reject("modified fixed AAA",lambda:preflight(c,backend),"invalid lower witness")
    c=copy.deepcopy(base);c["upper_rivals"][0]="."+c["upper_rivals"][0][1:-1]+".";reject("removed outer boundary pair",lambda:preflight(c,backend),"invalid upper rivals")
    c=copy.deepcopy(base);c["upper_rivals"]=c["upper_rivals"][:1];reject("insufficient actual upper cover",lambda:upper_check(c,backend),"upper bound fails")
    bad=ROOT/"work/checks/damaged-source.csv";bad.parent.mkdir(parents=True,exist_ok=True);bad.write_bytes((ROOT/"work/source/results.uniq.csv").read_bytes()+b"\n");reject("source SHA-256 mismatch",lambda:load_cases(bad),"source SHA-256 mismatch")
    out=ROOT/"work/checks/negative-controls.json";out.write_text(json.dumps(dict(status="PASS",controls=results),indent=2)+"\n");print(json.dumps(dict(status="PASS",negative_controls=len(results))))
if __name__=="__main__":main()
