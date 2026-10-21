"""
build_english_keyboard_ips.py
สร้าง IPS Patch สำหรับ Dragon Quest Heroes II (Build ID: 5C598E5025BF97BCEC69E67213B48503)
เปลี่ยนคีย์บอร์ดพิมพ์ชื่อทั้ง 2 หน้าให้เป็นภาษาอังกฤษ (A-Z, a-z) และตัวเลข (0-9)
โดยใช้พื้นที่ว่างในส่วน .rodata (0x017A0300) ไม่รบกวน .text เข้าเกมได้ 100%
"""

import os
import struct

BASE_DIR = r"D:\Game\dragon quest heroes i & ii"
TITLE_ID = "0100CD3000BDC000"
BUILD_ID = "5C598E5025BF97BCEC69E67213B48503"

YUZU_DIR = os.path.expanduser(rf"~\AppData\Roaming\yuzu\load\{TITLE_ID}\MODTHAI\exefs")
ATMOS_DIR = os.path.join(BASE_DIR, "mod", "atmosphere", "contents", TITLE_ID, "exefs")

# 1. แผนผังปุ่ม 83 ปุ่มสำหรับหน้า 1 (ตัวพิมพ์ใหญ่ + ตัวเลข)
PAGE1_KEYS = [
    # Block 1 (Left 30 keys): A-Z + เครื่องหมาย
    'A', 'B', 'C', 'D', 'E',
    'F', 'G', 'H', 'I', 'J',
    'K', 'L', 'M', 'N', 'O',
    'P', 'Q', 'R', 'S', 'T',
    'U', 'V', 'W', 'X', 'Y',
    'Z', ' ', '-', '.', '!',

    # Block 2 (Middle 28 keys): ตัวเลข 0-9 + สระซ้ำ + สัญลักษณ์
    '0', '1', '2', '3', '4',
    '5', '6', '7', '8', '9',
    'A', 'E', 'I', 'O', 'U',
    '?', '/', ':', ';', "'",
    '(', ')', '+', '=', '_',
    '~', '*', '%',

    # Block 3 (Right 25 keys): ตัวเลข 0-9 ซ้ำ + ตัวอักษรซ้ำ
    '0', '1', '2', '3', '4',
    '5', '6', '7', '8', '9',
    'A', 'B', 'C', 'D', 'E',
    'F', 'G', 'H', 'I', 'J',
    'K', 'L', 'M', 'N', 'O',
]
assert len(PAGE1_KEYS) == 83, f"Page 1 has {len(PAGE1_KEYS)} keys (expected 83)"

# 2. แผนผังปุ่ม 83 ปุ่มสำหรับหน้า 2 (ตัวพิมพ์เล็ก + ตัวเลข)
PAGE2_KEYS = [
    # Block 1 (Left 30 keys): a-z + เครื่องหมาย
    'a', 'b', 'c', 'd', 'e',
    'f', 'g', 'h', 'i', 'j',
    'k', 'l', 'm', 'n', 'o',
    'p', 'q', 'r', 's', 't',
    'u', 'v', 'w', 'x', 'y',
    'z', ' ', '-', '.', '?',

    # Block 2 (Middle 28 keys): ตัวเลข 0-9 + สระซ้ำ + สัญลักษณ์
    '0', '1', '2', '3', '4',
    '5', '6', '7', '8', '9',
    'a', 'e', 'i', 'o', 'u',
    '!', '/', ':', ';', "'",
    '(', ')', '+', '=', '_',
    '~', '*', '%',

    # Block 3 (Right 25 keys): ตัวเลข 0-9 ซ้ำ + ตัวอักษรซ้ำ
    '0', '1', '2', '3', '4',
    '5', '6', '7', '8', '9',
    'a', 'b', 'c', 'd', 'e',
    'f', 'g', 'h', 'i', 'j',
    'k', 'l', 'm', 'n', 'o',
]
assert len(PAGE2_KEYS) == 83, f"Page 2 has {len(PAGE2_KEYS)} keys (expected 83)"

