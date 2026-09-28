import binascii

def extract_att_writes(file_path):
    with open(file_path, 'rb') as f:
        data = f.read()

    print(f"File size: {len(data)} bytes")
    
    # We look for L2CAP ATT Write Request (0x12) or Write Command (0x52)
    # The L2CAP CID for ATT is 0x0004, which is stored little-endian as \x04\x00.
    # The preceding two bytes are L2CAP length.
    # So the pattern is: [len_lo] [len_hi] \x04 \x00 \x12 [handle_lo] [handle_hi] [payload...]
    # OR                 [len_lo] [len_hi] \x04 \x00 \x52 [handle_lo] [handle_hi] [payload...]
    
    writes = set()
    
    # Search for \x04\x00\x12 or \x04\x00\x52
    for i in range(2, len(data) - 10):
        if data[i:i+2] == b'\x04\x00':
            opcode = data[i+2]
            if opcode in [0x12, 0x52]:
                # Extract L2CAP length
                l2cap_len = data[i-2] + (data[i-1] << 8)
                
                # Check if length makes sense (at least 3 bytes for opcode + handle, max 512 bytes)
                if 3 <= l2cap_len <= 512 and i + 2 + l2cap_len <= len(data):
                    handle_lo = data[i+3]
                    handle_hi = data[i+4]
                    handle = handle_lo + (handle_hi << 8)
                    
                    payload_len = l2cap_len - 3
                    if payload_len > 0:
                        payload = data[i+5 : i+5+payload_len]
                        hex_payload = binascii.hexlify(payload).decode('ascii').upper()
                        
                        # Add to set to avoid duplicates
                        writes.add((opcode, handle, hex_payload))

    print(f"Found {len(writes)} unique ATT writes:")
    for w in sorted(writes):
        op_str = "Write Req" if w[0] == 0x12 else "Write Cmd"
        print(f"[{op_str}] Handle: 0x{w[1]:04X} -> Payload: {w[2]}")

if __name__ == "__main__":
    file_path = r"D:\file\bugreport-scout_g_sys-W1VCS36H.14-20-19-7-2026-09-28-11-21-49\FS\data\misc\bluetooth\logs\btsnoop_hci.log"
    extract_att_writes(file_path)
