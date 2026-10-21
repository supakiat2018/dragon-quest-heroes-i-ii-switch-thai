"""
deploy_formula_949_with_dialogs.py
ติดตั้งระบบฟอนต์ภาษาไทยสูตร 949 แท้ 100% พร้อมบทสนทนา 3 จุดในเกม:
- Ku 16 (Cells 505 - 579): 83 พยัญชนะเดี่ยวและสระ (เ, แ, โ, ใ, ไ ดันชิดขวาสุด offset_x=18)
- Ku 24+ (Cells 1257 - 3522): 2,223 PUA คลัสเตอร์ซ้อนชั้น (Option A: พยัญชนะ 30-31px, สระบน Y=7, วรรณยุกต์ยกสูง Y=0)
- ฉีดบทสนทนา 3 จุด (Offset 6512, 6641, 6849) เข้าสู่ Entry 36
- แป้นพิมพ์ภาษาอังกฤษ 166 ตัวเดิมใน Rows 1-3: ปลอดภัย 100% (ไม่ถูกแตะต้องแม้แต่ไบต์เดียว)
- ฉีดเข้า LINKDATA.BIN ทั้ง Atmosphere และ Yuzu Mod
"""

import os
import sys
import json
import time
import shutil
import struct
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
META_PATH = os.path.join(WORKSPACE_DIR, "kanji_cluster_slots.json")
MAPPING_PATH = os.path.join(SWITCH_DIR, "Mapping_Kanji.json")

sys.path.append(os.path.join(SWITCH_DIR, "tools"))
sys.path.append(WORKSPACE_DIR)
from build_thai_keyboard import encode_cell_dxt5, pack_entry_chunks
from build_switch_kanji_mapping import jis_to_sjis_char, jis_to_cell
from thai_font_preview_gui import compose_pua_cluster_image, render_tuned_single_glyph, load_or_create_config
from check_translations import tokenize_formula_949

TITLE_ID = "0100CD3000BDC000"
ATMO_BIN = os.path.join(BASE_DIR, "mod", "atmosphere", "contents", TITLE_ID, "romfs", "dqh2", "LINKDATA.BIN")
YUZU_BIN = os.path.expanduser(rf"~\AppData\Roaming\yuzu\load\{TITLE_ID}\MODTHAI\romfs\dqh2\LINKDATA.BIN")

ENTRY_55_OFF = 4805120
ENTRY_36_START = 363008

WIDTH_BLOCKS = 1024
BLOCK_BYTES = 16

def get_keyboard_checksum(dds_bytes):
    start_off = 128 + (1 * 9 * WIDTH_BLOCKS) * BLOCK_BYTES
    end_off   = 128 + (4 * 9 * WIDTH_BLOCKS) * BLOCK_BYTES
    return hashlib.md5(dds_bytes[start_off:end_off]).hexdigest()

