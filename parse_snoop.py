import struct

def parse_btsnoop(file_path):
    with open(file_path, 'rb') as f:
        data = f.read()

    if not data.startswith(b'btsnoop\0'):
        print("Decompressed data is not a valid btsnoop file.")
        return

    datalink = struct.unpack(">I", data[12:16])[0]
    
    offset = 16
    packet_count = 0
    writes = []

    while offset < len(data):
        if offset + 24 > len(data):
            break
        
        orig_len, inc_len, flags, drops, time_hi, time_lo = struct.unpack(">IIIIII", data[offset:offset+24])
        offset += 24
        
        packet_data = data[offset:offset+inc_len]
        offset += inc_len
        packet_count += 1
        
        # If datalink is Linux Monitor (1002), skip 4 bytes
        if datalink == 1002 and len(packet_data) > 4:
            adapter, opcode = struct.unpack("<HH", packet_data[0:4])
            packet_data = packet_data[4:]
        
        # flags bit 0 = 0 means Sent from host to controller.
        # But wait, in Linux monitor, the direction is also indicated by opcode.
        # opcode 0 or 2 means sent.
        if (flags & 1) == 0:
            if len(packet_data) > 0 and packet_data[0] == 0x02: # ACL Data
                if len(packet_data) > 9:
                    acl_len = struct.unpack("<H", packet_data[3:5])[0]
                    l2cap_len, l2cap_cid = struct.unpack("<HH", packet_data[5:9])
                    if l2cap_cid == 0x0004 and len(packet_data) >= 9 + l2cap_len: # ATT protocol
                        att_data = packet_data[9:9+l2cap_len]
                        if len(att_data) > 0:
                            opcode = att_data[0]
                            if opcode in [0x12, 0x52]: # Write Req, Write Cmd
                                handle = struct.unpack("<H", att_data[1:3])[0]
                                value = att_data[3:]
                                hex_val = ' '.join(f'{b:02x}' for b in value)
                                print(f"Packet {packet_count}: ATT Write (Opcode 0x{opcode:02x}) Handle: 0x{handle:04x}, Value: {hex_val}")

    print(f"Total packets processed: {packet_count}")

if __name__ == "__main__":
    file_path = r"D:\file\bugreport-scout_g_sys-W1VCS36H.14-20-19-7-2026-09-28-11-21-49\FS\data\misc\bluetooth\logs\btsnoop_hci.log"
    parse_btsnoop(file_path)
