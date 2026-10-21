"""
deploy_pridi_bold_title.py
- สร้างแผนภาพฟอนต์ใหม่ด้วย Pridi-Bold (ขนาดใหญ่ 26-33px หนาพิเศษ คมชัด)
- ย้ายตัวอักษรและสระทั้งหมดลงในช่อง "คานะ (Kana)" 100% (ไม่มีคันจิหลุดมาแน่นอน)
- เขียนข้อความ 3 ปุ่มใน Entry 36 ของ LINKDATA.BIN
    Button 1: ぁふるぃの (เริ่มเล่น)
    Button 2: もぅらきるさは (สร้างเซฟ)
    Button 3: まぇるさは (ลบเซฟ)
- ปรับระยะห่างฟอนต์ ExeFS ให้ชิดสวยงาม (21.0f)
"""

import os
import sys
import struct
import shutil
import subprocess
import numpy as np
from PIL import Image, ImageFont, ImageDraw

BASE_DIR = r"D:\Game\dragon quest heroes i & ii"
SWITCH_DIR = os.path.join(BASE_DIR, "switch")
WORKSPACE_DIR = os.path.join(SWITCH_DIR, "workspace")
TEX_DIR = os.path.join(WORKSPACE_DIR, "tex_55")
OUT_G1T_DIR = os.path.join(WORKSPACE_DIR, "out_g1t")
G1T_TOOL = os.path.join(SWITCH_DIR, "tools", "g1t_tool.py")
FONT_TTF = os.path.join(SWITCH_DIR, "fonts", "Pridi-Bold.ttf")

CLEAN_DDS = os.path.join(WORKSPACE_DIR, "tex_clean_55", "clean_entry_00055.TEX0.dxt5.dds")
TARGET_DDS = os.path.join(TEX_DIR, "entry_00055.TEX0.dxt5.dds")

TITLE_ID = "0100CD3000BDC000"
BUILD_ID = "5C598E5025BF97BCEC69E67213B48503"

MOD_DIR = os.path.join(BASE_DIR, "mod", "atmosphere", "contents", TITLE_ID, "romfs", "dqh2")
MOD_BIN = os.path.join(MOD_DIR, "LINKDATA.BIN")

YUZU_IPS = os.path.expanduser(rf"~\AppData\Roaming\yuzu\load\{TITLE_ID}\MODTHAI\exefs\{BUILD_ID}.ips")
ATMOS_IPS = os.path.join(BASE_DIR, "mod", "atmosphere", "contents", TITLE_ID, "exefs", f"{BUILD_ID}.ips")

ENTRY_55_OFF = 4805120
ENTRY_55_ZSZ = 1106944
ENTRY_36_OFF = 363008
ENTRY_36_SZ  = 104012

WIDTH_BLOCKS = 4096 // 4  # 1024
BLOCK_BYTES = 16

sys.path.append(os.path.join(SWITCH_DIR, "tools"))
from build_thai_keyboard import encode_cell_dxt5, pack_entry_chunks

# ฟอนต์ Pridi-Bold ขนาดใหญ่
f_base = ImageFont.truetype(FONT_TTF, 44)
f_tall = ImageFont.truetype(FONT_TTF, 36)

