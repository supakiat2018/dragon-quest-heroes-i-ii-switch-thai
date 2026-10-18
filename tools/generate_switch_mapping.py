"""
generate_switch_mapping.py
สร้างไฟล์ Mapping.json สำหรับ Dragon Quest Heroes II บน Nintendo Switch โดยเฉพาะ
- พยางค์สำเร็จรูป (Clusters) 2,208 ตัว -> แปลงเป็นอักขระ Hangul (ช่วง Cell 987 เป็นต้นไป ใน Entry 55/57)
- พยัญชนะเดี่ยว สระแนวบรรทัด ตัวเลข และเครื่องหมาย 83 ตัว -> แปลงเป็นอักขระ Kana (ตามผังคีย์บอร์ดในเกม)
- รองรับการใช้งานร่วมกับ csv_to_pua_gui.py ได้ทันที 100%
"""

import os
import sys
import json

SWITCH_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(SWITCH_DIR)

USER_MAPPING_PATH = r"C:\Users\Supakiat\Desktop\Mover\สร้างฟ้อน\mapping.json"
OUT_SWITCH_MAPPING = os.path.join(SWITCH_DIR, "Mapping.json")
OUT_DESKTOP_MAPPING = r"C:\Users\Supakiat\Desktop\Mover\สร้างฟ้อน\Mapping_Switch.json"

sys.path.append(os.path.join(SWITCH_DIR, "tools"))
from build_thai_keyboard import KEYBOARD_MAPPING

def main():
    print("[*] 1. โหลดรายชื่อพยางค์ 2,208 ตัวจากไฟล์ mapping.json เดิม...")
    with open(USER_MAPPING_PATH, "r", encoding="utf-8") as f:
        user_map = json.load(f)
    print(f"[+] โหลดพยางค์สำเร็จ: {len(user_map):,} รายการ")

    # 2. อ่านอักขระ Hangul ใน Entry 57 ของ Switch
    e57_path = os.path.join(SWITCH_DIR, "workspace", "entry_00057.bin")
    if not os.path.exists(e57_path):
        romfs_bin = os.path.join(BASE_DIR, "romfs", "dqh2", "LINKDATA.BIN")
        with open(romfs_bin, "rb") as f:
            f.seek(5966080)
            e57_data = f.read(13348)
    else:
        with open(e57_path, "rb") as f:
            e57_data = f.read()

    entries = [e57_data[i*4:(i+1)*4] for i in range(len(e57_data)//4)]
    
    hangul_slots = []
    for idx in range(987, len(entries)):
        raw = entries[idx]
        no_null = raw.rstrip(b'\x00')
        u8 = bytes(reversed(no_null))
        ch = u8.decode('utf-8', errors='ignore')
        hangul_slots.append((idx, ch))

    print(f"[+] ช่องอักขระ Hangul ที่พร้อมใช้งานใน Switch: {len(hangul_slots)} ช่อง (เริ่มจาก Cell 987)")
    assert len(user_map) <= len(hangul_slots), "Error: พยางค์มีจำนวนมากกว่าช่องที่มี!"

    switch_mapping = {}

    # ก) แมปพยางค์สำเร็จรูป (Clusters) เข้ากับอักขระ Hangul ใน Cell 987 เป็นต้นไป
    for i, thai_cluster in enumerate(user_map.keys()):
        cell_idx, target_ch = hangul_slots[i]
        switch_mapping[thai_cluster] = target_ch

    print(f"[+] สร้างแมปพยางค์สำเร็จรูป (ความยาว 2-3 ตัวอักษร): {len(switch_mapping)} รายการ")

    # ข) แมปพยัญชนะเดี่ยว สระแนวบรรทัด ตัวเลข และเครื่องหมาย (ความยาว 1 ตัวอักษร)
    single_count = 0
    for kana, cell, thai in KEYBOARD_MAPPING:
        # ถ้ายังไม่มีในแมป (เป็นตัวเดี่ยว) ให้ใส่เข้าไป
        if thai not in switch_mapping:
            switch_mapping[thai] = kana
            single_count += 1

    # เว้นวรรค
    switch_mapping[' '] = '\u3000' # ช่องว่างเต็มตัวอักษรของญี่ปุ่น

    print(f"[+] เพิ่มพยัญชนะเดี่ยว สระแนวบรรทัด ตัวเลข และเครื่องหมาย: {single_count} รายการ")
    print(f"[+] รวมทั้งสิ้นใน Mapping.json ของ Switch: {len(switch_mapping)} รายการ")

    # 3. บันทึกไฟล์ Mapping.json
    for out_p in [OUT_SWITCH_MAPPING, OUT_DESKTOP_MAPPING]:
        try:
            with open(out_p, "w", encoding="utf-8") as f:
                json.dump(switch_mapping, f, ensure_ascii=False, indent=2)
            print(f"[+] บันทึกไฟล์สำเร็จ: {out_p}")
        except Exception as e:
            print(f"[!] บันทึกไฟล์ {out_p} ไม่สำเร็จ: {e}")

    # 4. ทดสอบฟังก์ชัน Longest Match First กับประโยคตัวอย่าง
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

    test_sentences = [
        "ชื่อตัวละครหลัก",
        "กรุณาตั้งชื่อตัวละคร",
        "เริ่มต้นการผจญภัยในโลกแห่งมังกร",
        "ดาบเพลิงศักดิ์สิทธิ์ ระดับ 99",
        "น้ำมนต์ศักดิ์สิทธิ์ ฟื้นฟู HP 500"
    ]

    print("\n================== ตัวอย่างการแปลงข้อความ ==================")
    for s in test_sentences:
        conv = convert_sample(s)
        print(f"ข้อความ: {s}")
        print(f"ผลลัพธ์: {conv}")
        print(f"จำนวนตัวอักษร: {len(s)} -> {len(conv)} ช่อง")
        print("----------------------------------------------------------")

if __name__ == "__main__":
    main()
