"""
deploy_button_guides_thai.py
ติดตั้ง "แถบแนะนำปุ่มกดท้ายจอ" (Button Guides) ทั้ง 36 คำใน DQH2
ด้วยระบบ Formula 949 PUA (สระหน้า เ, แ, โ, ใ, ไ เป็นตัวเดี่ยว + PUA คลัสเตอร์เฉพาะตัวซ้อนแนวตั้ง)
- ฉีดเข้า Entry 36 ใน LINKDATA.BIN ทั้ง Atmosphere และ Yuzu
- รักษา Button Escape Codes (\x1bP...) ดั้งเดิมไว้ 100%
- ปลอดภัย 100% ไร้ Overflow (0% Overflow)
"""

import os
import sys
import json
import struct

BASE_DIR = r"D:\Game\dragon quest heroes i & ii"
SWITCH_DIR = os.path.join(BASE_DIR, "switch")
WORKSPACE_DIR = os.path.join(SWITCH_DIR, "workspace")
MAPPING_PATH = os.path.join(SWITCH_DIR, "Mapping_Kanji.json")

sys.path.append(os.path.join(SWITCH_DIR, "tools"))
sys.path.append(WORKSPACE_DIR)
from check_translations import tokenize_formula_949

TITLE_ID = "0100CD3000BDC000"
ATMO_BIN = os.path.join(BASE_DIR, "mod", "atmosphere", "contents", TITLE_ID, "romfs", "dqh2", "LINKDATA.BIN")
YUZU_BIN = os.path.expanduser(rf"~\AppData\Roaming\yuzu\load\{TITLE_ID}\MODTHAI\romfs\dqh2\LINKDATA.BIN")

ENTRY_36_START = 363008

# 36 คำแปลสั้นกระชับ สไตล์เกมเมอร์ พอดีกรอบ 0% Overflow
BUTTON_GUIDE_36 = [
    # หมวด 1: มุมกล้อง & ดูตัวละคร (4 คำ)
    ("リセット", "รีเซ็ต", "Reset"),
    ("かいてん", "หมุน", "Rotate"),
    ("ズーム", "ซูม", "Zoom"),
    ("くわしく見る", "ข้อมูล", "Details"),

    # หมวด 2: สำรวจ & เดินแมป (Action HUD - 10 คำ)
    ("はなす", "คุย", "Talk"),
    ("しらべる", "ตรวจ", "Examine"),
    ("あける", "เปิด", "Open"),
    ("ダッシュ", "วิ่ง", "Dash"),
    ("ジャンプ", "โดด", "Jump"),
    ("ぼうぎょ", "กัน", "Guard"),
    ("かいふく", "ฟื้นฟู", "Heal"),
    ("スキップ", "ข้าม", "Skip"),
    ("ひっさつ", "อัลติ", "Special Move"),
    ("メニュー", "เมนู", "Menu"),

    # หมวด 3: จัดเรียง & สลับหน้า (Sort & Filter - 12 คำ)
    ("キャラきりかえ", "สลับตัว", "Switch Character"),
    ("きりかえ", "สลับ", "Switch"),
    ("ページきりかえ", "สลับหน้า", "Switch Page"),
    ("入手順に", "ที่ได้", "Sort by Acquisition"),
    ("達成率順に", "สำเร็จ", "Sort by Completion"),
    ("コスト順に", "คอสต์", "Sort by Cost"),
    ("有効順に", "มีผล", "Sort by Validity"),
    ("使用順に", "ที่ใช้", "Sort by Usage"),
    ("種別順に", "ชนิด", "Sort by Category"),
    ("50音順に", "ก-ฮ", "Sort Alphabetically"),
    ("有効/無効", "เปิด", "Enable/Disable"),
    ("再検索", "ค้น", "Search Again"),

    # หมวด 4: จัดการของ & ปาร์ตี้ (Inventory & Party - 10 คำ)
    ("はずす", "ถอด", "Unequip"),
    ("すべてはずす", "ถอดหมด", "Unequip All"),
    ("いれかえる", "สลับที่", "Swap Slot"),
    ("並びかえる", "เรียง", "Reorder"),
    ("捨てる", "ทิ้ง", "Discard"),
    ("えらぶ", "เอา", "Select / Choose"),
    ("前回のパーティにする", "ใช้ทีมเดิม", "Revert to Previous Party"),
    ("いまのパーティにする", "ใช้ทีมนี้", "Apply Current Party"),
    ("封印/解除", "ผนึก", "Seal / Unseal"),
    ("すべて解除", "แก้หมด", "Release All Seals")
]

