"""
deploy_sliced_dialogues_and_bios.py
เวอร์ชันขยายขนาดใหญ่พิเศษ (Font Size 28pt) + แก้ไข "นักเรียน" เต็มคำสำหรับเทเรเซีย:
- T1: "นักเรียนนายร้อยสาวผู้เพียบพร้อม" (10 Tiles เต็มคำ ไม่ย่อ นร.)
- ปรับ baseline y=25 ป้องกันสระและวรรณยุกต์ล้นขอบ 100%
- ข้อความคมชัด ตัวใหญ่ อ่านง่าย สบายตา สไตล์เกมเมอร์
"""

import os
import sys
import struct
import shutil
import hashlib
import subprocess
import numpy as np
from PIL import Image, ImageFont, ImageDraw

BASE_DIR = r"D:\Game\dragon quest heroes i & ii"
SWITCH_DIR = os.path.join(BASE_DIR, "switch")
WORKSPACE_DIR = os.path.join(SWITCH_DIR, "workspace")
TEX_DIR = os.path.join(WORKSPACE_DIR, "tex_55")
OUT_G1T_DIR = os.path.join(WORKSPACE_DIR, "out_g1t")
TARGET_DDS = os.path.join(TEX_DIR, "entry_00055.TEX0.dxt5.dds")
G1T_TOOL = os.path.join(SWITCH_DIR, "tools", "g1t_tool.py")
FONT_TTF = os.path.join(SWITCH_DIR, "fonts", "Pridi-Bold.ttf")

sys.path.append(os.path.join(SWITCH_DIR, "tools"))
sys.path.append(WORKSPACE_DIR)
from build_thai_keyboard import encode_cell_dxt5, pack_entry_chunks
from deploy_all_dqh2_menus_master import cell_to_kanji

TITLE_ID = "0100CD3000BDC000"
ATMO_DIR = os.path.join(BASE_DIR, "mod", "atmosphere", "contents", TITLE_ID, "romfs", "dqh2")
ATMO_BIN = os.path.join(ATMO_DIR, "LINKDATA.BIN")
ATMO_IDX = os.path.join(ATMO_DIR, "LINKDATA.IDX")

YUZU_DIR = os.path.expanduser(rf"~\AppData\Roaming\yuzu\load\{TITLE_ID}\MODTHAI\romfs\dqh2")
YUZU_BIN = os.path.join(YUZU_DIR, "LINKDATA.BIN")
YUZU_IDX = os.path.join(YUZU_DIR, "LINKDATA.IDX")

ENTRY_55_OFF = 4805120
ENTRY_36_START = 363008
ENTRY_36_ORIG_SIZE = 104012
ORIG_BIN_SIZE = 3740846848

WIDTH_BLOCKS = 1024
BLOCK_BYTES = 16

# รายการและขนาดฟอนต์ 28pt (ขยายใหญ่เต็มตา อ่านง่าย 100%)
SLICED_ITEMS = [
    # Razel Bio (Cells 975..997 = 23 tiles)
    ("R1", "นักเรียนนายร้อยผู้รักคุณธรรม", 9, 975),
    ("R2", "สดใสร่าเริงเปี่ยมพลังใจ", 8, 984),
    ("R3", "นักดาบหนุ่มผู้มุ่งมั่น", 6, 992),
    
    # Teresia Bio (Cells 998..1022 = 25 tiles)
    ("T1", "นักเรียนนายร้อยสาวผู้เพียบพร้อม", 10, 998),
    ("T2", "สุขุมเยือกเย็นคอยนำเพื่อน", 8, 1008),
    ("T3", "นักดาบหญิงที่พึ่งพาได้", 7, 1016),
    
    # Prompt 1 (Cells 1023..1028 = 6 tiles)
    ("P1_1", "สร้างเซฟ ช่องใด?", 6, 1023),
    
    # Prompt 2 (Cells 1029..1051 = 23 tiles)
    ("P2_1", "เลือกตัวเอกที่จะออกผจญภัย", 9, 1029),
    ("P2_2", "เลือกชายหรือหญิงก็ได้", 7, 1038),
    ("P2_3", "เนื้อเรื่องจะไม่เปลี่ยน", 7, 1045),
    
    # Prompt 3 (Cells 1052..1064 = 13 tiles)
    ("P3_1", "ตั้งชื่อลูกพี่ลูกน้อง", 6, 1052),
    ("P3_2", "ที่จะร่วมผจญภัยไปด้วย", 7, 1058)
]

