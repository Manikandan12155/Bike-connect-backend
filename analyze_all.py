import json

def analyze():
    with open('server.log') as f:
        lines = f.readlines()
        
    pkts = []
    for l in lines:
        if '] 6b 05 ' in l:
            hex_str = l.split(']')[1].strip()
            parts = hex_str.split()
            pkts.append([int(x, 16) for x in parts])

    if not pkts:
        return
        
    p = pkts[0]
    
    for i in range(len(p)):
        vals = [x[i] for x in pkts if i < len(x)]
        vmin = min(vals)
        vmax = max(vals)
        if vmin != vmax:
            unique_vals = sorted(list(set(vals)))
            print(f"Byte {i}: min={vmin}, max={vmax}, uniques={len(unique_vals)}, values={unique_vals[:10]}")

if __name__ == "__main__":
    analyze()
