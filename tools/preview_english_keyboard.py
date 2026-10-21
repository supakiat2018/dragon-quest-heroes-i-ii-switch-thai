"""
preview_english_keyboard.py
สร้างภาพพรีวิวคีย์บอร์ด 83 ปุ่มหน้า 1 และ 83 ปุ่มหน้า 2
เพื่อตรวจสอบว่าตำแหน่งตัวอักษรและสัญลักษณ์ถูกต้อง 100% ก่อนแพ็กเข้าเกม
"""

import os
from PIL import Image

BASE_DIR = r"D:\Game\dragon quest heroes i & ii"
WORKSPACE_DIR = os.path.join(BASE_DIR, "switch", "workspace")
CLEAN_DDS = os.path.join(WORKSPACE_DIR, "tex_clean_55", "clean_entry_00055.TEX0.dxt5.dds")

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
    # Block 1 (ซ้าย 30 ปุ่ม: 5 คอลัมน์ x 6 แถว)
    'A', 'B', 'C', 'D', 'E',
    'F', 'G', 'H', 'I', 'J',
    'K', 'L', 'M', 'N', 'O',
    'P', 'Q', 'R', 'S', 'T',
    'U', 'V', 'W', 'X', 'Y',
    'Z', ' ', '-', '.', '!',

    # Block 2 (กลาง 28 ปุ่ม: 5 คอลัมน์ x 5 แถว + 3 ปุ่มล่าง)
    '0', '1', '2', '3', '4',
    '5', '6', '7', '8', '9',
    'A', 'E', 'I', 'O', 'U',
    '?', '/', ':', ';', '_',
    '+', '=', '-', '.', '!',
    '-', '~', '.',

    # Block 3 (ขวา 25 ปุ่ม: 5 คอลัมน์ x 5 แถว)
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

def create_preview():
    img = Image.open(CLEAN_DDS)
    
    def render_page(mapping, title):
        page_img = Image.new('RGBA', (17 * 36, 6 * 36 + 20), (20, 25, 35, 255))
        
        # Block 1 (ซ้าย Col 0..4)
        for i in range(30):
            r = i // 5
            c = i % 5
            ch = mapping[i]
            sr, sc = SRC_CHARS[ch]
            cell = img.crop((sc * 36, sr * 36, (sc + 1) * 36, (sr + 1) * 36))
            page_img.paste(cell, (c * 36, 10 + r * 36), mask=cell)
            
        # Block 2 (กลาง Col 6..10)
        for i in range(28):
            ch = mapping[30 + i]
            sr, sc = SRC_CHARS[ch]
            cell = img.crop((sc * 36, sr * 36, (sc + 1) * 36, (sr + 1) * 36))
            if i < 25:
                r = i // 5
                c = 6 + (i % 5)
            else:
                r = 5
                c = 6 + (i - 25)
            page_img.paste(cell, (c * 36, 10 + r * 36), mask=cell)
            
        # Block 3 (ขวา Col 12..16)
        for i in range(25):
            r = i // 5
            c = 12 + (i % 5)
            ch = mapping[58 + i]
            sr, sc = SRC_CHARS[ch]
            cell = img.crop((sc * 36, sr * 36, (sc + 1) * 36, (sr + 1) * 36))
            page_img.paste(cell, (c * 36, 10 + r * 36), mask=cell)
            
        return page_img

    p1_img = render_page(PAGE1_MAPPING, "PAGE 1")
    p2_img = render_page(PAGE2_MAPPING, "PAGE 2")
    
    total = Image.new('RGBA', (17 * 36, (6 * 36 + 20) * 2 + 10), (10, 10, 15, 255))
    total.paste(p1_img, (0, 0))
    total.paste(p2_img, (0, 6 * 36 + 20 + 10))
    
    out_preview = r"C:\Users\Supakiat\.gemini\antigravity\brain\ab5bc3db-774b-46d7-96ba-65470fc9eb39\english_keyboard_preview.png"
    total.save(out_preview)
    print(f"[+] บันทึกภาพพรีวิวคีย์บอร์ดสำเร็จ: {out_preview}")

if __name__ == "__main__":
    create_preview()