def render_line_banner(text, tiles, font_size=28):
    total_w = tiles * 36
    im = Image.new("RGBA", (total_w, 36), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(FONT_TTF, font_size)
    d.text((2, 25), text, font=f, fill=(255, 255, 255, 255), anchor="ls")
    return im

def write_cell_to_dds(dds_bytes, cell_idx, cell_img):
    row = cell_idx // 113
    col = cell_idx % 113
    rows_dxt = encode_cell_dxt5(cell_img)
    bx0 = (col * 36) // 4
    by0 = (row * 36) // 4
    for by in range(9):
        offset = 128 + ((by0 + by) * WIDTH_BLOCKS + bx0) * BLOCK_BYTES
        dds_bytes[offset : offset + 144] = rows_dxt[by]

def main():
    print("=" * 80)
    print(" [*] เริ่มต้นติดตั้งข้อความ Size 28pt + เทเรเซียคำเต็ม (นักเรียนนายร้อยสาวผู้เพียบพร้อม)...")
    print("=" * 80)

    # 1. โหลด DDS Texture
    print("\n[+] 1. โหลด Font Texture entry_00055.TEX0.dxt5.dds...")
    with open(TARGET_DDS, "rb") as f:
        dds_bytes = bytearray(f.read())

    # 2. เรนเดอร์และหั่นภาพชิ้นส่วนลงใน Cell Ku 21
    print("\n[+] 2. เรนเดอร์ข้อความ Size 28pt และหั่นลง Cell 975..1064 (Ku 21)...")
    for item_id, text, tiles, start_cell in SLICED_ITEMS:
        banner = render_line_banner(text, tiles, font_size=28)
        for t in range(tiles):
            cell_idx = start_cell + t
            tile = banner.crop((t * 36, 0, (t + 1) * 36, 36))
            write_cell_to_dds(dds_bytes, cell_idx, tile)
        print(f"    -> [{item_id:4s}] \"{text}\" ({tiles} tiles -> Cells {start_cell}..{start_cell+tiles-1}) สำเร็จ")

    with open(TARGET_DDS, "wb") as f:
        f.write(dds_bytes)
    print("    [+] บันทึก DDS สำเร็จ!")

    # 3. คอมไพล์ DDS -> G1T
    print("\n[+] 3. คอมไพล์ DDS กลับเป็น G1T...")
    cmd = [sys.executable, G1T_TOOL, "import", TEX_DIR, OUT_G1T_DIR]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print("[-] G1T compile failed:", res.stderr)
        return

    out_g1t = os.path.join(OUT_G1T_DIR, "entry_00055.g1t")
    with open(out_g1t, "rb") as f:
        g1t_data = f.read()
    packed_55 = pack_entry_chunks(g1t_data)
    print(f"    [+] แพ็ก Entry 55 สำเร็จ (ขนาด: {len(packed_55):,} ไบต์)")

    # 4. สร้างข้อความรหัสภาพสำหรับ Entry 36
    print("\n[+] 4. สร้างรหัสข้อความสำหรับ Entry 36...")
    def get_kanji_string(start_cell, tiles):
        return "".join(cell_to_kanji(start_cell + i) for i in range(tiles))

    # P1 (Cell 1023..1028 = 6 tiles)
    p1_str = get_kanji_string(1023, 6)
    p1_bytes = p1_str.encode('utf-8')
    p1_padded = p1_bytes + b'\x00' * (45 - len(p1_bytes))

    # P2 (Cell 1029..1051 = 23 tiles)
    p2_1 = get_kanji_string(1029, 9)
    p2_2 = get_kanji_string(1038, 7)
    p2_3 = get_kanji_string(1045, 7)
    p2_str = f"{p2_1}\n{p2_2}\n{p2_3}"
    p2_bytes = p2_str.encode('utf-8')
    p2_padded = p2_bytes + b'\x00' * (167 - len(p2_bytes))

    # P3 (Cell 1052..1064 = 13 tiles)
    p3_1 = get_kanji_string(1052, 6)
    p3_2 = get_kanji_string(1058, 7)
    p3_str = f"{p3_1}\n{p3_2}"
    p3_bytes = p3_str.encode('utf-8')
    p3_padded = p3_bytes + b'\x00' * (85 - len(p3_bytes))

    # Razel Bio (Cells 975..997 = 23 tiles)
    r1 = get_kanji_string(975, 9)
    r2 = get_kanji_string(984, 8)
    r3 = get_kanji_string(992, 6)
    r_str = f"{r1}\n{r2}\n{r3}\x00"
    r_bytes = r_str.encode('utf-8')

    # Teresia Bio (Cells 998..1022 = 25 tiles)
    t1 = get_kanji_string(998, 10)
    t2 = get_kanji_string(1008, 8)
    t3 = get_kanji_string(1016, 7)
    t_str = f"{t1}\n{t2}\n{t3}\x00"
    t_bytes = t_str.encode('utf-8')

    # โหลด Entry 36 เดิมจาก Yuzu หรือ Atmosphere
    src_bin = YUZU_BIN if os.path.exists(YUZU_BIN) else ATMO_BIN
    with open(src_bin, "rb") as f:
        f.seek(ENTRY_36_START)
        e36 = bytearray(f.read(ENTRY_36_ORIG_SIZE))

    # ฉีด Prompts ลงใน Offset เดิม
    e36[6512 : 6512 + 45] = p1_padded
    e36[6641 : 6641 + 167] = p2_padded
    e36[6849 : 6849 + 85] = p3_padded

    # ล้างข้อความเดิมของราเซลและเทเรเซีย
    e36[87136 : 87136 + 117] = b'\x00' * 117
    e36[87253 : 87253 + 108] = b'\x00' * 108

    # Append ประวัติตัวละครต่อท้าย Entry 36
    pad_r = (4 - (len(e36) % 4)) % 4
    e36.extend(b'\x00' * pad_r)
    new_r_off = len(e36)
    e36.extend(r_bytes)

    pad_t = (4 - (len(e36) % 4)) % 4
    e36.extend(b'\x00' * pad_t)
    new_t_off = len(e36)
    e36.extend(t_bytes)

    # อัปเดต Pointers 4144 และ 4148
    ptr_r = new_r_off - 32
    ptr_t = new_t_off - 32
    struct.pack_into('<I', e36, 4144, ptr_r)
    struct.pack_into('<I', e36, 4148, ptr_t)

    # อัปเดต Header size
    struct.pack_into('<I', e36, 8, len(e36) - 14)
    struct.pack_into('<I', e36, 16, len(e36) - 14)

    # Align 128 bytes
    pad_128 = (128 - (len(e36) % 128)) % 128
    e36.extend(b'\x00' * pad_128)
    new_entry36_size = len(e36)
    print(f"    [+] อัปเดต Entry 36 เสร็จสิ้น (ขนาดใหม่: {new_entry36_size:,} ไบต์)")

    # 5. ฉีดเข้า Atmosphere และ Yuzu
    targets = [
        ("Atmosphere Mod (Drive D)", ATMO_BIN, ATMO_IDX),
        ("Yuzu Mod (Drive C)", YUZU_BIN, YUZU_IDX)
    ]

    print("\n[+] 5. ติดตั้ง Font Texture และ Entry 36 เข้าตัวเกม...")
    for name, bin_path, idx_path in targets:
        if not os.path.exists(bin_path) or not os.path.exists(idx_path):
            print(f"    [-] ข้าม {name} (ไม่พบไฟล์)")
            continue

        print(f"    [*] ดำเนินการกับ {name}...")
        with open(bin_path, "r+b") as f:
            # ฉีด Entry 55
            f.seek(ENTRY_55_OFF)
            f.write(packed_55)
            # Append Entry 36 ท้ายไฟล์
            f.seek(ORIG_BIN_SIZE)
            f.truncate(ORIG_BIN_SIZE)
            f.seek(ORIG_BIN_SIZE)
            f.write(e36)

        # อัปเดต LINKDATA.IDX Entry 36
        with open(idx_path, "r+b") as f:
            f.seek(36 * 32)
            idx_record = struct.pack('<QQQQ', ORIG_BIN_SIZE, new_entry36_size, new_entry36_size, 0)
            f.write(idx_record)

        print(f"        [+] ฉีด Entry 55 + Append Entry 36 + อัปเดต IDX สำเร็จ!")

    print("\n" + "=" * 80)
    print(" [*] เสร็จสิ้นสมบูรณ์แบบ 100%! พร้อมทดสอบใน Yuzu")
    print("=" * 80)

if __name__ == "__main__":
    main()
