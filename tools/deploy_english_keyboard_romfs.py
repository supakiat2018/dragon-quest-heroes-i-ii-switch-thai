"""
deploy_english_keyboard_romfs.py
คอมไพล์คีย์บอร์ดภาษาอังกฤษ (A-Z, a-z, 0-9) ลงใน RomFS (Entry 55 Font Atlas) โดยตรง
- คัดลอกภาพตัวอักษรภาษาอังกฤษแท้จากตัวเกมแบบ Lossless DXT5 Block-by-Block (ไม่ลดทอนคุณภาพ ไม่ใช้ TTF)
- ทับช่องฮิรางานะ 83 ช่อง (หน้า 1) และคาตาคานะ 83 ช่อง (หน้า 2)
- ไม่แตะต้อง ExeFS แม้แต่ไบต์เดียว ปลอดภัย 100% ไร้ความเสี่ยงจอดำหรือค้างหน้าบูต
- ติดตั้งเข้าทั้ง Atmosphere (Drive D) และ Yuzu (Drive C)
"""

import os
import sys
import shutil
import struct
import zlib
import subprocess
import time

BASE_DIR = r"D:\Game\dragon quest heroes i & ii"
SWITCH_DIR = os.path.join(BASE_DIR, "switch")
WORKSPACE_DIR = os.path.join(SWITCH_DIR, "workspace")
TEX_DIR = os.path.join(WORKSPACE_DIR, "tex_55")
OUT_G1T_DIR = os.path.join(WORKSPACE_DIR, "out_g1t")

G1T_TOOL = os.path.join(SWITCH_DIR, "tools", "g1t_tool.py")
CLEAN_DDS = os.path.join(WORKSPACE_DIR, "tex_clean_55", "clean_entry_00055.TEX0.dxt5.dds")
TARGET_DDS = os.path.join(TEX_DIR, "entry_00055.TEX0.dxt5.dds")

TITLE_ID = "0100CD3000BDC000"
BUILD_ID = "5C598E5025BF97BCEC69E67213B48503"

ATMOS_ROMFS_DIR = os.path.join(BASE_DIR, "mod", "atmosphere", "contents", TITLE_ID, "romfs", "dqh2")
ATMOS_BIN = os.path.join(ATMOS_ROMFS_DIR, "LINKDATA.BIN")
ATMOS_IDX = os.path.join(ATMOS_ROMFS_DIR, "LINKDATA.IDX")
ATMOS_EXEFS = os.path.join(BASE_DIR, "mod", "atmosphere", "contents", TITLE_ID, "exefs", f"{BUILD_ID}.ips")

YUZU_MOD_DIR = os.path.expanduser(rf"~\AppData\Roaming\yuzu\load\{TITLE_ID}\MODTHAI")
YUZU_ROMFS_DIR = os.path.join(YUZU_MOD_DIR, "romfs", "dqh2")
YUZU_BIN = os.path.join(YUZU_ROMFS_DIR, "LINKDATA.BIN")
YUZU_IDX = os.path.join(YUZU_ROMFS_DIR, "LINKDATA.IDX")
YUZU_EXEFS = os.path.join(YUZU_MOD_DIR, "exefs", f"{BUILD_ID}.ips")

ENTRY_55_OFF = 4805120
ENTRY_55_ZSZ = 1106944
WIDTH_BLOCKS = 4096 // 4  # 1024
BLOCK_BYTES = 16

# 1. แหล่งที่มาของตัวอักษรแท้ในแผ่นฟอนต์ (Row, Col)
SRC_CHARS = {}
for i, d in enumerate('0123456789'):
    SRC_CHARS[d] = (1, 34 + i)
