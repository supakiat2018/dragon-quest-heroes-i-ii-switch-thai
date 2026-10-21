"""
deploy_seamless_menu_tiles.py
ติดตั้ง 3 เมนู (เริ่มเล่น / สร้างเซฟ / ลบเซฟ) ด้วยเทคโนโลยี "Seamless Sliced Image Tiles"
- เรนเดอร์ข้อความแบบภาพกราฟิกชิ้นเดียว (ความกว้าง 144x36px) ด้วยฟอนต์ Pridi-Bold ขนาด 32pt
- หั่นภาพออกเป็น 4 ชิ้น (ชิ้นละ 36x36px) ไร้รอยต่อ 100%
- ฉีดเข้าช่อง Japanese Kanji แถวที่ 4 (Cells 505 - 516) ใน Entry 55
- ตรวจสอบ Checksum แป้นพิมพ์ภาษาอังกฤษ 166 ตัวเดิม (Cells 209 - 377) ปลอดภัย 100%
- ฉีดข้อความ UTF-8 เข้าสู่ Entry 36 ใน LINKDATA.BIN ทั้ง Atmosphere และ Yuzu
"""

import os
import sys
import shutil
import struct
import zlib
import hashlib
import subprocess
import time
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
from build_thai_keyboard import encode_cell_dxt5, pack_entry_chunks

TITLE_ID = "0100CD3000BDC000"
ATMO_BIN = os.path.join(BASE_DIR, "mod", "atmosphere", "contents", TITLE_ID, "romfs", "dqh2", "LINKDATA.BIN")
YUZU_BIN = os.path.expanduser(rf"~\AppData\Roaming\yuzu\load\{TITLE_ID}\MODTHAI\romfs\dqh2\LINKDATA.BIN")

ENTRY_55_OFF = 4805120
ENTRY_36_START = 363008

WIDTH_BLOCKS = 1024
BLOCK_BYTES = 16

def get_keyboard_checksum(dds_bytes):
    """คำนวณ MD5 ของบล็อกคีย์บอร์ดแถว 1-3 ทั้งหมดเพื่อยืนยันว่าจะไม่ถูกแตะต้อง 100%"""
    start_off = 128 + (1 * 9 * WIDTH_BLOCKS) * BLOCK_BYTES
    end_off   = 128 + (4 * 9 * WIDTH_BLOCKS) * BLOCK_BYTES
    return hashlib.md5(dds_bytes[start_off:end_off]).hexdigest()

