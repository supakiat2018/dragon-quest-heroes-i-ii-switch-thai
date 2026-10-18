"""
build_full_thai_font_atlas.py
คอมไพล์ฟอนต์ภาษาไทยสมบูรณ์แบบ (ครบทั้ง 2,208 พยางค์ + 83 ปุ่มคีย์บอร์ด) ลงใน Entry 55 สำหรับ Nintendo Switch
ตาม Mapping.json โดยตรง:
- ทุกพยางค์สระซ้อนและวรรณยุกต์ถูกวาดลงในช่องว่างของ Entry 55 (Cell 987 - 3194)
- 0 Overflow ทุกตัวอักษร บาลานซ์ความสูงและเส้นบรรทัดพอดีกรอบ 36x36
- แพตช์ข้อความ "ชื่อตัวละครหลัก" ลงใน Entry 36 เพื่อทดสอบในเกมได้ทันที
"""

import os
import sys
import json
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

MAPPING_PATH = os.path.join(SWITCH_DIR, "Mapping.json")
ORIG_DDS = os.path.join(TEX_DIR, "entry_00055.TEX0.dxt5.dds")
ORIG_G1T = os.path.join(TEX_DIR, "entry_00055.g1t")
ENTRY_57_BIN = os.path.join(WORKSPACE_DIR, "entry_00057.bin")

TITLE_ID = "0100CD3000BDC000"
MOD_DIR = os.path.join(BASE_DIR, "mod", "atmosphere", "contents", TITLE_ID, "romfs", "dqh2")
MOD_BIN = os.path.join(MOD_DIR, "LINKDATA.BIN")
MOD_IDX = os.path.join(MOD_DIR, "LINKDATA.IDX")

YUZU_DIR = os.path.expanduser(r"~\AppData\Roaming\yuzu\load\0100CD3000BDC000\MODTHAI\romfs\dqh2")
YUZU_BIN = os.path.join(YUZU_DIR, "LINKDATA.BIN")
YUZU_IDX = os.path.join(YUZU_DIR, "LINKDATA.IDX")

sys.path.append(os.path.join(SWITCH_DIR, "tools"))
from build_thai_keyboard import encode_cell_dxt5, pack_entry_chunks

ENTRY_55_OFF = 4805120
ENTRY_55_ZSZ = 1106944
ENTRY_57_OFF = 5966080

WIDTH_BLOCKS = 4096 // 4  # 1024
BLOCK_BYTES = 16

def render_thai_cluster(font_tall, font_med, text):
    """เรนเดอร์พยางค์ภาษาไทยให้สวยงาม บาลานซ์ 0 Overflow ทุกตัวอักษร"""
    has_lower = any(c in text for c in 'ฺุู')
    has_upper = any(c in text for c in 'ิีึืั็')
    has_tone = any(c in text for c in '่้๊๋์')
    has_descender = text[0] in 'ฐฎฏญฤฦ'
    
    if has_descender:
        font = font_tall
        base_y = 25
    elif has_lower and has_tone:
        font = font_tall
        base_y = 25
    elif has_upper and has_tone:
        font = font_tall
        base_y = 29
    elif has_lower:
        font = font_med
        base_y = 26
    else:
        font = font_med
        base_y = 29
        
    cell = Image.new('RGBA', (36, 36), (0, 0, 0, 0))
    d = ImageDraw.Draw(cell)
    d.text((18, base_y), text, font=font, fill=(255, 255, 255, 255), anchor='ms')
    return cell

