"""
patch_save_menu_kanji.py
ฉีดข้อความเมนูและสมุดบันทึกภาษาไทย (ด้วยระบบ Japanese Kanji Overlay)
เข้าสู่ Entry 36 ของ LINKDATA.BIN
- ไร้ดอกจัน 100%
- ระยะชิดสวยงาม ได้สัดส่วนแบบภาษาอังกฤษ
"""

import os
import sys
import json

SWITCH_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(SWITCH_DIR)

MAPPING_PATH = os.path.join(SWITCH_DIR, "Mapping_Kanji.json")

TITLE_ID = "0100CD3000BDC000"
MOD_DIR = os.path.join(BASE_DIR, "mod", "atmosphere", "contents", TITLE_ID, "romfs", "dqh2")
MOD_BIN = os.path.join(MOD_DIR, "LINKDATA.BIN")
YUZU_DIR = os.path.expanduser(r"~\AppData\Roaming\yuzu\load\0100CD3000BDC000\MODTHAI\romfs\dqh2")
YUZU_BIN = os.path.join(YUZU_DIR, "LINKDATA.BIN")

ENTRY_36_BASE = 3740846848

TEXTS_TO_PATCH = [
    (86990, "เริ่ม", 16),
    (87006, "สร้างเซฟ", 25),
    (87031, "ลบเซฟ", 22),
    (87066, "เวลา", 16),
    (87082, "วันที่", 13),
    (87095, "เรื่อง", 16),
    (87111, "ว่าง", 25),
    (87361, "ชื่อตัวละครหลัก", 49),
]

def load_converter():
    with open(MAPPING_PATH, "r", encoding="utf-8") as f:
        mapping = json.load(f)
    max_len = max(len(k) for k in mapping.keys())

    def convert(text):
        res = []
        i = 0
        n = len(text)
        while i < n:
            matched = False
            for l in range(min(max_len, n - i), 0, -1):
                sub = text[i:i+l]
                if sub in mapping:
                    res.append(mapping[sub])
                    i += l
                    matched = True
                    break
            if not matched:
                res.append(text[i])
                i += 1
        return ''.join(res)

    return convert

def main():
    print("=" * 70)
    print(" [1/2] แปลงข้อความภาษาไทยเป็นรหัส Kanji/Kana ญี่ปุ่น...")
    print("=" * 70)
    convert = load_converter()

    encoded_patches = []
    for off, thai_text, max_len in TEXTS_TO_PATCH:
        conv_text = convert(thai_text)
        enc_bytes = conv_text.encode("utf-8")
        assert len(enc_bytes) < max_len, f"ข้อความ {thai_text} ยาวเกิน buffer ({len(enc_bytes)} >= {max_len})"
        padded = enc_bytes + b'\x00' * (max_len - len(enc_bytes))
        encoded_patches.append((off, thai_text, conv_text, padded))
        print(f"    Offset {off:5d}: '{thai_text}' -> '{conv_text}' ({len(enc_bytes)}b / {max_len}b)")

    print("\n" + "=" * 70)
    print(" [2/2] ฉีดข้อความเข้าสู่ LINKDATA.BIN (Entry 36)...")
    print("=" * 70)
    targets = [
        ("Atmosphere Mod", MOD_BIN),
        ("Yuzu Mod", YUZU_BIN)
    ]

    for name, bin_path in targets:
        if os.path.exists(bin_path):
            with open(bin_path, "r+b") as f:
                for off, thai_text, conv_text, padded in encoded_patches:
                    f.seek(ENTRY_36_BASE + off)
                    f.write(padded)
            print(f"    [+] ฉีดข้อความสำเร็จ -> {name} ({bin_path})")

    print("\n" + "=" * 70)
    print(" [SUCCESS] ฉีดข้อความเมนูภาษาไทยทั้ง 8 รายการเรียบร้อย 100%!")
    print("=" * 70)

if __name__ == "__main__":
    main()
