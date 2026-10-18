"""
test_append_entry.py
ทดสอบเทคนิคการ Append Entry 36 ต่อท้าย LINKDATA.BIN และอัปเดต LINKDATA.IDX
เพื่อให้ตัวเกมโหลดข้อมูลจากท้ายไฟล์แทน โดยไม่ต้องแก้ที่เดิม และเปิดทางให้ขยายความยาวได้ไม่จำกัด
"""

import os
import sys
import struct

SWITCH_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(SWITCH_DIR)

ROMFS_BIN = os.path.join(BASE_DIR, "romfs", "dqh2", "LINKDATA.BIN")
ROMFS_IDX = os.path.join(BASE_DIR, "romfs", "dqh2", "LINKDATA.IDX")

TITLE_ID = "0100CD3000BDC000"
MOD_DIR = os.path.join(BASE_DIR, "mod", "atmosphere", "contents", TITLE_ID, "romfs", "dqh2")
MOD_BIN = os.path.join(MOD_DIR, "LINKDATA.BIN")
MOD_IDX = os.path.join(MOD_DIR, "LINKDATA.IDX")

YUZU_DIR = os.path.expanduser(r"~\AppData\Roaming\yuzu\load\0100CD3000BDC000\MODTHAI\romfs\dqh2")
YUZU_BIN = os.path.join(YUZU_DIR, "LINKDATA.BIN")
YUZU_IDX = os.path.join(YUZU_DIR, "LINKDATA.IDX")

sys.path.append(os.path.join(SWITCH_DIR, "tools"))
from build_thai_keyboard import KEYBOARD_MAPPING

thai_to_kana = {t: k for k, cell, t in KEYBOARD_MAPPING}
thai_to_kana[' '] = '\u3000'

def encode_thai_to_kana(thai_str):
    res = []
    for c in thai_str:
        if c in thai_to_kana:
            res.append(thai_to_kana[c])
        else:
            res.append(c)
    return ''.join(res)

ORIGINAL_JP = "主人公の名前を　決めてください。"
ORIGINAL_BYTES = ORIGINAL_JP.encode("utf-8") # 48 bytes

ENTRY_ID = 36
ENTRY_36_ORIG_OFF = 363008
ENTRY_36_SIZE = 104012
TEXT_OFF_IN_E36 = 87361

ORIG_BIN_SIZE = 3740846848 # ขนาดต้นฉบับ 128-byte aligned พอดี

def main():
    print("[*] 1. อ่านข้อมูล Entry 36 ต้นฉบับที่สะอาดจาก ROMFS...")
    with open(ROMFS_BIN, "rb") as f:
        f.seek(ENTRY_36_ORIG_OFF)
        e36_data = bytearray(f.read(ENTRY_36_SIZE))
    assert len(e36_data) == ENTRY_36_SIZE
    assert e36_data[TEXT_OFF_IN_E36 : TEXT_OFF_IN_E36 + 48] == ORIGINAL_BYTES
    print("[+] ดึงข้อมูล Entry 36 ต้นฉบับสำเร็จ (มีภาษาญี่ปุ่นเดิมเป๊ะ)")

    # 2. แก้ไขข้อความใน Entry 36 เป็นภาษาไทย "ตั้งชื่อตัวหลัก"
    thai_text = "ตั้งชื่อตัวหลัก"
    kana_text = encode_thai_to_kana(thai_text)
    encoded = kana_text.encode("utf-8")
    padded = encoded + b'\x00' * (48 - len(encoded))
    
    e36_modified = bytearray(e36_data)
    e36_modified[TEXT_OFF_IN_E36 : TEXT_OFF_IN_E36 + 48] = padded
    print(f"[+] แก้ไขข้อความใน Buffer Entry 36 ใหม่เรียบร้อย: '{thai_text}' -> '{kana_text}'")

    # 3. จัด Alignment ข้อมูลที่จะ Append ให้ลงตัว 128 bytes
    pad_len = (128 - (len(e36_modified) % 128)) % 128
    append_data = bytes(e36_modified) + b'\x00' * pad_len
    new_entry_offset = ORIG_BIN_SIZE

    print(f"[*] New Entry 36 Offset = {new_entry_offset} (ท้ายไฟล์ LINKDATA.BIN เดิม)")
    print(f"[*] Append data size = {len(append_data)} bytes (รวม padding)")

    # 4. ดำเนินการกับโฟลเดอร์ MOD (Atmosphere) และ YUZU
    targets = [
        ("Atmosphere Mod", MOD_BIN, MOD_IDX),
        ("Yuzu Mod", YUZU_BIN, YUZU_IDX)
    ]

    for name, bin_path, idx_path in targets:
        print(f"\n[*] กำลังดำเนินการกับ {name}...")
        
        # ก) คืนค่าจุดเดิม (363008) ให้กลับเป็นภาษาญี่ปุ่นเดิม 100% เพื่อพิสูจน์ว่าเกมไม่ได้อ่านจากที่เดิมแล้ว!
        with open(bin_path, "r+b") as f:
            f.seek(ENTRY_36_ORIG_OFF + TEXT_OFF_IN_E36)
            f.write(ORIGINAL_BYTES)
            
            # ข) ตัดไฟล์ให้กลับไปที่ขนาดเดิม ORIG_BIN_SIZE ก่อน (กันการ append ซ้ำซ้อน) แล้วเขียนข้อมูลใหม่ต่อท้าย
            f.seek(ORIG_BIN_SIZE)
            f.truncate(ORIG_BIN_SIZE)
            f.seek(ORIG_BIN_SIZE)
            f.write(append_data)
            print(f"    [+] คืนค่าที่เดิม 363,008 เป็นภาษาญี่ปุ่น และ Append ข้อมูลใหม่ที่ {ORIG_BIN_SIZE} สำเร็จ")

        # ค) อัปเดต LINKDATA.IDX ของ Entry 36 ให้ชี้ไปที่ new_entry_offset
        with open(idx_path, "r+b") as f:
            f.seek(ENTRY_ID * 32)
            # โครงสร้าง 32 bytes: Offset (uint64), Size (uint64), ZSize (uint64), ZipFlag (uint64)
            new_idx_entry = struct.pack('<QQQQ', new_entry_offset, ENTRY_36_SIZE, ENTRY_36_SIZE, 0)
            f.write(new_idx_entry)
            print(f"    [+] อัปเดต LINKDATA.IDX Entry 36 ชี้ไปที่ Offset {new_entry_offset} เรียบร้อย!")

    print("\n[SUCCESS] การทดสอบ Append + IDX Redirect สำเร็จสมบูรณ์ 100%!")
    print("[NOTE] จุดเดิม (363,008) ถูกคืนค่าเป็นภาษาญี่ปุ่นเดิมแล้ว")
    print("[NOTE] แต่ตัวเกมจะอ่านข้อมูลภาษาไทยจากท้ายไฟล์แทน ตามที่ LINKDATA.IDX ชี้ไป!")

if __name__ == "__main__":
    main()