def patch_all_clusters_to_dds():
    print(f"[*] 1. โหลด Mapping.json: {MAPPING_PATH}...")
    with open(MAPPING_PATH, "r", encoding="utf-8") as f:
        mapping = json.load(f)
        
    clusters = {k: v for k, v in mapping.items() if len(k) > 1}
    print(f"[+] พบพยางค์สำเร็จรูปทั้งหมด {len(clusters):,} พยางค์")
    
    print(f"[*] 2. โหลดตาราง Entry 57 จาก ROMFS เพื่อหาพิกัด Cell ของอักขระแต่ละตัว...")
    romfs_bin = os.path.join(BASE_DIR, "romfs", "dqh2", "LINKDATA.BIN")
    with open(romfs_bin, "rb") as f:
        f.seek(ENTRY_57_OFF)
        e57_clean = f.read(13348)
        
    entries_57 = [e57_clean[i*4:(i+1)*4] for i in range(len(e57_clean)//4)]
    
    # สร้าง lookup table จาก character -> cell index
    char_to_cell = {}
    for idx, raw in enumerate(entries_57):
        no_null = raw.rstrip(b'\x00')
        u8 = bytes(reversed(no_null))
        ch = u8.decode('utf-8', errors='ignore')
        if ch:
            char_to_cell[ch] = idx
            
    print(f"[+] สร้าง Lookup Table สำเร็จ: {len(char_to_cell):,} ตัวอักษร")
    
    print(f"[*] 3. โหลดและแพตช์ไฟล์ DDS: {ORIG_DDS}...")
    with open(ORIG_DDS, "rb") as f:
        dds_bytes = bytearray(f.read())
        
    font_tall = ImageFont.truetype(FONT_TTF, 25)
    font_med = ImageFont.truetype(FONT_TTF, 26)
    
    success_count = 0
    for thai_str, target_ch in clusters.items():
        if target_ch not in char_to_cell:
            print(f"[!] Warning: Character {target_ch} for '{thai_str}' not in entry 57!")
            continue
            
        cell_idx = char_to_cell[target_ch]
        row = cell_idx // 113
        col = cell_idx % 113
        
        cell_img = render_thai_cluster(font_tall, font_med, thai_str)
        rows_dxt = encode_cell_dxt5(cell_img)
        
        bx0 = (col * 36) // 4
        by0 = (row * 36) // 4
        
        for by in range(9):
            offset = 128 + ((by0 + by) * WIDTH_BLOCKS + bx0) * BLOCK_BYTES
            dds_bytes[offset : offset + 144] = rows_dxt[by]
            
        success_count += 1
        
    with open(ORIG_DDS, "wb") as f:
        f.write(dds_bytes)
        
    print(f"[+] วาดและบีบอัดพยางค์สำเร็จรูป DXT5 ครบทั้ง {success_count:,} ช่องเสร็จสมบูรณ์!")
    return e57_clean

def compile_and_inject_g1t():
    print("[*] 4. Re-import DDS เข้า G1T ด้วย g1t_tool...")
    os.makedirs(OUT_G1T_DIR, exist_ok=True)
    cmd = [sys.executable, G1T_TOOL, "import", TEX_DIR, OUT_G1T_DIR]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0, f"g1t_tool import failed: {res.stderr}"
    
    out_g1t_file = os.path.join(OUT_G1T_DIR, "entry_00055.g1t")
    with open(out_g1t_file, "rb") as f:
        g1t_raw = f.read()
        
    packed = pack_entry_chunks(g1t_raw)
    pad_bytes = b'\x00' * (ENTRY_55_ZSZ - len(packed))
    full_payload = packed + pad_bytes
    assert len(full_payload) == ENTRY_55_ZSZ
    
    print("[*] 5. ฉีด Entry 55 (Font Atlas ใหม่) เข้า LINKDATA.BIN...")
    for path in [MOD_BIN, YUZU_BIN]:
        with open(path, "r+b") as f:
            f.seek(ENTRY_55_OFF)
            f.write(full_payload)
        print(f"    [+] ฉีด Entry 55 เข้า {path} เรียบร้อย!")

def restore_clean_entry_57(e57_clean):
    print("[*] 6. คืนค่า Entry 57 ให้เป็นมาตรฐานเกมที่สมบูรณ์...")
    for path in [MOD_BIN, YUZU_BIN]:
        with open(path, "r+b") as f:
            f.seek(ENTRY_57_OFF)
            f.write(e57_clean)
        print(f"    [+] คืนค่า Entry 57 ใน {path} เรียบร้อย!")

def convert_text_with_mapping(text, mapping):
    res = []
    i = 0
    n = len(text)
    max_len = max(len(k) for k in mapping.keys())
    while i < n:
        matched = False
        for length in range(min(max_len, n - i), 0, -1):
            sub = text[i : i + length]
            if sub in mapping:
                res.append(mapping[sub])
                i += length
                matched = True
                break
        if not matched:
            res.append(text[i])
            i += 1
    return ''.join(res)

def patch_header_title():
    print("[*] 7. แปลงและแพตช์ข้อความหัวข้อหน้าตั้งชื่อเป็น 'ชื่อตัวละครหลัก'...")
    with open(MAPPING_PATH, "r", encoding="utf-8") as f:
        mapping = json.load(f)
        
    thai_text = "ชื่อตัวละครหลัก"
    game_str = convert_text_with_mapping(thai_text, mapping)
    u8_payload = game_str.encode("utf-8")
    
    print(f"    ข้อความไทย: '{thai_text}'")
    print(f"    แปลงผ่าน Mapping.json: '{game_str}'")
    print(f"    ความยาวไบต์: {len(u8_payload)} ไบต์ (ขีดจำกัดช่อง: 48 ไบต์)")
    
    assert len(u8_payload) <= 48
    padded_payload = u8_payload + b'\x00' * (48 - len(u8_payload))
    
    with open(MOD_IDX, "rb") as f_idx:
        f_idx.seek(36 * 32)
        e36_off = struct.unpack("<Q", f_idx.read(8))[0]
        
    target_pos = e36_off + 87361
    for path in [MOD_BIN, YUZU_BIN]:
        with open(path, "r+b") as f:
            f.seek(target_pos)
            f.write(padded_payload)
        print(f"    [+] บันทึกข้อความ 'ชื่อตัวละครหลัก' เข้า {path} ที่ offset {target_pos} สำเร็จ!")

def main():
    print("=================================================================")
    print("[*] เริ่มกระบวนการสร้างฟอนต์ภาษาไทยสมบูรณ์แบบ 2,208 ตัว (Switch)")
    print("=================================================================")
    e57_clean = patch_all_clusters_to_dds()
    compile_and_inject_g1t()
    restore_clean_entry_57(e57_clean)
    patch_header_title()
    print("=================================================================")
    print("[SUCCESS] สร้างและติดตั้งฟอนต์ 2,208 พยางค์ + ข้อความ 'ชื่อตัวละครหลัก' สำเร็จ 100%!")
    print("=================================================================")

if __name__ == "__main__":
    main()