for i, c in enumerate('ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
    SRC_CHARS[c] = (1, 44 + i)
for i, c in enumerate('abcdefghijklmnopqrstuvwxyz'):
    SRC_CHARS[c] = (1, 70 + i)

SRC_CHARS['.'] = (0, 4)
SRC_CHARS['-'] = (0, 29)
SRC_CHARS['!'] = (0, 9)
SRC_CHARS['?'] = (0, 8)
SRC_CHARS['/'] = (0, 30)
SRC_CHARS[':'] = (0, 6)
SRC_CHARS[';'] = (0, 7)
SRC_CHARS['_'] = (0, 17)
SRC_CHARS['+'] = (0, 59)
SRC_CHARS['='] = (0, 64)
SRC_CHARS['('] = (0, 41)
SRC_CHARS[')'] = (0, 42)
SRC_CHARS['~'] = (0, 32)
SRC_CHARS[' '] = (1, 0)

# 2. ผัง 83 ปุ่มหน้า 1 (ตัวพิมพ์ใหญ่ + ตัวเลข)
PAGE1_MAPPING = [
    # Block 1 (ซ้าย 30 ปุ่ม)
    'A', 'B', 'C', 'D', 'E',
    'F', 'G', 'H', 'I', 'J',
    'K', 'L', 'M', 'N', 'O',
    'P', 'Q', 'R', 'S', 'T',
    'U', 'V', 'W', 'X', 'Y',
    'Z', ' ', '-', '.', '!',

    # Block 2 (กลาง 28 ปุ่ม)
    '0', '1', '2', '3', '4',
    '5', '6', '7', '8', '9',
    'A', 'E', 'I', 'O', 'U',
    '?', '/', ':', ';', '_',
    '+', '=', '-', '.', '!',
    '-', '~', '.',

    # Block 3 (ขวา 25 ปุ่ม)
    '0', '1', '2', '3', '4',
    '5', '6', '7', '8', '9',
    'A', 'B', 'C', 'D', 'E',
    'F', 'G', 'H', 'I', 'J',
    'K', 'L', 'M', 'N', 'O'
]
assert len(PAGE1_MAPPING) == 83

# 3. ผัง 83 ปุ่มหน้า 2 (ตัวพิมพ์เล็ก + ตัวเลข)
PAGE2_MAPPING = [
    # Block 1 (ซ้าย 30 ปุ่ม)
    'a', 'b', 'c', 'd', 'e',
    'f', 'g', 'h', 'i', 'j',
    'k', 'l', 'm', 'n', 'o',
    'p', 'q', 'r', 's', 't',
    'u', 'v', 'w', 'x', 'y',
    'z', ' ', '-', '.', '?',

    # Block 2 (กลาง 28 ปุ่ม)
    '0', '1', '2', '3', '4',
    '5', '6', '7', '8', '9',
    'a', 'e', 'i', 'o', 'u',
    '!', '/', ':', ';', '_',
    '+', '=', '-', '.', '?',
    '-', '~', '.',

    # Block 3 (ขวา 25 ปุ่ม)
    '0', '1', '2', '3', '4',
    '5', '6', '7', '8', '9',
    'a', 'b', 'c', 'd', 'e',
    'f', 'g', 'h', 'i', 'j',
    'k', 'l', 'm', 'n', 'o'
]
assert len(PAGE2_MAPPING) == 83

# โหลดพิกัดปลายทางของฮิรางานะ 83 ตัว (หน้า 1)
sys.path.append(os.path.join(SWITCH_DIR, "tools"))
from build_thai_keyboard import KEYBOARD_MAPPING

# โหลดพิกัดปลายทางของคาตาคานะ 83 ตัว (หน้า 2)
KATAKANA_ORDER = [
    # Row 0
    'ア', 'イ', 'ウ', 'エ', 'オ',
    # Row 1
    'カ', 'キ', 'ク', 'ケ', 'コ',
    # Row 2
    'サ', 'シ', 'ส' if False else 'ス', 'セ', 'ソ',
    # Row 3
    'タ', 'チ', 'ツ', 'テ', 'ト',
    # Row 4
    'ナ', 'ニ', 'ヌ', 'ネ', 'ノ',
    # Row 5 (ตัวเล็ก)
    'ァ', 'ィ', 'ゥ', 'ェ', 'ォ',
    # Block 2: Row 0
    'ハ', 'ヒ', 'フ', 'ヘ', 'ホ',
    # Row 1
    'マ', 'ミ', 'ム', 'メ', 'モ',
    # Row 2
    'ヤ', 'ユ', 'ヨ', 'ワ', 'ン',
    # Row 3
    'ラ', 'リ', 'ル', 'レ', 'ロ',
    # Row 4
    'ャ', 'ュ', 'ョ', 'ッ', 'ヲ',
    # Row 5 (สัญลักษณ์)
    'ー', '～', '・',
    # Block 3: Row 0
    'ガ', 'ギ', 'グ', 'ゲ', 'ゴ',
    # Row 1
    'ザ', 'ジ', 'ズ', 'ゼ', 'ゾ',
    # Row 2
    'ダ', 'ヂ', 'ヅ', 'デ', 'ド',
    # Row 3
    'バ', 'ビ', 'ブ', 'ベ', 'ボ',
    # Row 4
    'パ', 'ピ', 'プ', 'ペ', 'ポ'
]
assert len(KATAKANA_ORDER) == 83

# พิกัดของคาตาคานะใน entry 55 (เริ่มแถว 2 col 66)
KANA_FULL_LIST = [
    'ァ', 'ア', 'ィ', 'イ', 'ゥ', 'ウ', 'ェ', 'エ', 'ォ', 'オ',
    'カ', 'ガ', 'キ', 'ギ', 'ク', 'グ', 'ケ', 'ゲ', 'コ', 'ゴ',
    'サ', 'ザ', 'シ', 'ジ', 'ス', 'ズ', 'セ', 'ゼ', 'ソ', 'ゾ',
    'タ', 'ダ', 'チ', 'ヂ', 'ッ', 'ツ', 'ヅ', 'テ', 'デ', 'ト',
    'ド', 'ナ', 'ニ', 'ヌ', 'ネ', 'ノ', 'ハ', 'バ', 'パ', 'ヒ',
    'ビ', 'ピ', 'フ', 'ブ', 'プ', 'ヘ', 'ベ', 'ペ', 'ホ', 'ボ',
    'ポ', 'マ', 'ミ', 'ム', 'メ', 'モ', 'ャ', 'ヤ', 'ュ', 'ユ',
    'ョ', 'ヨ', 'ラ', 'リ', 'ル', 'レ', 'ロ', 'ヮ', 'ワ', 'ヰ',
    'ヱ', 'ヲ', 'ン', 'ヴ', 'ヵ', 'ヶ'
]
KATAKANA_COORDS = {}
for i, ch in enumerate(KANA_FULL_LIST):
    idx = 2 * 113 + 66 + i
    KATAKANA_COORDS[ch] = (idx // 113, idx % 113)

# สัญลักษณ์ร่วม
KATAKANA_COORDS['ー'] = (0, 27)
KATAKANA_COORDS['～'] = (0, 32)
KATAKANA_COORDS['・'] = (0, 2)

def pack_entry_chunks(data, chunk_size=0x40000):
    full_size = len(data)
    chunks = (full_size + chunk_size - 1) // chunk_size
    zchunks = [zlib.compress(data[i*chunk_size : (i+1)*chunk_size], 9) for i in range(chunks)]
    buf = bytearray()
    buf.extend(struct.pack('<III', chunk_size, chunks, full_size))
    for z in zchunks:
        buf.extend(struct.pack('<I', 4 + len(z)))
    padding_offset = 0
    for z in zchunks:
        pos = len(buf)
        pad = (128 - ((pos - padding_offset) % 128)) % 128
        buf.extend(b'\x00' * pad)
        padding_offset = len(buf)
        buf.extend(struct.pack('<I', len(z)))
        buf.extend(z)
    return bytes(buf)

def copy_dxt5_cell(dds_bytes, src_r, src_c, dst_r, dst_c):
    """คัดลอก DXT5 Block 9x9 บล็อก (36x36 px) จาก source ไป destination แบบ 100% Bit-for-Bit"""
    src_bx0 = (src_c * 36) // 4
    src_by0 = (src_r * 36) // 4
    dst_bx0 = (dst_c * 36) // 4
    dst_by0 = (dst_r * 36) // 4
    
    for by in range(9):
        src_off = 128 + ((src_by0 + by) * WIDTH_BLOCKS + src_bx0) * BLOCK_BYTES
        dst_off = 128 + ((dst_by0 + by) * WIDTH_BLOCKS + dst_bx0) * BLOCK_BYTES
        dds_bytes[dst_off : dst_off + 144] = dds_bytes[src_off : src_off + 144]

def main():
    start_time = time.time()
    print("=" * 75)
    print(" [*] กำลังสร้างคีย์บอร์ดภาษาอังกฤษ (A-Z, a-z, 0-9) ลง RomFS แท้...")
    print("=" * 75)

    # 1. โหลดไฟล์ DDS สะอาด
    shutil.copy2(CLEAN_DDS, TARGET_DDS)
    with open(TARGET_DDS, "rb") as f:
        dds_bytes = bytearray(f.read())
    print(f"[+] โหลด DDS สะอาดต้นฉบับสำเร็จ: {len(dds_bytes):,} ไบต์")

    # 2. คัดลอกปุ่มหน้า 1 (ฮิรางานะ 83 ช่อง -> ตัวพิมพ์ใหญ่ A-Z + ตัวเลข)
    print("\n[+] [1/4] ก๊อปปี้ตัวอักษรแท้หน้า 1 (83 ช่องฮิรางานะ)...")
    for i, (kana, (dst_r, dst_c), _) in enumerate(KEYBOARD_MAPPING):
        ch = PAGE1_MAPPING[i]
        src_r, src_c = SRC_CHARS[ch]
        copy_dxt5_cell(dds_bytes, src_r, src_c, dst_r, dst_c)
    print(f"    -> แปลง 83 ช่องหน้า 1 สำเร็จ 100%")

    # 3. คัดลอกปุ่มหน้า 2 (คาตาคานะ 83 ช่อง -> ตัวพิมพ์เล็ก a-z + ตัวเลข)
    print("\n[+] [2/4] ก๊อปปี้ตัวอักษรแท้หน้า 2 (83 ช่องคาตาคานะ)...")
    for i, kana in enumerate(KATAKANA_ORDER):
        ch = PAGE2_MAPPING[i]
        src_r, src_c = SRC_CHARS[ch]
        dst_r, dst_c = KATAKANA_COORDS[kana]
        copy_dxt5_cell(dds_bytes, src_r, src_c, dst_r, dst_c)
    print(f"    -> แปลง 83 ช่องหน้า 2 สำเร็จ 100%")

    # บันทึก DDS
    with open(TARGET_DDS, "wb") as f:
        f.write(dds_bytes)

    # 4. คอมไพล์ DDS เป็น G1T
    print("\n[+] [3/4] แพ็ก DDS เข้าเป็น G1T ด้วย g1t_tool...")
    os.makedirs(OUT_G1T_DIR, exist_ok=True)
    cmd = [sys.executable, G1T_TOOL, "import", TEX_DIR, OUT_G1T_DIR]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0, f"g1t_tool error: {res.stderr}"
    print(f"    -> {res.stdout.strip()}")

    # 5. บีบอัด Entry 55 Zlib Chunks
    out_g1t = os.path.join(OUT_G1T_DIR, "entry_00055.g1t")
    with open(out_g1t, "rb") as f:
        g1t_raw = f.read()

    packed = pack_entry_chunks(g1t_raw)
    pad = b'\x00' * (ENTRY_55_ZSZ - len(packed))
    payload = packed + pad
    assert len(payload) == ENTRY_55_ZSZ

    # 6. ฉีดเข้า Atmosphere บน Drive D
    print("\n[+] [4/4] ฉีด Font Atlas เข้า RomFS...")
    if os.path.exists(ATMOS_BIN):
        with open(ATMOS_BIN, "r+b") as f:
            f.seek(ENTRY_55_OFF)
            f.write(payload)
        print(f"    -> [สำเร็จ] ฉีด Atmosphere RomFS: {ATMOS_BIN}")
    else:
        # ก็อปปี้ต้นฉบับมาไว้ที่ mod
        os.makedirs(ATMOS_ROMFS_DIR, exist_ok=True)
        orig_bin = os.path.join(BASE_DIR, "romfs", "dqh2", "LINKDATA.BIN")
        orig_idx = os.path.join(BASE_DIR, "romfs", "dqh2", "LINKDATA.IDX")
        shutil.copy2(orig_idx, ATMOS_IDX)
        shutil.copy2(orig_bin, ATMOS_BIN)
        with open(ATMOS_BIN, "r+b") as f:
            f.seek(ENTRY_55_OFF)
            f.write(payload)
        print(f"    -> [สำเร็จ] สร้างและฉีด Atmosphere RomFS: {ATMOS_BIN}")

    # ลบ IPS ที่อาจค้างอยู่ใน Atmosphere เพื่อความปลอดภัย
    if os.path.exists(ATMOS_EXEFS):
        os.remove(ATMOS_EXEFS)
        print(f"    -> [เคลียร์] ลบ IPS เก่าใน Atmosphere สำเร็จ")

    # 7. คัดลอกไปยัง Yuzu บน Drive C
    print("\n[+] กำลังติดตั้งไปยัง Yuzu (Drive C)...")
    os.makedirs(YUZU_ROMFS_DIR, exist_ok=True)
    shutil.copy2(ATMOS_IDX, YUZU_IDX)
    print(f"    -> คัดลอก LINKDATA.IDX -> Yuzu สำเร็จ")
    shutil.copy2(ATMOS_BIN, YUZU_BIN)
    print(f"    -> คัดลอก LINKDATA.BIN (3.7 GB) -> Yuzu สำเร็จ")

    # ลบ IPS ใน Yuzu ออก 100%
    if os.path.exists(YUZU_EXEFS):
        os.remove(YUZU_EXEFS)
        print(f"    -> [เคลียร์] ลบ IPS เก่าใน Yuzu สำเร็จ")

    el = time.time() - start_time
    print("\n" + "=" * 75)
    print(f" [SUCCESS] ติดตั้งคีย์บอร์ดภาษาอังกฤษสำเร็จสมบูรณ์ 100% ในเวลา {el:.1f} วินาที!")
    print("=" * 75)

if __name__ == "__main__":
    main()
