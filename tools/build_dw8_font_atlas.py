"""
build_dw8_font_atlas.py
คอมไพล์ Font Atlas โดยดึงภาพ Glyphs คุณภาพสูงจาก Dynasty Warriors 8 (DW8)
- 44 พยัญชนะไทย + สระแนวบรรทัด
- 653 พยางค์ PUA ยอดนิยมจาก DW8
- ส่วนที่เหลือ fallback ด้วย TTF ที่ baseline เดียวกัน
- ฉีดเข้าสู่ Entry 55 ของ LINKDATA.BIN ใน Atmosphere และ Yuzu
"""

import os
import sys
import json
import time
import shutil
import struct
import subprocess
import numpy as np
from PIL import Image, ImageFont, ImageDraw

SWITCH_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(SWITCH_DIR)

WORKSPACE_DIR = os.path.join(SWITCH_DIR, "workspace")
TEX_DIR = os.path.join(WORKSPACE_DIR, "tex_55")
OUT_G1T_DIR = os.path.join(WORKSPACE_DIR, "out_g1t")
FONT_TTF = os.path.join(SWITCH_DIR, "fonts", "Pridi-Bold.ttf")
G1T_TOOL = os.path.join(SWITCH_DIR, "tools", "g1t_tool.py")

CLEAN_DDS = os.path.join(WORKSPACE_DIR, "tex_clean_55", "clean_entry_00055.TEX0.dxt5.dds")
TARGET_DDS = os.path.join(TEX_DIR, "entry_00055.TEX0.dxt5.dds")
META_PATH = os.path.join(WORKSPACE_DIR, "kanji_cluster_slots.json")

TITLE_ID = "0100CD3000BDC000"
MOD_DIR = os.path.join(BASE_DIR, "mod", "atmosphere", "contents", TITLE_ID, "romfs", "dqh2")
MOD_BIN = os.path.join(MOD_DIR, "LINKDATA.BIN")
YUZU_DIR = os.path.expanduser(r"~\AppData\Roaming\yuzu\load\0100CD3000BDC000\MODTHAI\romfs\dqh2")
YUZU_BIN = os.path.join(YUZU_DIR, "LINKDATA.BIN")

sys.path.append(os.path.join(SWITCH_DIR, "tools"))
from build_thai_keyboard import KEYBOARD_MAPPING, encode_cell_dxt5, pack_entry_chunks

ENTRY_55_OFF = 4805120
ENTRY_55_ZSZ = 1106944
WIDTH_BLOCKS = 4096 // 4  # 1024
BLOCK_BYTES = 16

# 1. โหลดข้อมูล DW8
DW8_GLYPHS_PATH = os.path.join(WORKSPACE_DIR, "dw8_glyphs.json")
DW8_DUMP_DIR = os.path.join(WORKSPACE_DIR, "dw8_font_dump")
USER_MAP_PATH = r"C:\Users\Supakiat\Desktop\Mover\สร้างฟ้อน\mapping.json"

with open(DW8_GLYPHS_PATH, "r", encoding="utf-8") as f:
    dw8_glyphs = json.load(f)

dw8_pages = [
    Image.open(os.path.join(DW8_DUMP_DIR, "dw8_page_0.png")),
    Image.open(os.path.join(DW8_DUMP_DIR, "dw8_page_1.png")),
    Image.open(os.path.join(DW8_DUMP_DIR, "dw8_page_2.png"))
]

with open(USER_MAP_PATH, "r", encoding="utf-8") as f:
    user_map = json.load(f)

# แมป lookup ของ DW8: thai_char/cluster -> glyph_info
dw8_lookup = {}
for g in dw8_glyphs:
    code_val = int(g['code'], 16)
    if 0x0E01 <= code_val <= 0x0E5B:
        dw8_lookup[chr(code_val)] = g
    elif code_val >= 0xF000:
        pua_char = chr(code_val)
        # หาว่า pua_char นี้ตรงกับ thai cluster ไหน
        for cluster, c in user_map.items():
            if c == pua_char:
                dw8_lookup[cluster] = g
                break

print(f"[+] DW8 Glyphs พร้อมใช้งาน: {len(dw8_lookup):,} ตัวอักษรและคลัสเตอร์")

