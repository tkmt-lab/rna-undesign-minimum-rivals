"""Finite motif grammar; adapted from the certificate-side research verifier."""
import itertools
from functools import lru_cache
PAIRS = ("UG", "GU", "CG", "GC", "UA", "AU")
ALPHABET = "UGCA"
def require(test, message):
    if not test: raise ValueError(message)
def tokens(motif):
    out=[]; i=0
    while i<len(motif):
        if motif[i:i+3]=="(*)": out.append("*"); i+=3
        else:
            require(motif[i] in "().", "invalid motif token")
            out.append(motif[i]); i+=1
    return "".join(out)
def expanded(t): return t.replace("*", "(...)")
@lru_cache(None)
def matching(db):
    stack=[]; pairs=[]
    for i,c in enumerate(db):
        if c=="(": stack.append(i)
        elif c==")":
            require(bool(stack), "unmatched closing pair")
            pairs.append((stack.pop(),i))
        else: require(c==".", "invalid dot-bracket symbol")
    require(not stack, "unmatched opening pair")
    return tuple(sorted(pairs, reverse=True))
def fixed_layout(motif):
    t=tokens(motif); db=expanded(t); pp=matching(db); fill=set(); offset=0
    for c in t:
        if c=="*": fill.update(range(offset+1,offset+4)); offset+=5
        else: offset+=1
    paired={i for pair in pp for i in pair}
    free=sorted(set(range(len(db)))-paired-fill, reverse=True)
    return db,pp,free,fill

def sequences(motif):
    db,pp,free,fill=fixed_layout(motif)
    for assignments in itertools.product(PAIRS,repeat=len(pp)):
        seq=["A"]*len(db)
        for (i,j),word in zip(pp,assignments): seq[i],seq[j]=word
        for assignment in itertools.product(ALPHABET,repeat=len(free)):
            for i,c in zip(free,assignment): seq[i]=c
            yield "".join(seq)

def valid_sequence(motif,sequence):
    db,pp,free,fill=fixed_layout(motif)
    return len(sequence)==len(db) and set(sequence)<=set("ACGU") and all(sequence[i]=="A" for i in fill) and all(sequence[i]+sequence[j] in PAIRS for i,j in pp)

def all_candidates(motif):
    """Stack automaton: boundary stars are indivisible closed children."""
    target=tokens(motif)
    require(target.startswith("(") and target.endswith(")"), "outer pair required")
    matching(expanded(target))
    inside=target[1:-1]; suffix=[0]*(len(inside)+1)
    for i in range(len(inside)-1,-1,-1): suffix[i]=suffix[i+1]+(inside[i]!="*")
    result=[]
    def valid(frame): return frame[0]>0 or frame[1]>=3
    def visit(pos,frames,body):
        if len(frames)-1>suffix[pos]: return
        if pos==len(inside):
            if len(frames)==1 and valid(frames[0]):
                s="("+body+")"
                if s!=target: result.append(s)
            return
        children,unpaired=frames[-1]
        if inside[pos]=="*":
            visit(pos+1,frames[:-1]+((children+1,unpaired),),body+"*"); return
        visit(pos+1,frames[:-1]+((children,unpaired+1),),body+".")
        visit(pos+1,frames+((0,0),),body+"(")
        if len(frames)>1 and valid(frames[-1]):
            parent=frames[-2]
            visit(pos+1,frames[:-2]+((parent[0]+1,parent[1]),),body+")")
    visit(0,((0,0),),"")
    require(len(result)==len(set(result)), "duplicate candidates")
    return sorted(result)
