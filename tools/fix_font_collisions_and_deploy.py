"""
fix_font_collisions_and_deploy.py
แก้ไขปัญหาการชนกันของฟอนต์ใน DQH2 อย่างสมบูรณ์ 100%:
1. ย้ายพยัญชนะเดี่ยวและสระทั้งหมด 76 ตัวจาก Ku 16 (Cell 505..581 ที่ชนกับเมนู)
   ไปอยู่ที่ Ku 20 (Cell 881..957 โซนว่างสนิท ปลอดภัย 100%)
2. อัปเดต Mapping_Kanji.json ให้ชี้ไปที่คันจิของ Ku 20
3. เรนเดอร์ตัวอักษรเดี่ยว 76 ตัวลงใน Ku 20 ของ entry_00055.TEX0.dxt5.dds (Option A 30px)
4. คอมไพล์ DDS -> G1T -> Entry 55 และฉีดเข้า LINKDATA.BIN
5. อัปเดตข้อความใน Entry 36 ทั้งหมด (บทสนทนา 3 จุด + ประวัติตัวละคร 2 ตัว) ด้วย Mapping ใหม่
6. ตรวจสอบการชนกัน: ต้องเป็น 0 ตัว 100%
"""

import os
import sys
import json
import time
import shutil
import struct
import hashlib
import subprocess
from PIL import Image

BASE_DIR = r"D:\Game\dragon quest heroes i & ii"
SWITCH_DIR = os.path.join(BASE_DIR, "switch")
WORKSPACE_DIR = os.path.join(SWITCH_DIR, "workspace")
TEX_DIR = os.path.join(WORKSPACE_DIR, "tex_55")
OUT_G1T_DIR = os.path.join(WORKSPACE_DIR, "out_g1t")
TARGET_DDS = os.path.join(TEX_DIR, "entry_00055.TEX0.dxt5.dds")
G1T_TOOL = os.path.join(SWITCH_DIR, "tools", "g1t_tool.py")
MAPPING_PATH = os.path.join(SWITCH_DIR, "Mapping_Kanji.json")

sys.path.append(os.path.join(SWITCH_DIR, "tools"))
sys.path.append(WORKSPACE_DIR)
from build_thai_keyboard import encode_cell_dxt5, pack_entry_chunks
from build_switch_kanji_mapping import jis_to_sjis_char, jis_to_cell
from thai_font_preview_gui import compose_pua_cluster_image, render_tuned_single_glyph, load_or_create_config
from check_translations import tokenize_formula_949

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

def get_keyboard_checksum(dds_bytes):
    start_off = 128 + (1 * 9 * WIDTH_BLOCKS) * BLOCK_BYTES
    end_off   = 128 + (4 * 9 * WIDTH_BLOCKS) * BLOCK_BYTES
    return hashlib.md5(dds_bytes[start_off:end_off]).hexdigest()

def get_kanji_ku_ten(kanji_char):
    try:
        sjis = kanji_char.encode('shift_jis')
    except Exception:
        return None, None
    if len(sjis) != 2:
        return None, None
    b1, b2 = sjis[0], sjis[1]
    if b2 >= 0x9f:
        ku = (b1 - 0x81) * 2 + 2 if b1 < 0xe0 else (b1 - 0xc1) * 2 + 2
        ten = b2 - 0x9e
    else:
        ku = (b1 - 0x81) * 2 + 1 if b1 < 0xe0 else (b1 - 0xc1) * 2 + 1
        ten = b2 - 0x3f if b2 < 0x7f else b2 - 0x40
    return ku, ten