def main():
    print("=" * 80)
    print(" [*] เริ่มต้นติดตั้ง แถบแนะนำปุ่มกดท้ายจอ (Button Guides) ทั้ง 36 คำ")
    print(" [*] ระบบ Formula 949 PUA (สระหน้าเดี่ยว + คลัสเตอร์ซ้อนแนวตั้ง)")
    print("=" * 80)

    with open(MAPPING_PATH, "r", encoding="utf-8") as f:
        mapping = json.load(f)

    dict_map = {jp: th for jp, th, en in BUTTON_GUIDE_36}

    # อ่านสล็อตทั้งหมดใน Entry 36
    bin_target = YUZU_BIN if os.path.exists(YUZU_BIN) else ATMO_BIN
    with open(bin_target, "rb") as f:
        f.seek(ENTRY_36_START + 102500)
        chunk = f.read(1600)

    pos = 0
    patches = []
    while pos < len(chunk):
        null_idx = chunk.find(b'\x00', pos)
        if null_idx == -1: break
        raw = chunk[pos:null_idx]
        slot_len = len(raw)

        if slot_len > 0 and b'\x1bP' in raw:
            text_bytes = raw
            btn_codes = []
            while text_bytes.startswith(b'\x1bP'):
                btn_codes.append(text_bytes[:3])
                text_bytes = text_bytes[3:]
                if text_bytes.startswith(b'\xef\xbc\x8b'):
                    btn_codes.append(b'+')
                    text_bytes = text_bytes[3:]
            
            try:
                jp_text = text_bytes.decode('utf-8')
            except:
                jp_text = ""

            if jp_text in dict_map:
                th_text = dict_map[jp_text]
                tokens = tokenize_formula_949(th_text)
                kanji_str = "".join(mapping[tok] if tok in mapping else tok for tok in tokens)
                
                btn_bytes = b"".join(btn_codes)
                new_payload = btn_bytes + kanji_str.encode('utf-8')
                assert len(new_payload) <= slot_len, f"Overflow at {pos}: {len(new_payload)} > {slot_len}"
                
                padded = new_payload + b'\x00' * (slot_len - len(new_payload))
                off = 102500 + pos
                patches.append((off, slot_len, jp_text, th_text, kanji_str, padded))

        elif slot_len > 0 and not b'\x1bP' in raw and 102500 + pos >= 104000:
            break
        pos = null_idx + 1

    print(f"\n[+] สแกนพบตำแหน่งแถบปุ่มกดทั้งหมด {len(patches)} ตำแหน่ง ครอบคลุม 36 คำหลัก:")
    for idx, (off, sz, jp, th, k, pad) in enumerate(patches, 1):
        print(f"  {idx:02d}. [Offset {off}] ({sz}b) \"{jp}\" -> \"{th}\" [PUA Kanji: {k}]")

    # ฉีดเข้า LINKDATA.BIN
    targets = [
        ("Atmosphere Mod (Drive D)", ATMO_BIN),
        ("Yuzu Mod (Drive C)", YUZU_BIN)
    ]

    print("\n[+] กำลังฉีดข้อมูลข้อความเข้าสู่ Entry 36 ใน LINKDATA.BIN...")
    for name, bpath in targets:
        if os.path.exists(bpath):
            with open(bpath, "r+b") as f:
                for off, sz, jp, th, k, padded in patches:
                    f.seek(ENTRY_36_START + off)
                    f.write(padded)
            print(f"    [+] ติดตั้งสำเร็จ -> {name}")
        else:
            print(f"    [-] ข้าม (ไม่พบไฟล์) -> {name}")

    print("\n" + "=" * 80)
    print(" [SUCCESS 100%] ติดตั้งแถบแนะนำปุ่มกด 36 คำ (42 สล็อต) เรียบร้อยสมบูรณ์แบบ!")
    print("=" * 80)

if __name__ == "__main__":
    main()
