import sys

def analyze():
    with open("server.log", "r") as f:
        lines = f.readlines()
        
    pkts_6b = []
    
    for line in lines:
        if "]" in line:
            data = line.split("]")[1].strip()
            parts = data.split()
            if len(parts) > 0 and parts[0] == "6b":
                pkts_6b.append([int(x, 16) for x in parts])
                
    if not pkts_6b:
        print("No 6b packets found")
        return
        
    print(f"Found {len(pkts_6b)} packets of type 6b")
    
    # Compare first packet with last packet
    first = pkts_6b[0]
    last = pkts_6b[-1]
    
    for i in range(min(len(first), len(last))):
        if first[i] != last[i]:
            # Print min, max, and unique values for this byte index
            vals = [p[i] for p in pkts_6b if i < len(p)]
            print(f"Byte {i}: changed from {first[i]} to {last[i]}. Min: {min(vals)}, Max: {max(vals)}, Uniques: {len(set(vals))}")

if __name__ == "__main__":
    analyze()
