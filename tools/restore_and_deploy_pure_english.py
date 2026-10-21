"""
restore_and_deploy_pure_english.py
- คืนค่าตัวอักษรและข้อความทั้งหมดในเกมกลับเป็นภาษาญี่ปุ่นแท้ 100% (Clean Japanese Text)
- ใส่เฉพาะคีย์บอร์ดภาษาอังกฤษ 166 ตัวอักษรแท้ (Cells 209-377) ลง RomFS Font Atlas (Entry 55)
- ลบ ExeFS IPS Patch ออกทั้งหมด 100% ทั่วทุก Mod Directory (Yuzu, Atmosphere, Ryujinx)
- ทำงานแบบ In-Place รวดเร็ว เสร็จสมบูรณ์ภายในไม่กี่วินาที
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

ORIG_ROMFS_BIN = os.path.join(BASE_DIR, "romfs", "dqh2", "LINKDATA.BIN")
ORIG_ROMFS_IDX = os.path.join(BASE_DIR, "romfs", "dqh2", "LINKDATA.IDX")

ENTRY_36_OFF = 363008
ENTRY_36_SZ  = 104012
ENTRY_55_OFF = 4805120
ENTRY_55_ZSZ = 1106944
ORIG_BIN_SZ  = 3740846848
ORIG_IDX_SZ  = 330688

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
    'ア', 'イ', 'ウ', 'エ', 'オ',
    'カ', 'キ', 'ク', 'ケ', 'コ',
    'サ', 'シ', 'ス', 'セ', 'ソ',
    'タ', 'チ', 'ツ', 'テ', 'ト',
    'ナ', 'ニ', 'ヌ', 'ネ', 'ノ',
    'ァ', 'ィ', 'ゥ', 'ェ', 'ォ',
    'ハ', 'ヒ', 'フ', 'ヘ', 'ホ',
    'マ', 'ミ', 'ム', 'メ', 'モ',
    'ヤ', 'ユ', 'ヨ', 'ワ', 'ン',
    'ラ', 'リ', 'ル', 'レ', 'ロ',
    'ャ', 'ュ', 'ョ', 'ッ', 'ヲ',
    'ー', '～', '・',
    'ガ', 'ギ', 'グ', 'ゲ', 'ゴ',
    'ザ', 'ジ', 'ズ', 'ゼ', 'ゾ',
    'ダ', 'ヂ', 'ヅ', 'デ', 'ド',
    'バ', 'ビ', 'ブ', 'ベ', 'ボ',
    'パ', 'ピ', 'プ', 'ペ', 'ポ'
]
assert len(KATAKANA_ORDER) == 83

KANA_FULL_LIST = [
    'ァ', 'ア', 'ィ', 'イ', 'ゥ', 'ウ', 'ェ', 'エ', 'ォ', 'オ',
    'カ', 'ガ', 'キ', 'ギ', 'ク', 'グ', 'ケ', 'ゲ', 'コ', 'ゴ',
    'サ', 'ザ', 'シ', 'ジ', 'ส', 'ズ', 'セ', 'ゼ', 'ソ', 'ゾ',
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

KATAKANA_COORDS['ス'] = KATAKANA_COORDS['ส']
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
    src_bx0 = (src_c * 36) // 4
    src_by0 = (src_r * 36) // 4
    dst_bx0 = (dst_c * 36) // 4
    dst_by0 = (dst_r * 36) // 4
    
    for by in range(9):
        src_off = 128 + ((src_by0 + by) * WIDTH_BLOCKS + src_bx0) * BLOCK_BYTES
        dst_off = 128 + ((dst_by0 + by) * WIDTH_BLOCKS + dst_bx0) * BLOCK_BYTES
        dds_bytes[dst_off : dst_off + 144] = dds_bytes[src_off : src_off + 144]

def build_pure_english_entry_55():
    print("[1/4] สร้างแผ่น Font Atlas Entry 55 (เฉพาะคีย์บอร์ดอังกฤษ 166 ปุ่ม)...")
    shutil.copy2(CLEAN_DDS, TARGET_DDS)
    with open(TARGET_DDS, "rb") as f:
        dds_bytes = bytearray(f.read())

    # หน้า 1
    for i, (kana, (dst_r, dst_c), _) in enumerate(KEYBOARD_MAPPING):
        ch = PAGE1_MAPPING[i]
        src_r, src_c = SRC_CHARS[ch]
        copy_dxt5_cell(dds_bytes, src_r, src_c, dst_r, dst_c)

    # หน้า 2
    for i, kana in enumerate(KATAKANA_ORDER):
        ch = PAGE2_MAPPING[i]
        src_r, src_c = SRC_CHARS[ch]
        dst_r, dst_c = KATAKANA_COORDS[kana]
        copy_dxt5_cell(dds_bytes, src_r, src_c, dst_r, dst_c)

    with open(TARGET_DDS, "wb") as f:
        f.write(dds_bytes)

    os.makedirs(OUT_G1T_DIR, exist_ok=True)
    cmd = [sys.executable, G1T_TOOL, "import", TEX_DIR, OUT_G1T_DIR]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0, f"g1t_tool error: {res.stderr}"

    out_g1t = os.path.join(OUT_G1T_DIR, "entry_00055.g1t")
    with open(out_g1t, "rb") as f:
        g1t_raw = f.read()

    packed = pack_entry_chunks(g1t_raw)
    pad = b'\x00' * (ENTRY_55_ZSZ - len(packed))
    payload = packed + pad
    assert len(payload) == ENTRY_55_ZSZ, f"Invalid payload size: {len(payload)}"
    print(f"      Entry 55 สร้างสำเร็จ ขนาด {len(payload):,} ไบต์")
    return payload

def main():
    t0 = time.time()
    print("=" * 80)
    print(" [*] DQH2 PURE JAPANESE + 166 ENGLISH KEYBOARD DEPLOYER")
    print("=" * 80)

    # อ่านข้อมูลต้นฉบับ Entry 36 และ IDX
    print("[+] กำลังอ่านไฟล์ข้อความและดัชนีต้นฉบับภาษาญี่ปุ่น...")
    with open(ORIG_ROMFS_BIN, "rb") as f:
        f.seek(ENTRY_36_OFF)
        orig_entry_36 = f.read(ENTRY_36_SZ)
    assert len(orig_entry_36) == ENTRY_36_SZ

    with open(ORIG_ROMFS_IDX, "rb") as f:
        orig_idx = f.read()
    assert len(orig_idx) == ORIG_IDX_SZ
    print("    -> ข้อมูลภาษาญี่ปุ่นต้นฉบับพร้อม")

    # สร้าง Entry 55
    entry_55_payload = build_pure_english_entry_55()

    # รายการเป้าหมาย
    targets = [
        {
            "name": "Atmosphere (Drive D)",
            "bin": os.path.join(BASE_DIR, "mod", "atmosphere", "contents", "0100CD3000BDC000", "romfs", "dqh2", "LINKDATA.BIN"),
            "idx": os.path.join(BASE_DIR, "mod", "atmosphere", "contents", "0100CD3000BDC000", "romfs", "dqh2", "LINKDATA.IDX"),
            "exefs": os.path.join(BASE_DIR, "mod", "atmosphere", "contents", "0100CD3000BDC000", "exefs")
        },
        {
            "name": "Yuzu (Drive C)",
            "bin": os.path.expanduser(r"~\AppData\Roaming\yuzu\load\0100CD3000BDC000\MODTHAI\romfs\dqh2\LINKDATA.BIN"),
            "idx": os.path.expanduser(r"~\AppData\Roaming\yuzu\load\0100CD3000BDC000\MODTHAI\romfs\dqh2\LINKDATA.IDX"),
            "exefs": os.path.expanduser(r"~\AppData\Roaming\yuzu\load\0100CD3000BDC000\MODTHAI\exefs")
        },
        {
            "name": "Ryujinx Mods (Drive C)",
            "bin": os.path.expanduser(r"~\AppData\Roaming\Ryujinx\mods\contents\0100cd3000bdc000\MODTHAI\romfs\dqh2\LINKDATA.BIN"),
            "idx": os.path.expanduser(r"~\AppData\Roaming\Ryujinx\mods\contents\0100cd3000bdc000\MODTHAI\romfs\dqh2\LINKDATA.IDX"),
            "exefs": os.path.expanduser(r"~\AppData\Roaming\Ryujinx\mods\contents\0100cd3000bdc000\MODTHAI\exefs")
        },
        {
            "name": "Ryujinx SDCard (Drive C)",
            "bin": os.path.expanduser(r"~\AppData\Roaming\Ryujinx\sdcard\atmosphere\contents\0100cd3000bdc000\romfs\dqh2\LINKDATA.BIN"),
            "idx": os.path.expanduser(r"~\AppData\Roaming\Ryujinx\sdcard\atmosphere\contents\0100cd3000bdc000\romfs\dqh2\LINKDATA.IDX"),
            "exefs": os.path.expanduser(r"~\AppData\Roaming\Ryujinx\sdcard\atmosphere\contents\0100cd3000bdc000\exefs")
        }
    ]

    print("\n[+] กำลังปรับปรุงข้อมูลและติดตั้งเข้าเป้าหมายทั้งหมด...")
    for t in targets:
        name = t["name"]
        bin_path = t["bin"]
        idx_path = t["idx"]
        exefs_dir = t["exefs"]

        if not os.path.exists(bin_path):
            print(f"    [-] ข้าม {name}: ไม่พบไฟล์ {bin_path}")
            continue

        print(f"\n    [*] ปรับปรุง: {name}")
        
        # 1. เขียน Entry 36 (ภาษาญี่ปุ่นแท้) และ Entry 55 (คีย์บอร์ดอังกฤษ) ลง BIN
        with open(bin_path, "r+b") as f:
            f.seek(ENTRY_36_OFF)
            f.write(orig_entry_36)
            f.seek(ENTRY_55_OFF)
            f.write(entry_55_payload)
            f.truncate(ORIG_BIN_SZ)
        print(f"        -> คืนค่า Entry 36 (ญี่ปุ่นแท้) + ฉีด Entry 55 (คีย์บอร์ดอังกฤษ) + ตัดขนาดกลับเป็น {ORIG_BIN_SZ:,} ไบต์")

        # 2. เขียน IDX แท้กลับคืน
        with open(idx_path, "wb") as f:
            f.write(orig_idx)
        print(f"        -> คืนค่า LINKDATA.IDX สำเร็จ")

        # 3. ลบไฟล์ IPS ในโฟลเดอร์ ExeFS
        if os.path.exists(exefs_dir):
            removed_ips = 0
            for item in os.listdir(exefs_dir):
                item_path = os.path.join(exefs_dir, item)
                if os.path.isfile(item_path):
                    os.remove(item_path)
                    removed_ips += 1
            print(f"        -> ล้างโฟลเดอร์ ExeFS สะอาด 100% (ลบ {removed_ips} ไฟล์)")

    el = time.time() - t0
    print("\n" + "=" * 80)
    print(f" [SUCCESS] ทุกเป้าหมายอัปเดตเสร็จสมบูรณ์เรียบร้อย 100% ในเวลา {el:.2f} วินาที!")
    print("=" * 80)

if __name__ == "__main__":
    main()
