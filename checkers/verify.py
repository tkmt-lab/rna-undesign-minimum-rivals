"""Verify minimum-rival certificates without importing search code.
Default: every row's grammar and lower bound, plus three full upper covers.
"""
import argparse,csv,hashlib,json,os,sys,time
from pathlib import Path
from geometry import (PAIRS,all_candidates,expanded,fixed_layout,matching,require,sequences,tokens,valid_sequence)
ROOT=Path(__file__).resolve().parents[1]
SOURCE_SHA256="a06d6cc495c36c50b4292e260ebc89d54d3dbd422b99fd2ebfae66431ff59041"
SMOKE_IDS=("m0081","m0335","m1780")
MODEL={"temperature":37.0,"dangles":2,"special_hp":1,"noLP":0,"noGU":0,"noGUclosure":0,"min_loop_size":3,"circ":0,"gquad":0,"logML":0,"salt":1.021,"energy_set":0}
def load_cases(source):
    data=source.read_bytes();require(hashlib.sha256(data).hexdigest()==SOURCE_SHA256,"source SHA-256 mismatch")
    rows=list(csv.DictReader(data.decode().splitlines()));require(len(rows)==1805,"wrong source row count")
    packet=json.loads((ROOT/"data/certificates.json").read_text());cases=packet["claims"]
    require(packet["schema"]=="rna-undesign-minimum-rivals.v0","wrong schema")
    require(packet["source"]["sha256"]==SOURCE_SHA256,"source metadata differs")
    require(packet["model"].get("backend")=="ViennaRNA" and packet["model"].get("version")=="2.7.2" and packet["model"].get("parameters")=="Turner 2004","energy backend metadata differs")
    require(all(packet["model"].get(k)==v for k,v in MODEL.items()),"energy model metadata differs")
    table=list(csv.DictReader((ROOT/"data/results.csv").open()))
    require(len(table)==108 and len({r["id"] for r in table})==108,"result table row count differs")
    table={r["id"]:r for r in table}
    fields={"source_data_row":"row_number","minimum_rivals":"claimed_minimum","candidate_count":"claimed_candidate_count","sequence_count":"claimed_sequence_count","motif_sha256":"motif_sha256"}
    for c in cases:
        require(c["id"] in table and all(table[c["id"]][a]==str(c[z]) for a,z in fields.items()),"CSV/JSON result mismatch")
    expected={i+1 for i,r in enumerate(rows) if int(r["N_Rival"])>=2}
    require(len(cases)==108 and len({c["row_number"] for c in cases})==108,"wrong or repeated rows")
    require({c["row_number"] for c in cases}==expected,"selected source rows differ")
    out=[]
    for c in cases:
        c=dict(c);n=c["row_number"];require(c["id"]==f"m{n:04d}","row ID mismatch")
        motif=rows[n-1]["Motif"];require(hashlib.sha256(motif.encode()).hexdigest()==c["motif_sha256"],"motif SHA-256 mismatch")
        c["motif"]=motif;out.append(c)
    require(sum(c["claimed_sequence_count"] for c in cases)==300119040,"wrong total sequence count")
    require(sum(c["claimed_minimum"] for c in cases)==310,"wrong sum of minima")
    return out
class Energy:
    def __init__(self):
        import RNA
        require(RNA.__version__=="2.7.2","requires ViennaRNA==2.7.2")
        RNA.params_load_RNA_Turner2004();self.RNA=RNA;self.md=RNA.md();self.tables={}
        for key,value in MODEL.items(): setattr(self.md,key,value)
        require(all(getattr(self.md,k)==v for k,v in MODEL.items()),"model settings differ")
    def prepare(self,seq): self.seq=seq;self.fc=self.RNA.fold_compound(seq,self.md,self.RNA.OPTION_EVAL_ONLY)
    def energy(self,db):
        if db not in self.tables:self.tables[db]=self.RNA.ptable(db)
        value=self.fc.eval_structure_pt(self.tables[db]);require(type(value) is int,"energy API must return integer")
        return value
    def compatible(self,db): return all(self.seq[i]+self.seq[j] in PAIRS for i,j in matching(db))
    def covered(self,db,baseline): return self.compatible(db) and self.energy(db)<=baseline