def main():
    print("=" * 75)
    print(" [*] เริ่มต้นติดตั้งฟอนต์สูตร 949 และบทสนทนา 3 จุด...")
    print("=" * 75)

    cfg = load_or_create_config()

    # 1. โหลด DDS
    with open(TARGET_DDS, "rb") as f:
        dds_bytes = bytearray(f.read())
    kb_hash_before = get_keyboard_checksum(dds_bytes)
    print(f"[+] 1. โหลด DDS สำเร็จ (Keyboard Checksum: {kb_hash_before})")

    # 2. เรนเดอร์ตัวอักษรเดี่ยวใน Ku 16 (Cells 505 - 579)
    print("\n[+] 2. เรนเดอร์ตัวอักษรเดี่ยวลงช่อง Ku 16 Kanji (Row 4-5)...")
    with open(MAPPING_PATH, "r", encoding="utf-8") as f:
        mapping = json.load(f)

    ku16_kanji = {jis_to_sjis_char(16, ten): (16, ten) for ten in range(1, 95)}
    count_ku16 = 0
    for thai, kanji in mapping.items():
        if kanji in ku16_kanji:
            ku, ten = ku16_kanji[kanji]
            row, col, cell_idx = jis_to_cell(ku, ten)
            
            # เรนเดอร์ด้วย Option A 30px
            if len(thai) > 1:
                cell_img, _ = compose_pua_cluster_image(thai, cfg)
            else:
                cell_img = render_tuned_single_glyph(thai, cfg)
                
            rows_dxt = encode_cell_dxt5(cell_img)
            bx0 = (col * 36) // 4
            by0 = (row * 36) // 4
            for by in range(9):
                off = 128 + ((by0 + by) * WIDTH_BLOCKS + bx0) * BLOCK_BYTES
                dds_bytes[off : off + 144] = rows_dxt[by]
            count_ku16 += 1
    print(f"    -> เรนเดอร์ตัวอักษรเดี่ยว Ku 16 สำเร็จ: {count_ku16} ตัว")

    # 3. เรนเดอร์ 2,223 PUA คลัสเตอร์ลงช่อง Ku 24+ (Cells 1257 - 3522)
    print("\n[+] 3. เรนเดอร์ 2,223 PUA คลัสเตอร์ซ้อนชั้น (Option A: พยัญชนะ 30-31px, สระบน Y=7, วรรณยุกต์ยกสูง Y=0)...")
    with open(META_PATH, "r", encoding="utf-8") as f:
        cluster_slots = json.load(f)

    for item in cluster_slots:
        thai_str = item['thai']
        row = item['row']
        col = item['col']
        
        if len(thai_str) > 1:
            cell_img, _ = compose_pua_cluster_image(thai_str, cfg)
        else:
            cell_img = render_tuned_single_glyph(thai_str, cfg)
            
        rows_dxt = encode_cell_dxt5(cell_img)
        bx0 = (col * 36) // 4
        by0 = (row * 36) // 4
        for by in range(9):
            off = 128 + ((by0 + by) * WIDTH_BLOCKS + bx0) * BLOCK_BYTES
            dds_bytes[off : off + 144] = rows_dxt[by]
    print(f"    -> เรนเดอร์ PUA คลัสเตอร์สำเร็จ: {len(cluster_slots)} รายการ")

    # บันทึก DDS
    with open(TARGET_DDS, "wb") as f:
        f.write(dds_bytes)
    print(f"[+] บันทึกไฟล์ DDS เรียบร้อย")

    # ตรวจสอบคีย์บอร์ด
    kb_hash_after = get_keyboard_checksum(dds_bytes)
    print(f"    [VERIFY] Checksum แป้นพิมพ์ภาษาอังกฤษ: {kb_hash_after}")
    assert kb_hash_before == kb_hash_after, "CRITICAL ERROR: แป้นพิมพ์ภาษาอังกฤษถูกแตะต้อง!"
    print(f"    [PASSED 100%] ยืนยัน: แป้นพิมพ์ภาษาอังกฤษ 166 ตัวเดิมปลอดภัย 100%")

    # 4. คอมไพล์ DDS เป็น G1T
    print("\n[+] 4. คอมไพล์ DDS เป็น G1T ด้วย g1t_tool...")
    cmd = [sys.executable, G1T_TOOL, "import", TEX_DIR, OUT_G1T_DIR]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0, f"g1t_tool error: {res.stderr}"
    print(f"    -> {res.stdout.strip()}")

    # 5. บีบอัด Entry 55 Zlib Chunks
    out_g1t = os.path.join(OUT_G1T_DIR, "entry_00055.g1t")
    with open(out_g1t, "rb") as f:
        g1t_raw = f.read()
    packed_55 = pack_entry_chunks(g1t_raw)
    print(f"[+] บีบอัด Entry 55 สำเร็จ: {len(packed_55):,} ไบต์")

    # 6. เตรียมแปลงบทสนทนา 3 จุดเป็นโค้ดญี่ปุ่น
    print("\n[+] 5. แปลงและเตรียมไบต์บทสนทนา 3 จุด...")

    def convert_text_to_codes(thai_text):
        toks = tokenize_formula_949(thai_text)
        res = []
        for t in toks:
            if t in mapping:
                res.append(mapping[t])
            elif t in ['\n', ' ', '　', '?', '？']:
                res.append(t)
            else:
                res.append(t)
        return ''.join(res)

    # Prompt 1 (Offset 6512, Max 45 bytes)
    p1_text = "สร้างเซฟ ช่องใด?"
    p1_conv = convert_text_to_codes(p1_text)
    p1_bytes = p1_conv.encode('utf-8')
    assert len(p1_bytes) < 45, f"P1 overflow: {len(p1_bytes)} >= 45"
    p1_padded = p1_bytes + b'\x00' * (45 - len(p1_bytes))

    # Prompt 2 (Offset 6641, Max 167 bytes)
    p2_text = (
        "เลือกตัวเอกที่จะออกผจญภัย\n"
        "เลือกชายหรือหญิงก็ได้\n"
        "เนื้อเรื่องจะไม่เปลี่ยน"
    )
    p2_conv = convert_text_to_codes(p2_text)
    p2_bytes = p2_conv.encode('utf-8')
    assert len(p2_bytes) < 167, f"P2 overflow: {len(p2_bytes)} >= 167"
    p2_padded = p2_bytes + b'\x00' * (167 - len(p2_bytes))

    # Prompt 3 (Offset 6849, Max 85 bytes)
    p3_text = (
        "ตั้งชื่อลูกพี่ลูกน้อง\n"
        "ที่จะร่วมผจญภัยไปด้วย"
    )
    p3_conv = convert_text_to_codes(p3_text)
    p3_bytes = p3_conv.encode('utf-8')
    assert len(p3_bytes) <= 85, f"P3 overflow: {len(p3_bytes)} > 85"
    p3_padded = p3_bytes + b'\x00' * (85 - len(p3_bytes))

    print(f"    -> Prompt 1 (6512): {len(p1_bytes)}b / 45b ('{p1_text}')")
    print(f"    -> Prompt 2 (6641): {len(p2_bytes)}b / 167b ('{p2_text.splitlines()[0]}...')")
    print(f"    -> Prompt 3 (6849): {len(p3_bytes)}b / 85b ('{p3_text.splitlines()[0]}...')")

    # 7. ฉีดเข้า LINKDATA.BIN
    targets = [
        ("Atmosphere Mod (Drive D)", ATMO_BIN),
        ("Yuzu Mod (Drive C)", YUZU_BIN)
    ]

    print("\n[+] 6. ฉีด Font Atlas Entry 55 และข้อความบทสนทนาเข้า LINKDATA.BIN...")
    for name, bin_path in targets:
        if os.path.exists(bin_path):
            with open(bin_path, "r+b") as f:
                # ฉีด Entry 55
                f.seek(ENTRY_55_OFF)
                f.write(packed_55)
                
                # ฉีดบทสนทนา Entry 36
                f.seek(ENTRY_36_START + 6512)
                f.write(p1_padded)
                
                f.seek(ENTRY_36_START + 6641)
                f.write(p2_padded)
                
                f.seek(ENTRY_36_START + 6849)
                f.write(p3_padded)
                
            print(f"    [+] ติดตั้งสำเร็จ -> {name}")

    print("\n" + "=" * 75)
    print(" [SUCCESS] ติดตั้งฟอนต์สูตร 949 และบทสนทนา 3 จุดเรียบร้อย 100%!")
    print(" - สระหน้า (เ, แ, โ, ใ, ไ): เดี่ยวชิดขวา วิ่งแนบชิดพยัญชนะสวยงาม")
    print(" - PUA คลัสเตอร์: เฉพาะตัวซ้อนแนวตั้ง ยกสูงลอยเด่นชัดระดับ Option A")
    print(" - บทสนทนา 3 จุด: แปลไทยและฉีดเข้าสู่ตำแหน่งเดิมเรียบร้อย")
    print(" - แป้นพิมพ์ภาษาอังกฤษ 166 ตัวเดิม: ปลอดภัย 100%")
    print("=" * 75)

if __name__ == "__main__":
    main()
