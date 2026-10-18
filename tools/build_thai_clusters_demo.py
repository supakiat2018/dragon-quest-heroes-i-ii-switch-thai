"""
build_thai_clusters_demo.py
ติดตั้งระบบพยางค์สำเร็จรูป (Precomposed Clusters / PUA) ลงใน Dragon Quest Heroes II บน Nintendo Switch:
1. วาดพยางค์ 'ชื่', 'ตั', 'ลั' ด้วย Pridi-Bold ลงใน Entry 55 (Font Atlas) ที่ Cell 987, 988, 989
2. แมปรหัส PUA \uF59B ('ชื่'), \uF014 ('ตั'), \uF024 ('ลั') ลงใน Entry 57 (Character Map)
3. แพตช์ข้อความหัวข้อหน้าตั้งชื่อตัวเอกเป็น 'ชื่อตัวละครหลัก' (สระและวรรณยุกต์รวมร่าง ไม่เว้นวรรคห่าง)
"""

import os
import sys
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
ENTRY_57_SZ = 13348

WIDTH_BLOCKS = 4096 // 4  # 1024
BLOCK_BYTES = 16

# รายการพยางค์ทดสอบนำร่องสำหรับคำว่า "ชื่อตัวละครหลัก"
CLUSTERS = [
    # (Thai cluster, PUA code, Cell index in Entry 55 & 57)
    ("ชื่", "\uf59b", 987), # Row 8, Col 83
    ("ตั", "\uf014", 988), # Row 8, Col 84
    ("ลั", "\uf024", 989), # Row 8, Col 85
]

def render_cluster(font, text):
    """เรนเดอร์พยางค์ไทยรวมแนวตั้ง ให้สระและวรรณยุกต์ซ้อนบนหัวพยัญชนะเป๊ะๆ ขนาด 36x36"""
    cell = Image.new('RGBA', (36, 36), (0, 0, 0, 0))
    d = ImageDraw.Draw(cell)
    d.text((18, 30), text, font=font, fill=(255, 255, 255, 255), anchor='ms')
    return cell

def patch_entry_55_dds():
    print(f"[*] กำลังแพตช์พยางค์สำเร็จรูป 'ชื่', 'ตั', 'ลั' ลงใน DDS: {ORIG_DDS}...")
    with open(ORIG_DDS, "rb") as f:
        dds_bytes = bytearray(f.read())
        
    f_cluster = ImageFont.truetype(FONT_TTF, 26)
    
    for thai_str, pua_code, cell_idx in CLUSTERS:
        row = cell_idx // 113
        col = cell_idx % 113
        
        cell_img = render_cluster(f_cluster, thai_str)
        rows_dxt = encode_cell_dxt5(cell_img)
        
        bx0 = (col * 36) // 4
        by0 = (row * 36) // 4
        
        for by in range(9):
            offset = 128 + ((by0 + by) * WIDTH_BLOCKS + bx0) * BLOCK_BYTES
            dds_bytes[offset : offset + 144] = rows_dxt[by]
            
        print(f"    [+] วาดพยางค์ '{thai_str}' (PUA U+{ord(pua_code):04X}) ลงที่ Cell {cell_idx} (Row {row}, Col {col})")
        
    with open(ORIG_DDS, "wb") as f:
        f.write(dds_bytes)
    print(f"[+] บันทึกไฟล์ DDS เรียบร้อย")

def build_and_inject_entry_55():
    print("[*] Re-importing DDS เข้า G1T ด้วย g1t_tool...")
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
    
    for path in [MOD_BIN, YUZU_BIN]:
        with open(path, "r+b") as f:
            f.seek(ENTRY_55_OFF)
            f.write(full_payload)
        print(f"[+] ฉีด Entry 55 เข้า {path} เรียบร้อย!")

def patch_and_inject_entry_57():
    print(f"[*] กำลังแมปรหัส PUA เข้าสู่ Entry 57 (Character Map)...")
    with open(ENTRY_57_BIN, "rb") as f:
        cmap = bytearray(f.read())
        
    for thai_str, pua_code, cell_idx in CLUSTERS:
        u8_bytes = pua_code.encode("utf-8")
        entry_bytes = bytes(reversed(u8_bytes)).ljust(4, b'\x00')
        cmap[cell_idx * 4 : (cell_idx + 1) * 4] = entry_bytes
        print(f"    [+] แมปรหัส Entry 57 index {cell_idx} -> PUA '{pua_code}' ({entry_bytes.hex()}) สำหรับ '{thai_str}'")
        
    with open(ENTRY_57_BIN, "wb") as f:
        f.write(cmap)
        
    for path in [MOD_BIN, YUZU_BIN]:
        with open(path, "r+b") as f:
            f.seek(ENTRY_57_OFF)
            f.write(cmap)
        print(f"[+] ฉีด Entry 57 เข้า {path} เรียบร้อย!")

def patch_header_text_with_clusters():
    print("[*] กำลังแปลงข้อความ 'ชื่อตัวละครหลัก' ด้วยระบบพยางค์ PUA...")
    # การแปลง:
    # "ชื่" -> \uf59b (PUA cluster)
    # "อ"   -> よ (Base consonant)
    # "ตั"  -> \uf014 (PUA cluster)
    # "ว"   -> み (Base consonant)
    # "ล"   -> ま (Base consonant)
    # "ะ"   -> ん (In-line vowel)
    # "ค"   -> え (Base consonant)
    # "ร"   -> ほ (Base consonant)
    # "ห"   -> や (Base consonant)
    # "ลั"  -> \uf024 (PUA cluster)
    # "ก"   -> あ (Base consonant)
    game_string = "\uf59bよ\uf014みまんえほや\uf024あ"
    u8_payload = game_string.encode("utf-8")
    print(f"[*] Game encoded string: {repr(game_string)} ({len(u8_payload)} bytes)")
    
    assert len(u8_payload) <= 48
    padded_payload = u8_payload + b'\x00' * (48 - len(u8_payload))
    
    # อ่าน offset ของ Entry 36 จาก LINKDATA.IDX (ซึ่งชี้ไปที่ 3740846848)
    with open(MOD_IDX, "rb") as f_idx:
        f_idx.seek(36 * 32)
        e36_off = struct.unpack("<Q", f_idx.read(8))[0]
    print(f"[*] Entry 36 Offset from IDX: {e36_off}")
    
    target_pos = e36_off + 87361
    for path in [MOD_BIN, YUZU_BIN]:
        with open(path, "r+b") as f:
            f.seek(target_pos)
            f.write(padded_payload)
        print(f"[+] เขียนข้อความ 'ชื่อตัวละครหลัก' เข้า {path} ที่ offset {target_pos} สำเร็จ!")

def main():
    print("=================================================================")
    print("[*] Switch DQH2 - Thai Precomposed Clusters (PUA) Mod Pipeline")
    print("=================================================================")
    patch_entry_55_dds()
    build_and_inject_entry_55()
    patch_and_inject_entry_57()
    patch_header_text_with_clusters()
    print("=================================================================")
    print("[SUCCESS] ติดตั้งพยางค์สำเร็จรูปและแพตช์ข้อความ 'ชื่อตัวละครหลัก' เรียบร้อย 100%!")
    print("=================================================================")

if __name__ == "__main__":
    main()