def preflight(case,backend):
    motif=case["motif"];k=case["claimed_minimum"]
    require(type(k) is int and 1<=k<=6,"invalid minimum")
    target,pp,free,fill=fixed_layout(motif);candidates=all_candidates(motif)
    require(len(candidates)==case["claimed_candidate_count"],"candidate count mismatch")
    require(6**len(pp)*4**len(free)==case["claimed_sequence_count"],"sequence count mismatch")
    upper=[tokens(s) for s in case["upper_rivals"]]
    require(len(upper)==k and len(set(upper))==k and all(s in candidates for s in upper),"invalid upper rivals")
    witnesses=case["lower_witnesses"]
    require(bool(witnesses) and len(set(witnesses))==len(witnesses),"empty/repeated witnesses")
    require(all(valid_sequence(motif,w) for w in witnesses),"invalid lower witness")
    masks=[0]*len(candidates)
    for i,w in enumerate(witnesses):
        backend.prepare(w);baseline=backend.energy(target)
        require(any(backend.covered(expanded(r),baseline) for r in upper),"upper rivals miss a lower witness")
        for j,r in enumerate(candidates):
            if backend.covered(expanded(r),baseline):masks[j]|=1<<i
    full=(1<<len(witnesses))-1;reachable={0}
    # Reusing a rival does not change its union: this covers all subsets of <=k-1.
    for depth in range(1,k):
        reachable|={state|mask for state in reachable for mask in masks}
        require(full not in reachable,"lower bound fails at size "+str(depth))
    return dict(id=case["id"],candidate_count=len(candidates),sequence_count=case["claimed_sequence_count"],minimum=k,witness_count=len(witnesses),lower="PASS",upper="NOT_RUN")
def upper_check(case,backend):
    target=fixed_layout(case["motif"])[0];upper=[expanded(tokens(s)) for s in case["upper_rivals"]];count=0
    for seq in sequences(case["motif"]):
        backend.prepare(seq);baseline=backend.energy(target)
        require(any(backend.covered(r,baseline) for r in upper),"upper bound fails for "+case["id"]+" sequence "+seq)
        count+=1
    require(count==case["claimed_sequence_count"],"enumerated count mismatch")
    return count

def run(args):
    require(sys.flags.optimize==0,"optimized Python is refused")
    try:os.nice(10)
    except (AttributeError,PermissionError):pass
    start=time.monotonic();cases=load_cases(args.source);backend=Energy();selected=set(args.case or ([] if args.full else SMOKE_IDS))
    if args.full:selected={c["id"] for c in cases}
    require(selected<={c["id"] for c in cases},"unknown case ID")
    result=[];total=0
    for c in cases:
        row=preflight(c,backend)
        if c["id"] in selected:row["upper"]="PASS";row["upper_sequences_checked"]=upper_check(c,backend);total+=row["upper_sequences_checked"]
        result.append(row)
    output=dict(status="PASS",mode="full" if args.full else "smoke" if not args.case else "selected",viennarna="2.7.2",model=MODEL,energy_units="integer 0.01 kcal/mol",rows=108,lower_bounds_checked=108,upper_cases_checked=sorted(selected),upper_sequences_checked=total,elapsed_seconds=time.monotonic()-start,results=result)
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(output,indent=2)+"\n")
    print(json.dumps({k:v for k,v in output.items() if k!="results"}))
    return output
if __name__=="__main__":
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument("--source",type=Path,default=ROOT/"work/source/results.uniq.csv");ap.add_argument("--full",action="store_true");ap.add_argument("--case",action="append");ap.add_argument("--output",type=Path,default=ROOT/"work/checks/latest.json");args=ap.parse_args()
    try:run(args)
    except (ValueError,FileNotFoundError,ImportError) as exc:print("FAIL: "+str(exc),file=sys.stderr);sys.exit(1)
