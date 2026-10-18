"""
patch_header_text.py
สคริปต์แก้ไขข้อความหัวข้อหน้าตั้งชื่อตัวละคร '主人公の名前を　決めてください。' เป็นภาษาไทย 'ตั้งชื่อตัวเอก'
บน Nintendo Switch / Yuzu (LINKDATA.BIN)
"""

import os
import sys

SWITCH_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(SWITCH_DIR)

TITLE_ID = "0100CD3000BDC000"
MOD_BIN = os.path.join(BASE_DIR, "mod", "atmosphere", "contents", TITLE_ID, "romfs", "dqh2", "LINKDATA.BIN")
YUZU_BIN = os.path.expanduser(r"~\AppData\Roaming\yuzu\load\0100CD3000BDC000\MODTHAI\romfs\dqh2\LINKDATA.BIN")

sys.path.append(os.path.join(SWITCH_DIR, "tools"))
from build_thai_keyboard import KEYBOARD_MAPPING

thai_to_kana = {t: k for k, cell, t in KEYBOARD_MAPPING}
thai_to_kana[' '] = '\u3000'

# Offset ของข้อความใน LINKDATA.BIN
ENTRY_36_OFFSET = 363008
TEXT_OFFSET_IN_E36 = 87361
TARGET_FILE_OFFSET = ENTRY_36_OFFSET + TEXT_OFFSET_IN_E36

ORIGINAL_JP = "主人公の名前を　決めてください。"
ORIGINAL_BYTES = ORIGINAL_JP.encode("utf-8")
SLOT_LEN = len(ORIGINAL_BYTES) # 48 bytes

def encode_thai_to_kana(thai_str):
    res = []
    for c in thai_str:
        if c in thai_to_kana:
            res.append(thai_to_kana[c])
        else:
            res.append(c)
    return ''.join(res)

def patch_file(bin_path, replacement_bytes):
    if not os.path.exists(bin_path):
        print(f"[!] File not found: {bin_path}")
        return False
    
    with open(bin_path, "r+b") as f:
        f.seek(TARGET_FILE_OFFSET)
        curr = f.read(SLOT_LEN)
        if curr != ORIGINAL_BYTES and curr != replacement_bytes:
            print(f"[*] Note: Current content at {TARGET_FILE_OFFSET} is already modified: {curr}")
        
        f.seek(TARGET_FILE_OFFSET)
        f.write(replacement_bytes)
        print(f"[+] Successfully patched: {bin_path}")
    return True

def main():
    thai_text = "ตั้งชื่อตัวหลัก"
    kana_text = encode_thai_to_kana(thai_text)
    encoded_bytes = kana_text.encode("utf-8")
    
    print(f"[*] Thai text: '{thai_text}'")
    print(f"[*] Mapped Kana: '{kana_text}'")
    print(f"[*] Encoded bytes ({len(encoded_bytes)} bytes): {encoded_bytes}")
    
    if len(encoded_bytes) > SLOT_LEN:
        print(f"[ERROR] Text too long! {len(encoded_bytes)} > {SLOT_LEN}")
        sys.exit(1)
        
    # เติม null bytes ให้เท่ากับขนาดเดิม 48 bytes เป๊ะๆ ไม่ให้กระทบข้อความถัดไป
    padded_bytes = encoded_bytes + b'\x00' * (SLOT_LEN - len(encoded_bytes))
    assert len(padded_bytes) == SLOT_LEN
    
    for path in [MOD_BIN, YUZU_BIN]:
        patch_file(path, padded_bytes)
        
    print("[SUCCESS] All files updated successfully!")

if __name__ == "__main__":
    main()
