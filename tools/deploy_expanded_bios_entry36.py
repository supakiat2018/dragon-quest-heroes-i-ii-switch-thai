"""
deploy_expanded_bios_entry36.py
ขยาย Entry 36 ต่อท้าย LINKDATA.BIN และอัปเดต LINKDATA.IDX
ใส่คำแปลประวัติตัวละคร ราเซล (Razel) และ เทเรเซีย (Teresia) ฉบับเต็ม 3 บรรทัด
โดยไม่จำกัดความยาว ไม่ทับข้อความเดิม และคงสภาพเมนู/แถบปุ่มกดทั้งหมด 100%
"""

import os
import sys
import json
import struct

BASE_DIR = r"D:\Game\dragon quest heroes i & ii"
SWITCH_DIR = os.path.join(BASE_DIR, "switch")
TITLE_ID = "0100CD3000BDC000"

ATMO_DIR = os.path.join(BASE_DIR, "mod", "atmosphere", "contents", TITLE_ID, "romfs", "dqh2")
ATMO_BIN = os.path.join(ATMO_DIR, "LINKDATA.BIN")
ATMO_IDX = os.path.join(ATMO_DIR, "LINKDATA.IDX")

YUZU_DIR = os.path.expanduser(rf"~\AppData\Roaming\yuzu\load\{TITLE_ID}\MODTHAI\romfs\dqh2")
YUZU_BIN = os.path.join(YUZU_DIR, "LINKDATA.BIN")
YUZU_IDX = os.path.join(YUZU_DIR, "LINKDATA.IDX")

MAPPING_PATH = os.path.join(SWITCH_DIR, "Mapping_Kanji.json")

sys.path.append(os.path.join(SWITCH_DIR, "workspace"))
from check_translations import tokenize_formula_949

ORIG_BIN_SIZE = 3740846848 # 128-byte aligned
ENTRY_36_START = 363008
ENTRY_36_ORIG_SIZE = 104012

