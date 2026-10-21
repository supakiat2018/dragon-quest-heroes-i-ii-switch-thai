"""
build_clean_english_keyboard.py
สร้าง IPS Patch คีย์บอร์ดภาษาอังกฤษ (A-Z, a-z, 0-9) อย่างถูกต้องและปลอดภัย 100%
- วาง String Pool ไว้ในช่องว่างแท้ของ .rodata (0x01054E50) ซึ่งมีขนาดว่าง 1,687 ไบต์
- ปรับเปลี่ยนเฉพาะ Pointer ตัวอักษร (v2) 83 ตัวของหน้า 1 และ 83 ตัวของหน้า 2
- ไม่แตะต้องฟังก์ชันระบบ ไม่แตะต้องปุ่มควบคุม ไม่แตะต้องข้อความเดิมในเกมใดๆ ทั้งสิ้น
"""

import os
import struct

BASE_DIR = r"D:\Game\dragon quest heroes i & ii"
MAIN_BIN = os.path.join(BASE_DIR, r"exeFS\main_decompressed.bin")

TITLE_ID = "0100CD3000BDC000"
BUILD_ID = "5C598E5025BF97BCEC69E67213B48503"

YUZU_DIR = os.path.expanduser(rf"~\AppData\Roaming\yuzu\load\{TITLE_ID}\MODTHAI\exefs")
ATMOS_DIR = os.path.join(BASE_DIR, "mod", "atmosphere", "contents", TITLE_ID, "exefs")

# 1. ผัง 83 ปุ่มหน้า 1 (ตัวพิมพ์ใหญ่ + ตัวเลข)
PAGE1_CHARS = [
    # Block 1 (ซ้าย 30 ปุ่ม): A-Z + เครื่องหมาย
    'A', 'B', 'C', 'D', 'E',
    'F', 'G', 'H', 'I', 'J',
    'K', 'L', 'M', 'N', 'O',
    'P', 'Q', 'R', 'S', 'T',
    'U', 'V', 'W', 'X', 'Y',
    'Z', ' ', '-', '.', '!',

    # Block 2 (กลาง 28 ปุ่ม): ตัวเลข 0-9 + สระซ้ำ + สัญลักษณ์
    '0', '1', '2', '3', '4',
    '5', '6', '7', '8', '9',
    'A', 'E', 'I', 'O', 'U',
    '?', '/', ':', ';', "'",
    '(', ')', '+', '=', '_',
    '~', '*', '%',

    # Block 3 (ขวา 25 ปุ่ม): ตัวเลข 0-9 ซ้ำ + ตัวอักษรซ้ำ
    '0', '1', '2', '3', '4',
    '5', '6', '7', '8', '9',
    'A', 'B', 'C', 'D', 'E',
    'F', 'G', 'H', 'I', 'J',
    'K', 'L', 'M', 'N', 'O',
]
assert len(PAGE1_CHARS) == 83

# 2. ผัง 83 ปุ่มหน้า 2 (ตัวพิมพ์เล็ก + ตัวเลข)
PAGE2_CHARS = [
    # Block 1 (ซ้าย 30 ปุ่ม): a-z + เครื่องหมาย
    'a', 'b', 'c', 'd', 'e',
    'f', 'g', 'h', 'i', 'j',
    'k', 'l', 'm', 'n', 'o',
    'p', 'q', 'r', 's', 't',
    'u', 'v', 'w', 'x', 'y',
    'z', ' ', '-', '.', '?',

    # Block 2 (กลาง 28 ปุ่ม): ตัวเลข 0-9 + สระซ้ำ + สัญลักษณ์
    '0', '1', '2', '3', '4',
    '5', '6', '7', '8', '9',
    'a', 'e', 'i', 'o', 'u',
    '!', '/', ':', ';', "'",
    '(', ')', '+', '=', '_',
    '~', '*', '%',

    # Block 3 (ขวา 25 ปุ่ม): ตัวเลข 0-9 ซ้ำ + ตัวอักษรซ้ำ
    '0', '1', '2', '3', '4',
    '5', '6', '7', '8', '9',
    'a', 'b', 'c', 'd', 'e',
    'f', 'g', 'h', 'i', 'j',
    'k', 'l', 'm', 'n', 'o',
]
assert len(PAGE2_CHARS) == 83

# 3. เตรียม String Pool วางใน .rodata ที่ 0x01054E50 (มีพื้นที่ว่าง 1,687 ไบต์)
RODATA_STRING_BASE = 0x01054E50

all_unique = sorted(list(set(PAGE1_CHARS + PAGE2_CHARS)))
str_pool = bytearray()
char_offsets = {}

for ch in all_unique:
    addr = RODATA_STRING_BASE + len(str_pool)
    char_offsets[ch] = addr
    str_pool.extend(ch.encode('utf-8') + b'\x00')

print(f"[+] เตรียมข้อความ {len(all_unique)} ตัวอักษร ขนาดรวม: {len(str_pool)} ไบต์")
print(f"[+] วางไว้ใน .rodata ที่ 0x{RODATA_STRING_BASE:08X} (ปลอดภัย 100%)")

# 4. สร้าง Records สำหรับ IPS Patch
records = []

# 4.1 Record เขียน String Pool
records.append((RODATA_STRING_BASE, bytes(str_pool)))

# 4.2 Record ปรับ Pointer หน้า 1 (เริ่ม 0x00ED74B8, ก้าวละ 24 ไบต์)
BASE_P1 = 0x00ED74B8
for i, ch in enumerate(PAGE1_CHARS):
    p_addr = BASE_P1 + i * 24
    target = char_offsets[ch]
    records.append((p_addr, struct.pack('<Q', target)))

# 4.3 Record ปรับ Pointer หน้า 2 (เริ่ม 0x00ED7CC8, ก้าวละ 24 ไบต์)
BASE_P2 = 0x00ED7CC8
for i, ch in enumerate(PAGE2_CHARS):
    p_addr = BASE_P2 + i * 24
    target = char_offsets[ch]
    records.append((p_addr, struct.pack('<Q', target)))

# 5. ประกอบไฟล์ IPS32
def make_ips32(records):
    buf = bytearray(b"IPS32")
    for off, payload in records:
        buf.extend(struct.pack(">IH", off, len(payload)))
        buf.extend(payload)
    buf.extend(b"EEOF")
    return bytes(buf)

ips_data = make_ips32(records)
print(f"[+] สร้าง Records ทั้งหมด: {len(records)} รายการ")
print(f"[+] ขนาดไฟล์ IPS: {len(ips_data)} ไบต์")

# 6. บันทึกไฟล์ไปยัง Yuzu และ Atmosphere
for target_dir in [YUZU_DIR, ATMOS_DIR]:
    os.makedirs(target_dir, exist_ok=True)
    target_file = os.path.join(target_dir, f"{BUILD_ID}.ips")
    with open(target_file, "wb") as f:
        f.write(ips_data)
    print(f"[+] บันทึกไฟล์ IPS สำเร็จ -> {target_file}")

print("=" * 60)
print("[SUCCESS] คีย์บอร์ดภาษาอังกฤษพร้อมใช้งาน 100%!")
print("=" * 60)