def main():
    print("=" * 80)
    print(" [*] เริ่มต้นแก้ไขปัญหา Font Cell Collisions ย้ายพยัญชนะเดี่ยวไป Ku 20...")
    print("=" * 80)

    # -------------------------------------------------------------
    # 1. โหลดและอัปเดต Mapping_Kanji.json
    # -------------------------------------------------------------
    print("\n[+] 1. ตรวจสอบและอัปเดต Mapping_Kanji.json จาก Ku 16 -> Ku 20...")
    with open(MAPPING_PATH, "r", encoding="utf-8") as f:
        mapping = json.load(f)

    # สำรองไฟล์เดิมไว้
    shutil.copy2(MAPPING_PATH, MAPPING_PATH + ".bak")

    moved_count = 0
    moved_list = []
    new_mapping = {}
    for thai, kanji in mapping.items():
        ku, ten = get_kanji_ku_ten(kanji)
        if ku == 16:
            # ย้ายจาก Ku 16 ไป Ku 20 ที่ Ten เดียวกัน!
            new_kanji = jis_to_sjis_char(20, ten)
            new_mapping[thai] = new_kanji
            moved_count += 1
            moved_list.append((thai, kanji, new_kanji, ten))
        else:
            new_mapping[thai] = kanji

    with open(MAPPING_PATH, "w", encoding="utf-8") as f:
        json.dump(new_mapping, f, ensure_ascii=False, indent=2)

    print(f"    -> ย้ายพยัญชนะเดี่ยวและสระทั้งหมด {moved_count} ตัวไป Ku 20 สำเร็จ!")
    print(f"    -> ตัวอย่าง: 'ก' ({moved_list[0][1]} -> {moved_list[0][2]}), 'น' ({moved_list[24][1]} -> {moved_list[24][2]}), 'เ' ({moved_list[48][1]} -> {moved_list[48][2]})")

    # -------------------------------------------------------------
    # 2. ตรวจสอบว่ายังมี Collision หลงเหลือหรือไม่
    # -------------------------------------------------------------
    menu_cells = set(range(505, 739))
    guide_cells = set(range(740, 817))
    kb_cells = set(range(0, 339))
    collisions_remaining = 0
    for thai, kanji in new_mapping.items():
        ku, ten = get_kanji_ku_ten(kanji)
        if ku is not None:
            _, _, cell = jis_to_cell(ku, ten)
            if cell in menu_cells or cell in guide_cells or cell in kb_cells:
                collisions_remaining += 1

    print(f"    [AUDIT] จำนวน Cell ชนกันหลังย้าย: {collisions_remaining} ช่อง (เป้าหมาย: 0)")
    assert collisions_remaining == 0, f"Error: Still {collisions_remaining} collisions!"
    print("    [PASSED 100%] การชนกันทั้งหมดถูกกำจัดเป็น 0 ช่องอย่างสมบูรณ์แบบ!")

    # -------------------------------------------------------------
    # 3. เรนเดอร์ตัวอักษรเดี่ยว Ku 20 ลงใน Font Sheet DDS
    # -------------------------------------------------------------
    print("\n[+] 2. เรนเดอร์ตัวอักษรเดี่ยวลงช่อง Ku 20 (Cells 881..957) ใน DDS...")
    with open(TARGET_DDS, "rb") as f:
        dds_bytes = bytearray(f.read())

    kb_hash_before = get_keyboard_checksum(dds_bytes)
    cfg = load_or_create_config()

    count_rendered = 0
    for thai, kanji in new_mapping.items():
        ku, ten = get_kanji_ku_ten(kanji)
        if ku == 20:
            row, col, cell_idx = jis_to_cell(20, ten)
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
            count_rendered += 1

    print(f"    -> เรนเดอร์และฉีด Ku 20 สำเร็จ: {count_rendered} ช่อง")

    # ยืนยันแป้นพิมพ์ไม่พัง
    kb_hash_after = get_keyboard_checksum(dds_bytes)
    assert kb_hash_before == kb_hash_after, "Error: Keyboard was modified!"
    print("    [PASSED 100%] แป้นพิมพ์ภาษาอังกฤษปลอดภัย 100%")

    with open(TARGET_DDS, "wb") as f:
        f.write(dds_bytes)
    print("    [+] บันทึกไฟล์ DDS เรียบร้อย")

    # -------------------------------------------------------------
    # 4. คอมไพล์ DDS -> G1T -> Entry 55
    # -------------------------------------------------------------
    print("\n[+] 3. คอมไพล์ DDS เป็น G1T ด้วย g1t_tool...")
    cmd = [sys.executable, G1T_TOOL, "import", TEX_DIR, OUT_G1T_DIR]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0, f"g1t_tool error: {res.stderr}"

    out_g1t = os.path.join(OUT_G1T_DIR, "entry_00055.g1t")
    with open(out_g1t, "rb") as f:
        g1t_raw = f.read()
    packed_55 = pack_entry_chunks(g1t_raw)
    print(f"    -> บีบอัด Entry 55 สำเร็จ: {len(packed_55):,} ไบต์")

    # -------------------------------------------------------------
    # 5. จัดการ Entry 36 (บทสนทนา 3 จุด + ประวัติตัวละคร 2 ตัว)
    # -------------------------------------------------------------
    print("\n[+] 4. สร้างและเตรียม Entry 36 ด้วย Mapping ใหม่ (Ku 20)...")
    with open(ATMO_BIN, "rb") as f:
        f.seek(ENTRY_36_START)
        e36 = bytearray(f.read(ENTRY_36_ORIG_SIZE))

    def convert_text_to_codes(thai_text):
        toks = tokenize_formula_949(thai_text)
        res = []
        for t in toks:
            if t == ' ':
                res.append('　')
            elif t in new_mapping:
                res.append(new_mapping[t])
            else:
                res.append(t)
        return ''.join(res)

    # ก) บทสนทนา 3 จุดเดิม
    p1_bytes = convert_text_to_codes("สร้างเซฟ ช่องใด?").encode('utf-8')
    p1_padded = p1_bytes + b'\x00' * (45 - len(p1_bytes))

    p2_bytes = convert_text_to_codes("เลือกตัวเอกที่จะออกผจญภัย\nเลือกชายหรือหญิงก็ได้\nเนื้อเรื่องจะไม่เปลี่ยน").encode('utf-8')
    p2_padded = p2_bytes + b'\x00' * (167 - len(p2_bytes))

    p3_bytes = convert_text_to_codes("ตั้งชื่อลูกพี่ลูกน้อง\nที่จะร่วมผจญภัยไปด้วย").encode('utf-8')
    p3_padded = p3_bytes + b'\x00' * (85 - len(p3_bytes))

    e36[6512 : 6512 + 45] = p1_padded
    e36[6641 : 6641 + 167] = p2_padded
    e36[6849 : 6849 + 85] = p3_padded

    # ข) ประวัติตัวละคร ราเซล และ เทเรเซีย แปลเต็ม 3 บรรทัด
    r_text = (
        "นักเรียนนายร้อย ผู้มีจิตใจรักความยุติธรรม\n"
        "ด้วยความร่าเริงสดใส และความมุ่งมั่นอันเปี่ยมล้น\n"
        "นักดาบหนุ่ม ผู้มุ่งไปข้างหน้าอย่างไม่ย่อท้อ"
    )
    t_text = (
        "นักเรียนนายร้อยสาว ผู้เพียบพร้อมทั้งปัญญาและความงาม\n"
        "คอยชี้นำเพื่อนพ้อง ด้วยความสุขุมเยือกเย็นเสมอ\n"
        "นักดาบหญิง ผู้หนักแน่นและพึ่งพาได้"
    )

    r_codes = convert_text_to_codes(r_text) + '\x00'
    t_codes = convert_text_to_codes(t_text) + '\x00'
    r_bytes = r_codes.encode('utf-8')
    t_bytes = t_codes.encode('utf-8')

    # ล้างช่องเดิม 87136 / 87253
    e36[87136 : 87136 + 117] = b'\x00' * 117
    e36[87253 : 87253 + 108] = b'\x00' * 108

    # Append ต่อท้าย Entry 36
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

    print(f"    -> อัปเดตข้อความใหม่เสร็จสิ้น (ขนาด Entry 36 รวม: {new_entry36_size:,} ไบต์)")

    # -------------------------------------------------------------
    # 6. ฉีดเข้า Atmosphere และ Yuzu
    # -------------------------------------------------------------
    targets = [
        ("Atmosphere Mod (Drive D)", ATMO_BIN, ATMO_IDX),
        ("Yuzu Mod (Drive C)", YUZU_BIN, YUZU_IDX)
    ]

    print("\n[+] 5. ติดตั้ง Font Atlas Entry 55 และ Entry 36 เข้าตัวเกม...")
    for name, bin_path, idx_path in targets:
        if not os.path.exists(bin_path) or not os.path.exists(idx_path):
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

        print(f"        [+] ฉีด Entry 55 + Append Entry 36 + Redirect IDX สำเร็จ!")

    print("\n" + "=" * 80)
    print(" [SUCCESS] แก้ไขปัญหา Font Cell Collisions และติดตั้งสมบูรณ์แบบ 100%!")
    print("=" * 80)

if __name__ == "__main__":
    main()
