# Barrido natural por entradas de mazmorra con guard.exe. Uso: python scripts/guards_win_fuzz.py 0,1,2 1 3  (entradas, semillas, procesos)
import random, re, subprocess, sys, json, time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
ROOT = Path(__file__).resolve().parent.parent
W = ROOT/"out"/"guards-win"; EXE = W/"guard.exe"; ROM = ROOT/"roms"/"alttp_usa.sfc"
LOW = 0x00004000  # BELOW_NORMAL_PRIORITY_CLASS
inputs = ["START@1100-1110","A@1300-1305","A@1500-1504","DOWN@1540-1542","DOWN@1560-1562","DOWN@1580-1582",
          "RIGHT@1600-1602","RIGHT@1620-1622","A@1640-1643","A@2000-2004"]+[f"A@{f}-{f+3}" for f in range(2100,5200,50)]
base = [str(EXE), str(ROM), "--frames", "5400", "--frame-blocks", "20000"]
for p in inputs: base += ["--press", p]
state = W/"base.sst"
if not state.exists():
    subprocess.run(base+["--state-save", f"{state}@5300"], capture_output=True, text=True, check=True, creationflags=LOW)
OPTS = ["fix_door_submodule","fix_stair_tags","fix_skullwoods_door","fix_camera_twice"]
def script(seed, frames=1500):
    rnd = random.Random(seed); out=[]; f=5600; end=5600+frames
    while f < end:
        d = rnd.choice(["UP","UP","DOWN","LEFT","RIGHT","UP","A","B","Y"]); n = rnd.randint(20,120)
        out.append(f"{d}@{f}-{f+n}"); f += n + rnd.randint(0,10)
    return out
def run(job):
    ent, seed, opt = job
    d = W/f"fz_{ent:02X}_{seed}_{opt}"; d.mkdir(exist_ok=True)
    cmd=[str(EXE), str(ROM), "--frames", "7200", "--frame-blocks", "20000", "--state-load", f"{state}@5300",
         "--poke", f"0010E={ent:02X}@5310","--poke","0010F=00@5310","--poke","00010=06@5310","--poke","00011=00@5310","--poke","000B0=00@5310"]
    for p in script(seed): cmd += ["--press", p]
    for o in OPTS: cmd += ["--game-opt", f"{o}={opt}"]
    cmd += ["--dump", str(d)]
    pr = subprocess.run(cmd, capture_output=True, text=True, timeout=600, creationflags=LOW)
    c = {n:[int(a),int(b)] for n,a,b in re.findall(r'^GUARD (\w+) (\d+) (\d+)$', pr.stdout, re.M)}
    wram = (d/"wram.bin").read_bytes() if (d/"wram.bin").exists() else b""
    return ent, seed, opt, pr.returncode, c, wram
if __name__ == "__main__":
    ents = [int(x,0) for x in sys.argv[1].split(",")]; seeds = [int(x) for x in sys.argv[2].split(",")]
    workers = int(sys.argv[3]) if len(sys.argv)>3 else 3
    jobs = [(e,s,o) for e in ents for s in seeds for o in (1,0)]
    t=time.time(); res={}
    with ThreadPoolExecutor(workers) as ex:
        for ent,seed,opt,rc,c,wram in ex.map(run, jobs): res[(ent,seed,opt)]=(rc,c,wram)
    summ=[]
    for e in ents:
        for s in seeds:
            a,b=res[(e,s,1)],res[(e,s,0)]
            corr={n:v[1] for n,v in a[1].items() if v[1]}
            summ.append(dict(entrance=e,seed=s,rc=(a[0],b[0]),same=(a[2]==b[2]),corrections=corr,
                             diff=[i for i in range(min(len(a[2]),len(b[2]))) if a[2][i]!=b[2][i]][:8]))
    for r in summ: print(json.dumps(r))
    print("tiempo", round(time.time()-t))