def make_bold_glyph(text, is_tall=False):
    f = f_tall if is_tall else f_base
    canvas = Image.new('RGBA', (120, 80), (0, 0, 0, 0))
    d = ImageDraw.Draw(canvas)
    # วาดด้วย stroke_width=1 เพื่อเพิ่มความหนาตัน (Extra Bold) เข้ากับสไตล์เกม Dragon Quest
    d.text((20, 15), text, font=f, fill=(255, 255, 255, 255), stroke_width=1, stroke_fill=(255, 255, 255, 255))
    arr = np.array(canvas)[:, :, 3]
    coords = np.argwhere(arr > 10)
    if len(coords) == 0:
        return Image.new('RGBA', (36, 36), (0, 0, 0, 0))
    min_y, min_x = coords.min(axis=0)
    max_y, max_x = coords.max(axis=0)
    cr = canvas.crop((min_x, min_y, max_x + 1, max_y + 1))

    # ปรับสเกลความสูง: ตัวธรรมดา 26px, ตัวสูง 33px
    target_h = 33 if is_tall else 26
    scale = target_h / float(cr.height)
    nw = max(1, int(round(cr.width * scale)))
    nh = target_h
    cr = cr.resize((nw, nh), Image.Resampling.LANCZOS)

    cell = Image.new('RGBA', (36, 36), (0, 0, 0, 0))
    # จัดชิดล่าง baseline ที่ y=32
    cy = max(1, 32 - nh)
    # วางตรงกลางแนวนอนของเซลล์ 36x36
    cx = max(0, (36 - nw) // 2)
    cell.paste(cr, (cx, cy), cr)
    return cell

# รายการ 13 ตัวอักษรที่แมปลงช่อง "คานะ (Kana)" 100% ไม่มีคันจิปน!
KANA_MAPPING = [
    # (ชื่อไทย, คานะ, row, col, is_tall)
    ('เริ่', 'ぁ', 1,  96, True),   # 0x3041 (Small A)
    ('ล่',  'ぃ', 1,  98, True),   # 0x3043 (Small I)
    ('ร้',  'ぅ', 1, 100, True),   # 0x3045 (Small U)
    ('บ',   'ぇ', 1, 102, False),  # 0x3047 (Small E)
    ('ง',   'き', 1, 108, False),  # 0x304D (Ki)
    ('ซ',   'さ', 2,   3, False),  # 0x3055 (Sa)
    ('น',   'の', 2,  28, False),  # 0x306E (No)
    ('ฟ',   'は', 2,  29, True),   # 0x306F (Ha)
    ('ม',   'ふ', 2,  35, False),  # 0x3075 (Fu)
    ('ล',   'ま', 2,  44, False),  # 0x307E (Ma)
    ('ส',   'も', 2,  48, False),  # 0x3082 (Mo)
    ('า',   'ら', 2,  55, False),  # 0x3089 (Ra)
    ('เ',   'る', 2,  57, False),  # 0x308B (Ru)
]

def make_ips32(records):
    buf = bytearray(b"IPS32")
    for off, payload in records:
        buf.extend(struct.pack(">IH", off, len(payload)))
        buf.extend(payload)
    buf.extend(b"EEOF")
    return bytes(buf)

def main():
    print("=" * 70)
    print(" [1/4] สร้างภาพตัวอักษร Pridi-Bold (หนาพิเศษ 26-33px) ลงช่องคานะ...")
    print("=" * 70)
    shutil.copy2(CLEAN_DDS, TARGET_DDS)
    with open(TARGET_DDS, "rb") as f:
        dds_bytes = bytearray(f.read())

    for thai_name, kana_ch, row, col, is_tall in KANA_MAPPING:
        cell_img = make_bold_glyph(thai_name, is_tall)
        rows_dxt = encode_cell_dxt5(cell_img)
        bx0 = (col * 36) // 4
        by0 = (row * 36) // 4
        for by in range(9):
            offset = 128 + ((by0 + by) * WIDTH_BLOCKS + bx0) * BLOCK_BYTES
            dds_bytes[offset : offset + 144] = rows_dxt[by]
        cell_idx = row * 113 + col
        print(f"    [+] '{thai_name:4}' -> คานะ '{kana_ch}' (Row {row:2}, Col {col:3}, Cell {cell_idx:4}) [Pure Kana]")

    with open(TARGET_DDS, "wb") as f:
        f.write(dds_bytes)
    print("[+] บันทึก DDS สำเร็จ:", TARGET_DDS)

    print("\n" + "=" * 70)
    print(" [2/4] แปลง DDS เป็น G1T และฉีดเข้า Entry 55 ใน LINKDATA.BIN...")
    print("=" * 70)
    os.makedirs(OUT_G1T_DIR, exist_ok=True)
    cmd = [sys.executable, G1T_TOOL, "import", TEX_DIR, OUT_G1T_DIR]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0, f"g1t_tool import failed: {res.stderr}"

    out_g1t = os.path.join(OUT_G1T_DIR, "entry_00055.g1t")
    with open(out_g1t, "rb") as f:
        g1t_raw = f.read()

    packed = pack_entry_chunks(g1t_raw)
    pad = b'\x00' * (ENTRY_55_ZSZ - len(packed))
    payload = packed + pad
    assert len(payload) == ENTRY_55_ZSZ

    with open(MOD_BIN, "r+b") as f:
        f.seek(ENTRY_55_OFF)
        f.write(payload)
    print(f"[+] ฉีด Entry 55 เข้า RomFS บน Drive D: สำเร็จ ({MOD_BIN})")

    print("\n" + "=" * 70)
    print(" [3/4] เขียนข้อความ 3 ปุ่มเมนูลงใน Entry 36 (LINKDATA.BIN) ด้วยคานะ 100%...")
    print("=" * 70)
    with open(MOD_BIN, "rb") as f:
        f.seek(ENTRY_36_OFF)
        e36_data = bytearray(f.read(ENTRY_36_SZ))

    # Button 1: เริ่มเล่น -> ぁふるぃの (budget: 16 bytes)
    str1 = "ぁふるぃの".encode('utf-8') + b'\x00'
    assert len(str1) <= 16
    e36_data[86990 : 86990 + len(str1)] = str1
    for i in range(86990 + len(str1), 87006):
        e36_data[i] = 0

    # Button 2: สร้างเซฟ -> もぅらきるさは (budget: 25 bytes)
    str2 = "もぅらきるさは".encode('utf-8') + b'\x00'
    assert len(str2) <= 25
    e36_data[87006 : 87006 + len(str2)] = str2
    for i in range(87006 + len(str2), 87031):
        e36_data[i] = 0

    # Button 3: ลบเซฟ -> まぇるさは (budget: 22 bytes)
    str3 = "まぇるさは".encode('utf-8') + b'\x00'
    assert len(str3) <= 22
    e36_data[87031 : 87031 + len(str3)] = str3
    for i in range(87031 + len(str3), 87053):
        e36_data[i] = 0

    with open(MOD_BIN, "r+b") as f:
        f.seek(ENTRY_36_OFF)
        f.write(e36_data)
    print(f"[+] เขียน Entry 36 ลงใน LINKDATA.BIN สำเร็จ ({ENTRY_36_SZ} bytes)")
    print("    [+] Button 1 (86990): เริ่มเล่น -> ぁふるぃの (5 ตัวอักษรคานะ)")
    print("    [+] Button 2 (87006): สร้างเซฟ -> もぅらきるさは (7 ตัวอักษรคานะ)")
    print("    [+] Button 3 (87031): ลบเซฟ   -> まぇるさは (5 ตัวอักษรคานะ)")

    print("\n" + "=" * 70)
    print(" [4/4] ปรับระยะห่างฟอนต์ ExeFS ให้ชิดสวยงาม (21.0f)...")
    print("=" * 70)
    # opcode: mov w8, #0x41a80000 (21.0f) -> LE hex: 0835a852
    patch_21f = bytes.fromhex("0835a852")
    records = [
        (0x0001C728, patch_21f)
    ]
    ips_bytes = make_ips32(records)

    for target_ips in [YUZU_IPS, ATMOS_IPS]:
        os.makedirs(os.path.dirname(target_ips), exist_ok=True)
        with open(target_ips, "wb") as f:
            f.write(ips_bytes)
        print(f"[+] บันทึก IPS Patch -> {target_ips} ({len(ips_bytes)} bytes)")

    print("\n" + "=" * 70)
    print("[SUCCESS] ทุกขั้นตอนเสร็จสมบูรณ์ 100%! ไม่หลุดเป็นภาษาอื่นแน่นอน!")
    print("=" * 70)

if __name__ == "__main__":
    main()