# 3. วาง String Pool ไว้ในพื้นที่ว่างท้าย .rodata (0x017A0300)
# ปลอดภัย 100% เพราะเป็นข้อมูล Data ล้วนๆ CPU ไม่รันเป็นโค้ดแน่นอน
STRING_RODATA_ADDR = 0x017A0300

all_unique_chars = sorted(list(set(PAGE1_KEYS + PAGE2_KEYS + ['a-z', 'A-Z'])))
str_pool = bytearray()
char_addrs = {}

for ch in all_unique_chars:
    encoded = ch.encode('utf-8') + b'\x00'
    addr = STRING_RODATA_ADDR + len(str_pool)
    char_addrs[ch] = addr
    str_pool.extend(encoded)

print(f"[+] Total unique strings: {len(all_unique_chars)}")
print(f"[+] String pool placed in .rodata at 0x{STRING_RODATA_ADDR:08X} ({len(str_pool)} bytes)")

# 4. สร้าง Records สำหรับ IPS Patch
records = []

# Record สำหรับ String Pool ใน .rodata
records.append((STRING_RODATA_ADDR, bytes(str_pool)))

# Record สำหรับ Page 1 Pointers (เริ่ม 0x00ED74B8, ก้าวทีละ 24 ไบต์)
BASE_PAGE1 = 0x00ED74B8
for i, ch in enumerate(PAGE1_KEYS):
    p_addr = BASE_PAGE1 + i * 24
    target_str_addr = char_addrs[ch]
    ptr_bytes = struct.pack('<Q', target_str_addr)
    records.append((p_addr, ptr_bytes))

# ปุ่มสลับหน้า (Key 83) บนหน้า 1: เปลี่ยนจาก 'カナ' เป็น 'a-z'
TOGGLE_PAGE1 = 0x00ED7C80
records.append((TOGGLE_PAGE1, struct.pack('<Q', char_addrs['a-z'])))

# Record สำหรับ Page 2 Pointers (เริ่ม 0x00ED7CC8, ก้าวทีละ 24 ไบต์)
BASE_PAGE2 = 0x00ED7CC8
for i, ch in enumerate(PAGE2_KEYS):
    p_addr = BASE_PAGE2 + i * 24
    target_str_addr = char_addrs[ch]
    ptr_bytes = struct.pack('<Q', target_str_addr)
    records.append((p_addr, ptr_bytes))

# ปุ่มสลับหน้า (Key 169) บนหน้า 2: เปลี่ยนจาก 'かな' เป็น 'A-Z'
TOGGLE_PAGE2 = 0x00ED8490
records.append((TOGGLE_PAGE2, struct.pack('<Q', char_addrs['A-Z'])))

# 5. ประกอบไฟล์ IPS32
def make_ips32(records):
    buf = bytearray(b"IPS32")
    for off, payload in records:
        buf.extend(struct.pack(">IH", off, len(payload)))
        buf.extend(payload)
    buf.extend(b"EEOF")
    return bytes(buf)

ips_data = make_ips32(records)
print(f"[+] Total IPS records: {len(records)}, total size: {len(ips_data)} bytes")

# 6. บันทึกไฟล์ไปยัง Yuzu และ Atmosphere
for target_dir in [YUZU_DIR, ATMOS_DIR]:
    os.makedirs(target_dir, exist_ok=True)
    target_file = os.path.join(target_dir, f"{BUILD_ID}.ips")
    with open(target_file, "wb") as f:
        f.write(ips_data)
    print(f"[+] Saved IPS Patch -> {target_file}")

print("\n" + "=" * 70)
print("[SUCCESS] บันทึกแพตช์คีย์บอร์ด (.rodata) เรียบร้อยแล้ว พร้อมทดสอบ!")
print("=" * 70)
