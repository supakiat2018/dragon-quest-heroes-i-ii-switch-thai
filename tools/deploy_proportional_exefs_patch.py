"""
deploy_proportional_exefs_patch.py
ระบบสร้างและติดตั้ง ExeFS Proportional Kerning Patch (ARM64 IPS32)
พร้อมฟอนต์ RomFS Left-Aligned สำหรับ Nintendo Switch (Build ID: 5C598E5025BF97BCEC69E67213B48503)

ความสามารถ:
1. เรนเดอร์ 12 เซลล์เมนูหลัก (เริ่มเล่น, สร้างเซฟ, ลบเซฟ) แบบ Proportional (Left-Aligned x=3, Baseline แถว 31)
2. ฉีดลง DDS -> G1T -> LINKDATA.BIN ทั้ง Atmosphere, Yuzu, Ryujinx
3. ตรวจสอบ Checksum คีย์บอร์ดอังกฤษ 166 ตัว (Cells 209-377) ปลอดภัย 100%
4. สร้าง ExeFS IPS32 Patch (5C598E5025BF97BCEC69E67213B48503.ips)
   - Hook จุด 0x0001C628 (NSO offset 0x0001C728)
   - Code Cave ที่ 0x00DC2430 (NSO offset 0x00DC2530)
   - ตรวจสอบ cell_index: ถ้าเป็นตัวอักษรไทย -> คืนค่าความกว้าง Proportional (16.0f - 30.0f)
   - ถ้าเป็นตัวอักษรอื่นในเกม -> คืนค่า 36.0f เท่าเดิม 100% ไม่กระทบภาษาญี่ปุ่น
5. ติดตั้งไฟล์ IPS เข้าโฟลเดอร์ exefs ของ Atmosphere, Yuzu, Ryujinx ครบทุกแพลตฟอร์ม
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
from build_thai_keyboard import encode_cell_dxt5
from deploy_english_keyboard_romfs import pack_entry_chunks

TITLE_ID = "0100CD3000BDC000"
BUILD_ID = "5C598E5025BF97BCEC69E67213B48503"

# RomFS Targets
ATMOS_ROMFS_DIR = os.path.join(BASE_DIR, "mod", "atmosphere", "contents", TITLE_ID, "romfs", "dqh2")
ATMOS_BIN = os.path.join(ATMOS_ROMFS_DIR, "LINKDATA.BIN")
YUZU_MOD_DIR = os.path.expanduser(rf"~\AppData\Roaming\yuzu\load\{TITLE_ID}\MODTHAI")
YUZU_BIN = os.path.join(YUZU_MOD_DIR, "romfs", "dqh2", "LINKDATA.BIN")
RYUJINX_MOD_DIR = os.path.expanduser(rf"~\AppData\Roaming\Ryujinx\sdcard\atmosphere\contents\{TITLE_ID.lower()}\{TITLE_ID}\MODTHAI")
RYUJINX_BIN = os.path.join(RYUJINX_MOD_DIR, "romfs", "dqh2", "LINKDATA.BIN")

# ExeFS IPS Targets
ATMOS_IPS_PATHS = [
    os.path.join(BASE_DIR, "mod", "atmosphere", "contents", TITLE_ID, "exefs", f"{BUILD_ID}.ips"),
    os.path.join(BASE_DIR, "mod", "atmosphere", "exefs_patches", "dqh2_thai", f"{BUILD_ID}.ips"),
]
YUZU_IPS_PATHS = [
    os.path.join(YUZU_MOD_DIR, "exefs", f"{BUILD_ID}.ips"),
]
RYUJINX_IPS_PATHS = [
    os.path.join(RYUJINX_MOD_DIR, "exefs", f"{BUILD_ID}.ips"),
    os.path.expanduser(rf"~\AppData\Roaming\Ryujinx\sdcard\atmosphere\exefs_patches\dqh2_thai\{BUILD_ID}.ips"),
]

f32 = ImageFont.truetype(FONT_TTF, 32)
f_mark = ImageFont.truetype(FONT_TTF, 28)

UPPER_MARKS = set('\u0e31\u0e34\u0e35\u0e36\u0e37\u0e4d')
LOWER_MARKS = set('\u0e38\u0e39\u0e3a')
TONE_MARKS  = set('\u0e48\u0e49\u0e4a\u0e4b\u0e4c\u0e47')

def get_glyph_crop(ch):
    font = f_mark if (ch in UPPER_MARKS or ch in LOWER_MARKS or ch in TONE_MARKS) else f32
    t = Image.new('RGBA', (80, 80), (0, 0, 0, 0))
    if ch in UPPER_MARKS or ch in TONE_MARKS:
        ImageDraw.Draw(t).text((40, 44), ch, font=font, fill=(255, 255, 255, 255), anchor='ms')
    elif ch in LOWER_MARKS:
        ImageDraw.Draw(t).text((40, 76), ch, font=font, fill=(255, 255, 255, 255), anchor='ms')
    else:
        ImageDraw.Draw(t).text((40, 60), ch, font=font, fill=(255, 255, 255, 255), anchor='ms')
    coords = np.argwhere(np.array(t)[:, :, 3] > 20)
    if len(coords) == 0:
        return Image.new('RGBA', (5, 5), (0, 0, 0, 0))
    return t.crop((coords[:, 1].min(), coords[:, 0].min(), coords[:, 1].max() + 1, coords[:, 0].max() + 1))

def render_proportional_cell(ch, baseline=32):
    """
    เรนเดอร์ตัวอักษรแบบ Left-Aligned (x=3) ในช่อง 36x36
    เพื่อให้ Advance Width ใน ExeFS ทำงานได้อย่างสมบูรณ์แบบ
    """
    cell = Image.new('RGBA', (36, 36), (0, 0, 0, 0))
    if ch == 'เริ่':
        cr_e = get_glyph_crop('เ').resize((10, 19), Image.Resampling.LANCZOS)
        cr_r = get_glyph_crop('ร').resize((15, 19), Image.Resampling.LANCZOS)
        cr_i = get_glyph_crop('ิ').resize((15, 6), Image.Resampling.LANCZOS)
        cr_t = get_glyph_crop('่').resize((8, 8), Image.Resampling.LANCZOS)
        cell.paste(cr_e, (3, baseline - 19), cr_e)
        cell.paste(cr_r, (14, baseline - 19), cr_r)
        cell.paste(cr_i, (14, baseline - 19 - 6 - 1), cr_i)
        cell.paste(cr_t, (14 + 15 - 8 - 1, baseline - 19 - 6 - 1 - 8 - 1), cr_t)
        return cell, 27.0
    elif ch == 'เล่':
        cr_e = get_glyph_crop('เ').resize((10, 19), Image.Resampling.LANCZOS)
        cr_l = get_glyph_crop('ล').resize((17, 19), Image.Resampling.LANCZOS)
        cr_t = get_glyph_crop('่').resize((8, 8), Image.Resampling.LANCZOS)
        cell.paste(cr_e, (3, baseline - 19), cr_e)
        cell.paste(cr_l, (14, baseline - 19), cr_l)
        cell.paste(cr_t, (14 + (17 - 8)//2, baseline - 19 - 8 + 2), cr_t)
        return cell, 29.0
    elif ch == 'ร้':
        cr_r = get_glyph_crop('ร').resize((15, 19), Image.Resampling.LANCZOS)
        cr_t = get_glyph_crop('้').resize((9, 9), Image.Resampling.LANCZOS)
        cell.paste(cr_r, (3, baseline - 19), cr_r)
        cell.paste(cr_t, (3 + 15 - 9 - 1, baseline - 19 - 9 + 2), cr_t)
        return cell, 17.0
    elif ch == 'เซ':
        cr_e = get_glyph_crop('เ').resize((10, 19), Image.Resampling.LANCZOS)
        cr_s = get_glyph_crop('ซ').resize((18, 19), Image.Resampling.LANCZOS)
        cell.paste(cr_e, (3, baseline - 19), cr_e)
        cell.paste(cr_s, (14, baseline - 19), cr_s)
        return cell, 30.0
    else:
        cr = get_glyph_crop(ch)
        h = 25 if ch in ['ป', 'ฝ', 'ฟ', 'ฬ'] else (20 if ch in ['ส', 'ศ', 'ฮ'] else 19)
        w = 14 if ch in ['า', 'ะ'] else cr.width
        sc = cr.resize((w, h), Image.Resampling.LANCZOS)
        cell.paste(sc, (3, baseline - h), sc)
        return cell, float(w + 2)

def get_keyboard_checksum(dds_bytes):
    WIDTH_BLOCKS = 1024
    BLOCK_BYTES = 16
    start_off = 128 + (1 * 9 * WIDTH_BLOCKS) * BLOCK_BYTES
    end_off   = 128 + (4 * 9 * WIDTH_BLOCKS) * BLOCK_BYTES
    return hashlib.md5(dds_bytes[start_off:end_off]).hexdigest()

def build_ips_patch(width_table):
    """
    สร้างไฟล์ IPS32 สำหรับ ARM64 Switch
    Hook 0x0001C628 (NSO offset 0x0001C728) -> Jump to Cave 0x00DC2430 (NSO offset 0x00DC2530)
    """
    cave_addr = 0x00DC2430
    hook_site = 0x0001C628

    routine = [
        0x1000016a,  # adr  x10, table (offset 0xdc245c)
        0xb840854b,  # ldr  w11, [x10], #8
        0x340000ab,  # cbz  w11, default (0xdc244c)
        0x6b09017f,  # cmp  w11, w9
        0x54ffffa1,  # b.ne loop (0xdc2434)
        0xb85fc148,  # ldur w8, [x10, #-4]
        0x14000002,  # b    exit (0xdc2450)
        0x52a84208,  # mov  w8, #0x42100000 (36.0f)
        0xb9000849,  # str  w9, [x2, #8]
        0xb9000c48,  # str  w8, [x2, #0xc]
        0xd65f03c0,  # ret
    ]

    cave_words = list(routine)
    for cell_idx, w in width_table:
        w_float_bytes = struct.pack('<f', float(w))
        w_float_u32 = struct.unpack('<I', w_float_bytes)[0]
        cave_words.append(cell_idx)
        cave_words.append(w_float_u32)
    cave_words.append(0)
    cave_words.append(0)

    cave_payload = b''.join(struct.pack('<I', w) for w in cave_words)
    hook_b = struct.pack('<I', 0x14000000 | (((cave_addr - hook_site) >> 2) & 0x03FFFFFF))

    ips = bytearray(b'IPS32')
    # Record 1: Hook at NSO offset 0x0001C728
    ips.extend(struct.pack('>IH', hook_site + 0x100, len(hook_b)))
    ips.extend(hook_b)
    # Record 2: Cave code and table at NSO offset 0x00DC2530
    ips.extend(struct.pack('>IH', cave_addr + 0x100, len(cave_payload)))
    ips.extend(cave_payload)
    ips.extend(b'EEOF')
    return bytes(ips)

def main():
    print("=" * 75)
    print(" [*] ติดตั้งระบบ ExeFS Proportional Kerning Patch + Font RomFS")
    print(f" [*] Target Build ID: {BUILD_ID}")
    print("=" * 75)

    # 1. รายการตัวอักษร 12 ตัว (Cells 505 - 516)
    THAI_CELLS = [
        ('เริ่', 4, 53, 505, '亜'),
        ('ม',   4, 54, 506, '唖'),
        ('เล่', 4, 55, 507, '娃'),
        ('น',   4, 56, 508, '阿'),
        ('ส',   4, 57, 509, '哀'),
        ('ร้',  4, 58, 510, '愛'),
        ('า',   4, 59, 511, '挨'),
        ('ง',   4, 60, 512, '姶'),
        ('เซ',  4, 61, 513, '逢'),
        ('ฟ',   4, 62, 514, '葵'),
        ('ล',   4, 63, 515, '茜'),
        ('บ',   4, 64, 516, '穐'),
    ]

    # โหลด DDS ปัจจุบัน
    with open(TARGET_DDS, "rb") as f:
        dds_bytes = bytearray(f.read())
    kb_hash_before = get_keyboard_checksum(dds_bytes)
    print(f"[+] 1. โหลด DDS สำเร็จ | Checksum คีย์บอร์ดก่อนแก้: {kb_hash_before}")

    width_table = []
    WIDTH_BLOCKS = 1024
    BLOCK_BYTES = 16

    print("\n[+] 2. เรนเดอร์ตัวอักษร Left-Aligned (x=3) และฉีดเข้า DDS...")
    for ch, row, col, cell_id, kanji in THAI_CELLS:
        c_img, adv_w = render_proportional_cell(ch)
        width_table.append((cell_id, adv_w))

        rows_dxt = encode_cell_dxt5(c_img)
        bx0 = (col * 36) // 4
        by0 = (row * 36) // 4
        for by in range(9):
            off = 128 + ((by0 + by) * WIDTH_BLOCKS + bx0) * BLOCK_BYTES
            dds_bytes[off : off + 144] = rows_dxt[by]
        print(f"    -> '{ch:4s}' [Cell {cell_id:3d}] [Kanji: {kanji}] -> Width = {adv_w:4.1f} px")

    with open(TARGET_DDS, "wb") as f:
        f.write(dds_bytes)

    kb_hash_after = get_keyboard_checksum(dds_bytes)
    assert kb_hash_before == kb_hash_after, "Checksum คีย์บอร์ดไม่ตรงกัน!"
    print(f"[+] ตรวจสอบ Checksum คีย์บอร์ดผ่าน 100%: {kb_hash_after}")

    # 3. คอมไพล์ DDS -> G1T
    print("\n[+] 3. คอมไพล์ DDS เป็น G1T...")
    cmd = [sys.executable, G1T_TOOL, "import", TEX_DIR, OUT_G1T_DIR]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0, f"g1t_tool error: {res.stderr}"

    out_g1t = os.path.join(OUT_G1T_DIR, "entry_00055.g1t")
    with open(out_g1t, "rb") as f:
        g1t_raw = f.read()
    packed_55 = pack_entry_chunks(g1t_raw)
    print(f"[+] บีบอัด Entry 55 สำเร็จ: {len(packed_55):,} ไบต์")

    # 4. ฉีดเข้า RomFS LINKDATA.BIN
    targets_bin = [
        ("Atmosphere Mod (Drive D)", ATMOS_BIN),
        ("Yuzu Mod (Drive C)", YUZU_BIN),
        ("Ryujinx Mod (Drive C)", RYUJINX_BIN)
    ]
    ENTRY_55_OFF = 4805120
    ENTRY_36_START = 363008

    p1_bytes = "亜唖娃阿".encode('utf-8') + b'\x00' * 4
    p2_bytes = "哀愛挨姶逢葵".encode('utf-8') + b'\x00' * 7
    p3_bytes = "茜穐逢葵".encode('utf-8') + b'\x00' * 10

    print("\n[+] 4. ฉีดไฟล์ฟอนต์และข้อความเข้า LINKDATA.BIN ทั้ง 3 แพลตฟอร์ม...")
    for name, bin_path in targets_bin:
        if os.path.exists(bin_path):
            with open(bin_path, "r+b") as f:
                f.seek(ENTRY_55_OFF)
                f.write(packed_55)
                f.seek(ENTRY_36_START + 86990)
                f.write(p1_bytes)
                f.seek(ENTRY_36_START + 87006)
                f.write(p2_bytes)
                f.seek(ENTRY_36_START + 87031)
                f.write(p3_bytes)
            print(f"    [+] ติดตั้งสำเร็จ -> {name}")
        else:
            print(f"    [-] ข้าม (ไม่พบไฟล์): {bin_path}")

    # 5. สร้างและติดตั้ง ExeFS IPS32 Patch
    print("\n[+] 5. สร้างไฟล์ ExeFS IPS32 Patch (Proportional Advance Width)...")
    ips_bytes = build_ips_patch(width_table)
    print(f"[+] สร้าง IPS Patch สำเร็จ ({len(ips_bytes)} ไบต์)")

    all_ips_destinations = ATMOS_IPS_PATHS + YUZU_IPS_PATHS + RYUJINX_IPS_PATHS
    print("\n[+] 6. กระจายไฟล์ IPS Patch ไปยังโฟลเดอร์ exefs ทั้งหมด...")
    for p in all_ips_destinations:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "wb") as f:
            f.write(ips_bytes)
        print(f"    [+] บันทึก IPS Patch -> {p}")

    print("\n" + "=" * 75)
    print(" [SUCCESS] เสร็จสมบูรณ์ 100%!")
    print(" - RomFS Font: Left-aligned (x=3) วางระนาบแม่นยำ")
    print(" - ExeFS IPS Patch: Hook font advance width แบบ Proportional ตามตาราง 12 ตัว")
    print(" - ภาษาญี่ปุ่นและคีย์บอร์ดอังกฤษ: คืนค่า 36.0f เต็ม ไม่กระทบเลยแม้แต่นิดเดียว")
    print("=" * 75)

if __name__ == "__main__":
    main()
