#!/usr/bin/env python

# OFFSET = 0x3
BLOCK_LENGTH = 0x14
FIRST_BLOCK_ADDR = 0x1124b
ELF_BASE_ADDR = 0x10000


# def parse_line(line: str):
#     (lnb, code) = line.split(":", 1)
#     addr = OFFSET + (int(lnb) - 1) * BLOCK_LENGTH
#     next = bytearray.fromhex(code.strip()[-4 * 2:])
#     return addr, addr + int.from_bytes(next, 'little') + BLOCK_LENGTH

def find_addresses(blob, b):
    addresses = []
    needle = bytearray.fromhex(b)
    a = blob.find(needle)
    while a != -1:
        addresses.append(a - 5)
        a = blob.find(needle,a+1)
    return addresses

def find_next_addr(blob, curr_addr):
    jmp_bytes = blob[curr_addr + BLOCK_LENGTH - 4:curr_addr + BLOCK_LENGTH]
    jmp_int = int.from_bytes(jmp_bytes, 'little')
    return curr_addr + BLOCK_LENGTH + jmp_int


if __name__ == "__main__":

    # Search strings to search for all block loading "H" or "V".
    # These strings of bytes were identified using Ghidra.
    load_h_bytes = "4983f90075fac6034843e9"
    load_v_bytes = "4983f90075fac6035643e9"

    with open("padawanlock", "rb") as pfd:
        blob = pfd.read()

    h_loading = find_addresses(blob, load_h_bytes)
    v_loading = find_addresses(blob, load_v_bytes)

    # Create a map <next_addr> -> <current_addr> for all blocks loading "H"
    h_references = {find_next_addr(blob, addr): addr for addr in h_loading}

    # Find all blocks loading "H" that are followed by a block loading "V"
    v_refs = set(h_references.keys()).intersection(set(v_loading))
    h_addrs = [h_references[x] for x in v_refs]

    # Compute the inverse calculation of `PIN * 0x14 + 0x1124b`
    print([int((x - (FIRST_BLOCK_ADDR - ELF_BASE_ADDR)) / BLOCK_LENGTH) for x in h_addrs])

    ### xxd based solution:
    # with open("H_search.txt", "r") as hfd:
    #     h_map = {x[1]: x[0] for x in [parse_line(l) for l in hfd.readlines()]}
    #
    # with open("V_search.txt", "r") as vfd:
    #     v_addr = [parse_line(l)[0] for l in vfd.readlines()]
    #
    #
    # res = [(h_map[x] - (JUMP - BASE_ADDR))/0x14 for x in set(h_map.keys()).intersection(set(v_addr))]
    # print(res)