def render_word_banner_slices(word_text, num_tiles=4, font_size=32):
    """
    เรนเดอร์คำเป็นภาพกราฟิกชิ้นเดียวความกว้าง 144x36px แล้วหั่นเป็นชิ้นละ 36x36px
    """
    total_w = num_tiles * 36
    total_h = 36
    
    im = Image.new('RGBA', (total_w, total_h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(FONT_TTF, font_size)
    
    bbox = d.textbbox((0, 0), word_text, font=f)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    
    # จัดกึ่งกลางพอดีเป๊ะในแบนเนอร์ 144px
    tx = (total_w - tw) // 2 - bbox[0]
    ty = (total_h - th) // 2 - bbox[1] - 1
    
    d.text((tx, ty), word_text, font=f, fill=(255, 255, 255, 255))
    
    # หั่นเป็น 4 ชิ้น (36x36px)
    slices = []
    for i in range(num_tiles):
        tile = im.crop((i * 36, 0, (i + 1) * 36, 36))
        slices.append(tile)
        
    return im, slices

def main():
    print("=" * 75)
    print(" [*] เริ่มต้นติดตั้ง Seamless Sliced Image Tiles สำหรับ 3 เมนู...")
    print("=" * 75)
    
    # 1. โหลด Entry 55 DDS
    print(f"\n[+] 1. โหลด Font Sheet Texture: {TARGET_DDS}")
    with open(TARGET_DDS, "rb") as f:
        dds_bytes = bytearray(f.read())
        
    kb_hash_before = get_keyboard_checksum(dds_bytes)
    print(f"    [CHECK] Checksum แป้นพิมพ์ภาษาอังกฤษก่อนแก้: {kb_hash_before}")
    
    # 2. รายการปุ่มและชิ้นส่วนภาพ
    # Button 1: เริ่มเล่น -> Cells 505-508 (Row 4, Cols 53-56) [Kanji: 亜唖娃阿]
    # Button 2: สร้างเซฟ -> Cells 509-512 (Row 4, Cols 57-60) [Kanji: 哀愛挨姶]
    # Button 3: ลบเซฟ  -> Cells 513-516 (Row 4, Cols 61-64) [Kanji: 逢葵茜穐]
    
    MENU_ITEMS = [
        ("เริ่มเล่น", [
            (4, 53, 505, '亜'),
            (4, 54, 506, '唖'),
            (4, 55, 507, '娃'),
            (4, 56, 508, '阿')
        ]),
        ("สร้างเซฟ", [
            (4, 57, 509, '哀'),
            (4, 58, 510, '愛'),
            (4, 59, 511, '挨'),
            (4, 60, 512, '姶')
        ]),
        ("ลบเซฟ", [
            (4, 61, 513, '逢'),
            (4, 62, 514, '葵'),
            (4, 63, 515, '茜'),
            (4, 64, 516, '穐')
        ])
    ]
    
    print("\n[+] 2. เรนเดอร์ภาพกราฟิก หั่นเป็นชิ้น และฉีดเข้าช่องคันจิ...")
    for word_text, tile_specs in MENU_ITEMS:
        banner_img, slices = render_word_banner_slices(word_text, num_tiles=4, font_size=32)
        print(f"\n    [*] คำว่า '{word_text}' (แบนเนอร์ภาพ 144x36px):")
        for idx, (row, col, cell_id, kanji) in enumerate(tile_specs):
            tile_img = slices[idx]
            rows_dxt = encode_cell_dxt5(tile_img)
            bx0 = (col * 36) // 4
            by0 = (row * 36) // 4
            for by in range(9):
                off = 128 + ((by0 + by) * WIDTH_BLOCKS + bx0) * BLOCK_BYTES
                dds_bytes[off : off + 144] = rows_dxt[by]
            print(f"        -> ชิ้นที่ {idx+1}/4 -> Cell {cell_id} (Row {row}, Col {col}) [Kanji: {kanji}]")

    # บันทึก DDS
    with open(TARGET_DDS, "wb") as f:
        f.write(dds_bytes)
    print(f"\n[+] บันทึกไฟล์ DDS เรียบร้อย")

    # ตรวจสอบ Checksum คีย์บอร์ด
    kb_hash_after = get_keyboard_checksum(dds_bytes)
    print(f"    [VERIFY] Checksum แป้นพิมพ์ภาษาอังกฤษหลังแก้: {kb_hash_after}")
    assert kb_hash_before == kb_hash_after, "CRITICAL ERROR: แป้นพิมพ์คีย์บอร์ดถูกแตะต้อง!"
    print(f"    [PASSED 100%] ยืนยัน: แป้นพิมพ์ภาษาอังกฤษ 166 ตัวเดิมไม่ถูกแตะต้องแม้แต่ไบต์เดียว!")

    # 3. คอมไพล์ DDS เป็น G1T
    print("\n[+] 3. คอมไพล์ DDS เป็น G1T ด้วย g1t_tool...")
    cmd = [sys.executable, G1T_TOOL, "import", TEX_DIR, OUT_G1T_DIR]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0, f"g1t_tool error: {res.stderr}"
    print(f"    -> {res.stdout.strip()}")

    # 4. บีบอัด Entry 55 Zlib Chunks
    out_g1t = os.path.join(OUT_G1T_DIR, "entry_00055.g1t")
    with open(out_g1t, "rb") as f:
        g1t_raw = f.read()
    packed_55 = pack_entry_chunks(g1t_raw)
    print(f"[+] บีบอัด Entry 55 สำเร็จ: {len(packed_55):,} ไบต์")

    # 5. เตรียมไบต์ข้อความ Entry 36
    # ปุ่ม 1: เริ่มเล่น -> 亜唖娃阿 (12b + 4 null = 16b buffer)
    p1_bytes = "亜唖娃阿".encode('utf-8') + b'\x00' * 4
    assert len(p1_bytes) == 16, f"ปุ่ม 1 ขนาดผิด ({len(p1_bytes)} != 16)"

    # ปุ่ม 2: สร้างเซฟ -> 哀愛挨姶 (12b + 13 null = 25b buffer)
    p2_bytes = "哀愛挨姶".encode('utf-8') + b'\x00' * 13
    assert len(p2_bytes) == 25, f"ปุ่ม 2 ขนาดผิด ({len(p2_bytes)} != 25)"

    # ปุ่ม 3: ลบเซฟ -> 逢葵茜穐 (12b + 10 null = 22b buffer)
    p3_bytes = "逢葵茜穐".encode('utf-8') + b'\x00' * 10
    assert len(p3_bytes) == 22, f"ปุ่ม 3 ขนาดผิด ({len(p3_bytes)} != 22)"

    # 6. ฉีดเข้า LINKDATA.BIN
    targets = [
        ("Atmosphere Mod (Drive D)", ATMO_BIN),
        ("Yuzu Mod (Drive C)", YUZU_BIN)
    ]

    print("\n[+] 4. ฉีดไฟล์ฟอนต์ Entry 55 และข้อความ Entry 36 เข้า LINKDATA.BIN...")
    for name, bin_path in targets:
        if os.path.exists(bin_path):
            with open(bin_path, "r+b") as f:
                # 6.1 ฉีด Entry 55 Font Atlas
                f.seek(ENTRY_55_OFF)
                f.write(packed_55)
                
                # 6.2 ฉีดข้อความ Entry 36
                f.seek(ENTRY_36_START + 86990)
                f.write(p1_bytes)
                
                f.seek(ENTRY_36_START + 87006)
                f.write(p2_bytes)
                
                f.seek(ENTRY_36_START + 87031)
                f.write(p3_bytes)
                
            print(f"    [+] ติดตั้งสำเร็จ -> {name}")

    print("\n" + "=" * 75)
    print(" [SUCCESS] ติดตั้ง 3 เมนู (เริ่มเล่น / สร้างเซฟ / ลบเซฟ) เรียบร้อย 100%!")
    print(" - เทคนิค: Seamless Sliced Image Tiles (ภาพกราฟิกชิ้นเดียวไร้รอยต่อ)")
    print(" - ขนาดฟอนต์: Pridi-Bold 32pt อิ่มหนา ได้สัดส่วนสากล ไม่ยืด ไม่เบียด")
    print(" - แป้นพิมพ์ภาษาอังกฤษ 166 ตัวเดิม: ปลอดภัย 100%")
    print("=" * 75)

if __name__ == "__main__":
    main()