def main():
    print("=" * 75)
    print(" [*] เริ่มต้น Deploy ขยาย Entry 36 ต่อท้าย LINKDATA.BIN + Repoint IDX...")
    print("=" * 75)

    with open(MAPPING_PATH, "r", encoding="utf-8") as f:
        mapping = json.load(f)

    # 1. เตรียมข้อความแปลภาษาไทยฉบับเต็มสมบูรณ์ 3 บรรทัด
    texts = {
        'razel': [
            'นักเรียนนายร้อย ผู้มีจิตใจรักความยุติธรรม',
            'ด้วยความร่าเริงสดใส และความมุ่งมั่นอันเปี่ยมล้น',
            'นักดาบหนุ่ม ผู้มุ่งไปข้างหน้าอย่างไม่ย่อท้อ'
        ],
        'teresia': [
            'นักเรียนนายร้อยสาว ผู้เพียบพร้อมทั้งปัญญาและความงาม',
            'คอยชี้นำเพื่อนพ้อง ด้วยความสุขุมเยือกเย็นเสมอ',
            'นักดาบหญิง ผู้หนักแน่นและพึ่งพาได้'
        ]
    }

    def to_kanji_block(lines):
        out_lines = []
        for l in lines:
            toks = tokenize_formula_949(l)
            kline = ''.join('　' if t == ' ' else mapping.get(t, t) for t in toks)
            out_lines.append(kline)
        return '\n'.join(out_lines) + '\x00'

    r_kanji = to_kanji_block(texts['razel'])
    t_kanji = to_kanji_block(texts['teresia'])

    r_bytes = r_kanji.encode('utf-8')
    t_bytes = t_kanji.encode('utf-8')

    print(f"[+] 1. เตรียมข้อความสำเร็จ:")
    print(f"    - Razel ({len(r_bytes)} bytes): {r_kanji[:30]}...")
    print(f"    - Teresia ({len(t_bytes)} bytes): {t_kanji[:30]}...")

    # 2. อ่าน Entry 36 เดิมจาก ATMO_BIN (มีเมนู แถบปุ่มกด และบทสนทนาที่แปลไว้แล้วครบถ้วน)
    with open(ATMO_BIN, "rb") as f:
        f.seek(ENTRY_36_START)
        e36 = bytearray(f.read(ENTRY_36_ORIG_SIZE))

    print(f"[+] 2. อ่าน Entry 36 เดิมสำเร็จ: {len(e36)} ไบต์")

    # 3. ล้างช่องเดิมที่เคยทดสอบย่อคำไว้ (87136 และ 87253) ให้เป็น null bytes สะอาดตา
    e36[87136 : 87136 + 117] = b'\x00' * 117
    e36[87253 : 87253 + 108] = b'\x00' * 108

    # 4. นำข้อความใหม่ไป Append ต่อท้ายสุดของ Entry 36
    # จัดตำแหน่งให้เริ่มที่ 4-byte aligned
    pad_r = (4 - (len(e36) % 4)) % 4
    e36.extend(b'\x00' * pad_r)
    new_r_off = len(e36)
    e36.extend(r_bytes)

    pad_t = (4 - (len(e36) % 4)) % 4
    e36.extend(b'\x00' * pad_t)
    new_t_off = len(e36)
    e36.extend(t_bytes)

    # 5. อัปเดตตาราง Pointer ใน Entry 36
    # Offset 4144 -> Razel (ptr value = new_r_off - 32)
    # Offset 4148 -> Teresia (ptr value = new_t_off - 32)
    ptr_r = new_r_off - 32
    ptr_t = new_t_off - 32
    struct.pack_into('<I', e36, 4144, ptr_r)
    struct.pack_into('<I', e36, 4148, ptr_t)

    print(f"[+] 3. อัปเดต Pointer สำเร็จ:")
    print(f"    - Ptr 4144 -> {ptr_r} (Absolute: {new_r_off})")
    print(f"    - Ptr 4148 -> {ptr_t} (Absolute: {new_t_off})")

    # 6. อัปเดตขนาดข้อมูลใน Header ของ Entry 36
    new_unpadded_size = len(e36)
    struct.pack_into('<I', e36, 8, new_unpadded_size - 14)
    struct.pack_into('<I', e36, 16, new_unpadded_size - 14)

    # 7. จัด Alignment ท้าย Entry 36 ให้ลงตัว 128 bytes (สำหรับ LINKDATA.BIN)
    pad_128 = (128 - (len(e36) % 128)) % 128
    e36.extend(b'\x00' * pad_128)
    new_entry_size = len(e36)
    print(f"[+] 4. ขนาด Entry 36 ใหม่หลัง Append + 128-byte Pad: {new_entry_size:,} ไบต์ (เดิม {ENTRY_36_ORIG_SIZE:,} ไบต์)")

    # 8. ฉีดเข้าทั้ง Atmosphere และ Yuzu
    targets = [
        ("Atmosphere Mod (Drive D)", ATMO_BIN, ATMO_IDX),
        ("Yuzu Mod (Drive C)", YUZU_BIN, YUZU_IDX)
    ]

    for name, bin_path, idx_path in targets:
        if not os.path.exists(bin_path) or not os.path.exists(idx_path):
            print(f"[-] ไม่พบไฟล์สำหรับ {name} ข้าม...")
            continue

        print(f"\n[*] กำลังติดตั้งลงใน {name}...")
        
        # ก) Append Entry 36 เข้าท้ายไฟล์ LINKDATA.BIN ที่ ORIG_BIN_SIZE
        with open(bin_path, "r+b") as f:
            f.seek(ORIG_BIN_SIZE)
            f.truncate(ORIG_BIN_SIZE)
            f.seek(ORIG_BIN_SIZE)
            f.write(e36)
            print(f"    [+] Append ข้อมูล {new_entry_size:,} ไบต์ ที่ตำแหน่ง {ORIG_BIN_SIZE:,} สำเร็จ")

        # ข) อัปเดต LINKDATA.IDX Entry 36 ชี้ไปที่ ORIG_BIN_SIZE
        with open(idx_path, "r+b") as f:
            f.seek(36 * 32)
            idx_record = struct.pack('<QQQQ', ORIG_BIN_SIZE, new_entry_size, new_entry_size, 0)
            f.write(idx_record)
            print(f"    [+] อัปเดต LINKDATA.IDX Entry 36 ชี้ไปที่ Offset {ORIG_BIN_SIZE:,} (Size {new_entry_size:,}) สำเร็จ")

    print("\n" + "=" * 75)
    print(" [SUCCESS] Deploy คำแปลเต็มสมบูรณ์ 3 บรรทัดด้วยวิธี Append + Redirect สำเร็จ 100%!")
    print("=" * 75)

if __name__ == "__main__":
    main()