# ฟังก์ชันดึง Glyph จาก DW8 เข้า 36x36 cell
def extract_dw8_cell(glyph_info, target_baseline=29):
    flts = glyph_info['flts']
    p = glyph_info['page']
    u0, v0, u1 = flts[3], flts[4], flts[5]
    x0 = int(round(u0 * 1024))
    y0 = int(round(v0 * 1024))
    x1 = int(round(u1 * 1024))
    
    # ครอปแนวตั้งโดยยึด baseline = 50
    # ต้องการ baseline อยู่ที่ target_baseline (29)
    y_start = max(0, y0 + 50 - target_baseline)
    y_end = min(1024, y_start + 36)
    
    cell_raw = dw8_pages[p].crop((x0, y_start, x1, y_end))
    
    arr = np.array(cell_raw)[:, :, 3]
    coords = np.argwhere(arr > 10)
    if len(coords) == 0:
        return Image.new('RGBA', (36, 36), (0, 0, 0, 0))
        
    min_x = coords[:, 1].min()
    max_x = coords[:, 1].max()
    cr = cell_raw.crop((min_x, 0, max_x + 1, 36))
    
    out_cell = Image.new('RGBA', (36, 36), (0, 0, 0, 0))
    cx = max(0, (36 - cr.width) // 2)
    out_cell.paste(cr, (cx, 0), cr)
    return out_cell

# Fallback font
f_base = ImageFont.truetype(FONT_TTF, 30)
f_single = ImageFont.truetype(FONT_TTF, 27)

def render_fallback_cell(text):
    cell = Image.new('RGBA', (36, 36), (0, 0, 0, 0))
    tdraw = ImageDraw.Draw(cell)
    bbox = f_base.getbbox(text)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    cx = max(0, (36 - w) // 2)
    cy = max(0, 29 - h)
    tdraw.text((cx, cy), text, font=f_base, fill=(255, 255, 255, 255))
    return cell

def get_glyph_cell(text):
    if text in dw8_lookup:
        return extract_dw8_cell(dw8_lookup[text])
    return render_fallback_cell(text)

def main():
    start_time = time.time()
    print("=" * 70)
    print(" [1/4] เตรียมแผ่นภาพสะอาด Entry 55 จาก tex_clean_55...")
    print("=" * 70)
    shutil.copy2(CLEAN_DDS, TARGET_DDS)
    with open(TARGET_DDS, "rb") as f:
        dds_bytes = bytearray(f.read())
    print(f"[+] โหลด DDS สะอาดสำเร็จ: {len(dds_bytes):,} bytes")

    # 2. วาดพยัญชนะและสระแนวบรรทัด 83 ช่อง (Kana)
    print("\n" + "=" * 70)
    print(" [2/4] วาดตัวอักษร 83 ตัวลงในช่อง Kana ด้วยภาพฟอนต์จาก DW8...")
    print("=" * 70)
    dw8_count = 0
    fb_count = 0
    for kana, (row, col), thai_ch in KEYBOARD_MAPPING:
        if thai_ch in dw8_lookup:
            cell_img = extract_dw8_cell(dw8_lookup[thai_ch])
            dw8_count += 1
        else:
            cell_img = render_fallback_cell(thai_ch)
            fb_count += 1
            
        rows_dxt = encode_cell_dxt5(cell_img)
        bx0 = (col * 36) // 4
        by0 = (row * 36) // 4
        for by in range(9):
            offset = 128 + ((by0 + by) * WIDTH_BLOCKS + bx0) * BLOCK_BYTES
            dds_bytes[offset : offset + 144] = rows_dxt[by]
            
    print(f"[+] บันทึก 83 ช่องคีย์บอร์ดสำเร็จ (DW8 แท้: {dw8_count}, Fallback: {fb_count})")

    # 3. วาดคลัสเตอร์ PUA 2,223 ช่อง
    print("\n" + "=" * 70)
    print(" [3/4] วาดคลัสเตอร์ PUA 2,223 ช่องลงในช่องคันจิด้วยภาพฟอนต์จาก DW8...")
    print("=" * 70)
    with open(META_PATH, "r", encoding="utf-8") as f:
        cluster_slots = json.load(f)
        
    t_render = time.time()
    dw8_c_count = 0
    fb_c_count = 0
    for item in cluster_slots:
        thai_str = item['thai']
        row = item['row']
        col = item['col']
        
        if thai_str in dw8_lookup:
            cell_img = extract_dw8_cell(dw8_lookup[thai_str])
            dw8_c_count += 1
        else:
            cell_img = render_fallback_cell(thai_str)
            fb_c_count += 1
            
        rows_dxt = encode_cell_dxt5(cell_img)
        bx0 = (col * 36) // 4
        by0 = (row * 36) // 4
        for by in range(9):
            offset = 128 + ((by0 + by) * WIDTH_BLOCKS + bx0) * BLOCK_BYTES
            dds_bytes[offset : offset + 144] = rows_dxt[by]

    el_render = time.time() - t_render
    print(f"[+] บันทึก {len(cluster_slots)} ช่องคันจิสำเร็จใน {el_render:.1f} วินาที! (DW8 แท้: {dw8_c_count}, Fallback: {fb_c_count})")

    # บันทึก DDS
    with open(TARGET_DDS, "wb") as f:
        f.write(dds_bytes)
    print(f"[+] บันทึก DDS อัปเดต: {TARGET_DDS}")

    # 4. แปลงกลับเป็น G1T และฉีดเข้าเกม
    print("\n" + "=" * 70)
    print(" [4/4] แปลง DDS เป็น G1T และฉีดเข้าสู่ LINKDATA.BIN...")
    print("=" * 70)
    os.makedirs(OUT_G1T_DIR, exist_ok=True)
    cmd = [sys.executable, G1T_TOOL, "import", TEX_DIR, OUT_G1T_DIR]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0, f"g1t_tool import failed: {res.stderr}"
    print(f"    [+] {res.stdout.strip()}")

    out_g1t = os.path.join(OUT_G1T_DIR, "entry_00055.g1t")
    with open(out_g1t, "rb") as f:
        g1t_raw = f.read()

    packed = pack_entry_chunks(g1t_raw)
    pad = b'\x00' * (ENTRY_55_ZSZ - len(packed))
    payload = packed + pad
    assert len(payload) == ENTRY_55_ZSZ

    targets = [
        ("Atmosphere Mod", MOD_BIN),
        ("Yuzu Mod", YUZU_BIN)
    ]

    for name, bin_path in targets:
        if os.path.exists(bin_path):
            with open(bin_path, "r+b") as f:
                f.seek(ENTRY_55_OFF)
                f.write(payload)
            print(f"    [+] ฉีด Entry 55 สำเร็จ -> {name} ({bin_path})")

    total_el = time.time() - start_time
    print("\n" + "=" * 70)
    print(f" [SUCCESS] สร้าง Font Atlas จาก DW8 สำเร็จทั้งหมดใน {total_el:.1f} วินาที!")
    print("=" * 70)

if __name__ == "__main__":
    main()
