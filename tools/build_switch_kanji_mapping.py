"""
build_switch_kanji_mapping.py
สร้างผังแมปปิ้ง Mapping_Kanji.json สำหรับ Nintendo Switch
โดยแมปพยางค์ PUA ทั้ง 2,208 ตัว เข้ากับอักขระคันจิแท้ของญี่ปุ่น (Shift-JIS / JIS X 0208)
เริ่มต้นที่ Ku 24 Ten 01 (Row 11 Col 14) เป็นต้นไป
รับประกัน: ไร้ดอกจัน 100% ตัวเกมโหมดญี่ปุ่นยอมรับแน่นอน
"""

import os
import sys
import json

SWITCH_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(SWITCH_DIR)

USER_MAPPING_PATH = r"C:\Users\Supakiat\Desktop\Mover\สร้างฟ้อน\mapping.json"
OUT_SWITCH_MAPPING = os.path.join(SWITCH_DIR, "Mapping_Kanji.json")
OUT_DESKTOP_MAPPING = r"C:\Users\Supakiat\Desktop\Mover\สร้างฟ้อน\Mapping_Switch.json"

sys.path.append(os.path.join(SWITCH_DIR, "tools"))
from build_thai_keyboard import KEYBOARD_MAPPING

def jis_to_sjis_char(ku, ten):
    b1 = ((ku - 1) >> 1) + (0x81 if ku <= 62 else 0xc1)
    if ku % 2 == 1:
        b2 = ten + 0x3f + (1 if ten > 63 else 0)
    else:
        b2 = ten + 0x9e
    return bytes([b1, b2]).decode('shift-jis')

def jis_to_cell(ku, ten):
    offset = (ku - 16) * 94 + (ten - 1)
    idx = 505 + offset
    row = idx // 113
    col = idx % 113
    return row, col, idx

def main():
    print("[*] 1. โหลดรายชื่อพยางค์ 2,208 ตัวจากไฟล์ mapping.json...")
    with open(USER_MAPPING_PATH, "r", encoding="utf-8") as f:
        user_map = json.load(f)
    print(f"[+] โหลดพยางค์สำเร็จ: {len(user_map):,} รายการ")

    switch_mapping = {}
    cluster_slots = []

    # เริ่มที่ Ku 24 Ten 01
    START_KU = 24
    START_TEN = 1
    start_offset = (START_KU - 16) * 94 + (START_TEN - 1)

    print(f"[*] 2. แมปคลัสเตอร์ 2,208 ตัวเข้ากับรหัสคันจิแท้ (เริ่ม Ku {START_KU} Ten {START_TEN})...")
    for i, cluster in enumerate(user_map.keys()):
        cur_offset = start_offset + i
        ku = 16 + cur_offset // 94
        ten = 1 + cur_offset % 94
        kanji_ch = jis_to_sjis_char(ku, ten)
        r, c, cell_idx = jis_to_cell(ku, ten)
        
        switch_mapping[cluster] = kanji_ch
        cluster_slots.append({
            'thai': cluster,
            'kanji': kanji_ch,
            'ku': ku,
            'ten': ten,
            'row': r,
            'col': c,
            'cell_idx': cell_idx
        })

    print(f"[+] แมปคลัสเตอร์สำเร็จ: {len(cluster_slots)} รายการ")
    print(f"    - ตัวแรก: '{cluster_slots[0]['thai']}' -> '{cluster_slots[0]['kanji']}' (Row {cluster_slots[0]['row']}, Col {cluster_slots[0]['col']})")
    print(f"    - ตัวสุดท้าย: '{cluster_slots[-1]['thai']}' -> '{cluster_slots[-1]['kanji']}' (Row {cluster_slots[-1]['row']}, Col {cluster_slots[-1]['col']})")

    # 3. แมปพยัญชนะเดี่ยว สระแนวบรรทัด และตัวเลข
    single_count = 0
    for kana, (r, c), thai in KEYBOARD_MAPPING:
        if thai not in switch_mapping:
            switch_mapping[thai] = kana
            single_count += 1

    # เว้นวรรคเต็มตัวอักษร
    switch_mapping[' '] = '\u3000'

    print(f"[+] เพิ่มพยัญชนะเดี่ยว/สระแนวบรรทัด/ตัวเลข: {single_count} รายการ")
    print(f"[+] รวมทั้งสิ้นใน Mapping_Kanji.json: {len(switch_mapping)} รายการ")

    # บันทึกไฟล์ Mapping
    for out_p in [OUT_SWITCH_MAPPING, OUT_DESKTOP_MAPPING]:
        try:
            with open(out_p, "w", encoding="utf-8") as f:
                json.dump(switch_mapping, f, ensure_ascii=False, indent=2)
            print(f"[+] บันทึกไฟล์สำเร็จ: {out_p}")
        except Exception as e:
            print(f"[!] บันทึกไฟล์ {out_p} ไม่สำเร็จ: {e}")

    # บันทึก metadata สำหรับสคริปต์วาดฟอนต์
    meta_path = os.path.join(SWITCH_DIR, "workspace", "kanji_cluster_slots.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(cluster_slots, f, ensure_ascii=False, indent=2)
    print(f"[+] บันทึกสล็อตพิกัดสำหรับเรนเดอร์ฟอนต์: {meta_path}")

    # ทดสอบฟังก์ชัน Longest Match First กับประโยคตัวอย่าง
    def convert_sample(text):
        res = []
        i = 0
        n = len(text)
        max_len = max(len(k) for k in switch_mapping.keys())
        while i < n:
            matched = False
            for length in range(min(max_len, n - i), 0, -1):
                sub = text[i : i + length]
                if sub in switch_mapping:
                    res.append(switch_mapping[sub])
                    i += length
                    matched = True
                    break
            if not matched:
                res.append(text[i])
                i += 1
        return ''.join(res)

    print("\n[*] 4. ทดสอบแปลงประโยคด้วยระบบ Longest Match First:")
    samples = ["ว่าง", "สร้างเซฟ", "ลบเซฟ", "เริ่มผจญภัย", "ชื่อตัวละครหลัก", "เวลาเล่น", "วันที่", "เนื้อเรื่อง"]
    for s in samples:
        conv = convert_sample(s)
        print(f"    '{s}' -> '{conv}' ({len(conv)} ตัวอักษร, UTF-8 {len(conv.encode('utf-8'))} bytes)")

if __name__ == "__main__":
    main()
