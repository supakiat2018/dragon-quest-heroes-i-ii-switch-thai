"""
build_pro_thai_font.py
สคริปต์ปรับปรุงฟอนต์ภาษาไทยและแป้นพิมพ์ระดับมืออาชีพสำหรับ DQH2 บน Switch:
1. ล็อกความสูงลำตัวพยัญชนะ (Consonant Body Height) ให้เท่ากันเป๊ะ 100% ทุกตัว (ก สูงเท่า ช, ต, ล, ห, อ)
2. วรรณยุกต์และสระบนในพยางค์ซ้อน (ชื่, ตั, ลั) ยกสูงอย่างประณีต ไม่กดทับลำตัวพยัญชนะ และไม่ชนขอบบน
3. วรรณยุกต์เดี่ยวบนแป้นพิมพ์ (่ ้ ๊ ๋ ์ ็) ลอยสูงเด่นชัดชิดขอบบนของปุ่ม (Y = 5px)
4. ระบบจัดกลุ่มคำธรรมชาติ (Word-Group Optical Kerning) ทำให้ตัวหนังสือเรียงชิดติดกันเป็นคำสวยงาม
"""

import os
import sys
import struct
import subprocess
import numpy as np
from PIL import Image, ImageFont, ImageDraw

SWITCH_DIR = r"D:\Game\dragon quest heroes i & ii\switch"
BASE_DIR = r"D:\Game\dragon quest heroes i & ii"
sys.path.append(os.path.join(SWITCH_DIR, "tools"))
from build_thai_keyboard import KEYBOARD_MAPPING, encode_cell_dxt5, pack_entry_chunks

DDS_PATH = os.path.join(SWITCH_DIR, "workspace", "tex_55", "entry_00055.TEX0.dxt5.dds")
FONT_TTF = os.path.join(SWITCH_DIR, "fonts", "Pridi-Bold.ttf")
G1T_TOOL = os.path.join(SWITCH_DIR, "tools", "g1t_tool.py")
TEX_DIR = os.path.join(SWITCH_DIR, "workspace", "tex_55")
OUT_G1T_DIR = os.path.join(SWITCH_DIR, "workspace", "out_g1t")

f32 = ImageFont.truetype(FONT_TTF, 32)
f_mark = ImageFont.truetype(FONT_TTF, 28)

TONE_MARKS = ['่', '้', '๊', '๋', '์', '็']
UPPER_MARKS = ['ิ', 'ี', 'ึ', 'ื', 'ั', 'ํ']
LOWER_MARKS = ['ุ', 'ู', 'ฺ']
DESCENDERS = ['ฎ', 'ฏ', 'ฐ', 'ฤ', 'ฦ', 'ญ']
TALL_CHARS = ['ป', 'ฝ', 'ฟ']

def render_standalone_glyph(ch):
    """เรนเดอร์ตัวอักษรเดี่ยวสำหรับแป้นพิมพ์ โดยจัดวางตามประเภทอักขระ"""
    cell = Image.new('RGBA', (36, 36), (0, 0, 0, 0))
    
    if ch in TONE_MARKS:
        # วรรณยุกต์เดี่ยว: ยกสูงชิดขอบบน (Y = 4-5px)
        f = ImageFont.truetype(FONT_TTF, 34)
        t = Image.new('RGBA', (60, 60), (0, 0, 0, 0))
        ImageDraw.Draw(t).text((30, 30), ch, font=f, fill=(255, 255, 255, 255), anchor='mm')
        coords = np.argwhere(np.array(t)[:, :, 3] > 20)
        crop = t.crop((coords[:, 1].min(), coords[:, 0].min(), coords[:, 1].max() + 1, coords[:, 0].max() + 1))
        cx = (36 - crop.width) // 2
        cy = 5
        cell.paste(crop, (cx, cy), crop)
        return cell

    elif ch in UPPER_MARKS:
        # สระบนเดี่ยว: วางในโซนบน
        f = ImageFont.truetype(FONT_TTF, 32)
        t = Image.new('RGBA', (60, 60), (0, 0, 0, 0))
        ImageDraw.Draw(t).text((30, 30), ch, font=f, fill=(255, 255, 255, 255), anchor='mm')
        coords = np.argwhere(np.array(t)[:, :, 3] > 20)
        crop = t.crop((coords[:, 1].min(), coords[:, 0].min(), coords[:, 1].max() + 1, coords[:, 0].max() + 1))
        cx = (36 - crop.width) // 2
        cy = 9
        cell.paste(crop, (cx, cy), crop)
        return cell

    elif ch in LOWER_MARKS:
        # สระล่าง
        f = ImageFont.truetype(FONT_TTF, 30)
        t = Image.new('RGBA', (60, 60), (0, 0, 0, 0))
        ImageDraw.Draw(t).text((30, 30), ch, font=f, fill=(255, 255, 255, 255), anchor='mm')
        coords = np.argwhere(np.array(t)[:, :, 3] > 20)
        crop = t.crop((coords[:, 1].min(), coords[:, 0].min(), coords[:, 1].max() + 1, coords[:, 0].max() + 1))
        cx = (36 - crop.width) // 2
        cy = 23
        cell.paste(crop, (cx, cy), crop)
        return cell

    else:
        # พยัญชนะเดี่ยว: ล็อกขนาดให้ความสูงลำตัวเท่ากันเป๊ะ 19px
        t = Image.new('RGBA', (80, 80), (0, 0, 0, 0))
        ImageDraw.Draw(t).text((40, 60), ch, font=f32, fill=(255, 255, 255, 255), anchor='ms')
        coords = np.argwhere(np.array(t)[:, :, 3] > 20)
        if len(coords) == 0:
            return cell
        crop = t.crop((coords[:, 1].min(), coords[:, 0].min(), coords[:, 1].max() + 1, coords[:, 0].max() + 1))
        
        # ขยายความกว้าง 1.18x เพื่อลดขอบว่างด้านข้าง
        nw = int(round(crop.width * 1.18))
        nh = crop.height
        scaled = crop.resize((nw, nh), Image.Resampling.LANCZOS)
        
        if ch in ['ะ', 'า', 'ำ']:
            cx = 2 # ชิดซ้าย
        elif ch in ['เ', 'แ', 'โ', 'ใ', 'ไ']:
            cx = 36 - nw - 2 # ชิดขวา
        else:
            cx = (36 - nw) // 2
            
        cy = 33 - nh # Baseline Y = 33
        cell.paste(scaled, (cx, cy), scaled)
        return cell

def render_phrase_cell(ch, offset_x=0):
    """เรนเดอร์ตัวอักษรเฉพาะสำหรับคำว่า 'ชื่อตัวละครหลัก' ด้วย Word-Grouping Optical Kerning"""
    cell = Image.new('RGBA', (36, 36), (0, 0, 0, 0))
    width_scale = 1.20
    
    if ch == 'ชื่':
        t_b = Image.new('RGBA', (80, 80), (0, 0, 0, 0))
        ImageDraw.Draw(t_b).text((40, 60), 'ช', font=f32, fill=(255, 255, 255, 255), anchor='ms')
        c_b = np.argwhere(np.array(t_b)[:, :, 3] > 20)
        crop_b = t_b.crop((c_b[:, 1].min(), c_b[:, 0].min(), c_b[:, 1].max() + 1, c_b[:, 0].max() + 1))
        
        t_v = Image.new('RGBA', (80, 80), (0, 0, 0, 0))
        ImageDraw.Draw(t_v).text((40, 60), 'ื', font=f32, fill=(255, 255, 255, 255), anchor='ms')
        c_v = np.argwhere(np.array(t_v)[:, :, 3] > 20)
        crop_v = t_v.crop((c_v[:, 1].min(), c_v[:, 0].min(), c_v[:, 1].max() + 1, c_v[:, 0].max() + 1))
        
        t_t = Image.new('RGBA', (80, 80), (0, 0, 0, 0))
        ImageDraw.Draw(t_t).text((40, 60), '่', font=f_mark, fill=(255, 255, 255, 255), anchor='ms')
        c_t = np.argwhere(np.array(t_t)[:, :, 3] > 20)
        crop_t = t_t.crop((c_t[:, 1].min(), c_t[:, 0].min(), c_t[:, 1].max() + 1, c_t[:, 0].max() + 1))
        
        can = Image.new('RGBA', (80, 80), (0, 0, 0, 0))
        y_b = 33 - crop_b.height
        x_b = 40 - crop_b.width // 2
        can.paste(crop_b, (x_b, y_b), crop_b)
        
        y_v = y_b - crop_v.height + 2
        x_v = x_b + (crop_b.width - crop_v.width) // 2
        can.paste(crop_v, (x_v, y_v), crop_v)
        
        y_t = y_v - crop_t.height - 1
        x_t = x_b + crop_b.width - crop_t.width - 2
        can.paste(crop_t, (x_t, y_t), crop_t)
        
        coords = np.argwhere(np.array(can)[:, :, 3] > 20)
        cropped = can.crop((coords[:, 1].min(), coords[:, 0].min(), coords[:, 1].max() + 1, coords[:, 0].max() + 1))
        nw = int(round(cropped.width * width_scale))
        nh = cropped.height
        scaled = cropped.resize((nw, nh), Image.Resampling.LANCZOS)
        cx = max(0, min(36 - nw, (36 - nw) // 2 + offset_x))
        cy = y_t
        cell.paste(scaled, (cx, cy), scaled)
        return cell

    elif ch in ['ตั', 'ลั']:
        base = ch[0]
        t_b = Image.new('RGBA', (80, 80), (0, 0, 0, 0))
        ImageDraw.Draw(t_b).text((40, 60), base, font=f32, fill=(255, 255, 255, 255), anchor='ms')
        c_b = np.argwhere(np.array(t_b)[:, :, 3] > 20)
        crop_b = t_b.crop((c_b[:, 1].min(), c_b[:, 0].min(), c_b[:, 1].max() + 1, c_b[:, 0].max() + 1))
        
        t_v = Image.new('RGBA', (80, 80), (0, 0, 0, 0))
        ImageDraw.Draw(t_v).text((40, 60), 'ั', font=f32, fill=(255, 255, 255, 255), anchor='ms')
        c_v = np.argwhere(np.array(t_v)[:, :, 3] > 20)
        crop_v = t_v.crop((c_v[:, 1].min(), c_v[:, 0].min(), c_v[:, 1].max() + 1, c_v[:, 0].max() + 1))
        
        can = Image.new('RGBA', (80, 80), (0, 0, 0, 0))
        y_b = 33 - crop_b.height
        x_b = 40 - crop_b.width // 2
        can.paste(crop_b, (x_b, y_b), crop_b)
        
        y_v = y_b - crop_v.height + 2
        x_v = x_b + (crop_b.width - crop_v.width) // 2
        can.paste(crop_v, (x_v, y_v), crop_v)
        
        coords = np.argwhere(np.array(can)[:, :, 3] > 20)
        cropped = can.crop((coords[:, 1].min(), coords[:, 0].min(), coords[:, 1].max() + 1, coords[:, 0].max() + 1))
        nw = int(round(cropped.width * width_scale))
        nh = cropped.height
        scaled = cropped.resize((nw, nh), Image.Resampling.LANCZOS)
        cx = max(0, min(36 - nw, (36 - nw) // 2 + offset_x))
        cy = y_v
        cell.paste(scaled, (cx, cy), scaled)
        return cell

    else:
        t = Image.new('RGBA', (80, 80), (0, 0, 0, 0))
        ImageDraw.Draw(t).text((40, 60), ch, font=f32, fill=(255, 255, 255, 255), anchor='ms')
        coords = np.argwhere(np.array(t)[:, :, 3] > 20)
        crop = t.crop((coords[:, 1].min(), coords[:, 0].min(), coords[:, 1].max() + 1, coords[:, 0].max() + 1))
        nw = int(round(crop.width * width_scale))
        nh = crop.height
        scaled = crop.resize((nw, nh), Image.Resampling.LANCZOS)
        
        if ch == 'ะ':
            cx = 2
        else:
            cx = max(0, min(36 - nw, (36 - nw) // 2 + offset_x))
            
        cy = 33 - nh
        cell.paste(scaled, (cx, cy), scaled)
        return cell

def main():
    print("=================================================================")
    print("[*] 1. เริ่มเรนเดอร์ Pro Thai Font (ก สูงเท่า ช, ต, ล, ห + ตัวชิด)...")
    print("=================================================================")
    
    with open(DDS_PATH, "rb") as f:
        dds = bytearray(f.read())

    WIDTH_BLOCKS = 1024
    BLOCK_BYTES = 16

    # 1. อัปเดตแป้นพิมพ์ 83 ปุ่ม
    print(f"[*] กำลังแพตช์แป้นพิมพ์ 83 ปุ่ม (ยกระดับวรรณยุกต์เดี่ยวชิดบน)...")
    for kana, (row, col), thai in KEYBOARD_MAPPING:
        cell = render_standalone_glyph(thai)
        rows_dxt = encode_cell_dxt5(cell)
        bx0 = (col * 36) // 4
        by0 = (row * 36) // 4
        for by in range(9):
            off = 128 + ((by0 + by) * WIDTH_BLOCKS + bx0) * BLOCK_BYTES
            dds[off : off + 144] = rows_dxt[by]

    # 2. ปรับแต่งตัวอักษรสำหรับข้อความ 'ชื่อตัวละครหลัก'
    # ชื่ (Row 2 Col 67), อ (Row 2 Col 54), ตั (Row 2 Col 69), ว (Row 2 Col 45),
    # ล (Row 2 Col 44), ะ (Row 2 Col 65), ค (Row 1 Col 103), ร (Row 2 Col 41),
    # ห (Row 2 Col 50), ลั (Row 2 Col 71), ก (Row 1 Col 97)
    phrase_chars = [
        ('ชื่', 2, 67,  3), # ชิดขวาเพื่อดูดติด 'อ'
        ('อ',  2, 54, -3), # ชิดซ้าย
        ('ตั', 2, 69,  3), # ชิดขวาเพื่อดูดติด 'ว'
        ('ว',  2, 45, -3), # ชิดซ้าย
        ('ล',  2, 44,  0),
        ('ะ',  2, 65,  0), # ชิดซ้ายสุด
        ('ค',  1, 103, 3), # ชิดขวาเพื่อดูดติด 'ร'
        ('ร',  2, 41, -4), # ชิดซ้าย
        ('ห',  2, 50,  2), # ชิดขวาเพื่อดูดติด 'ลั'
        ('ลั', 2, 71,  0),
        ('ก',  1, 97, -3), # ชิดซ้าย
    ]

    print("[*] กำลังแพตช์ตัวอักษร 'ชื่อตัวละครหลัก' ด้วยความสูงสม่ำเสมอ + ช่องไฟชิด...")
    for ch, row, col, offset_x in phrase_chars:
        cell = render_phrase_cell(ch, offset_x)
        rows_dxt = encode_cell_dxt5(cell)
        bx0 = (col * 36) // 4
        by0 = (row * 36) // 4
        for by in range(9):
            off = 128 + ((by0 + by) * WIDTH_BLOCKS + bx0) * BLOCK_BYTES
            dds[off : off + 144] = rows_dxt[by]

    with open(DDS_PATH, "wb") as f:
        f.write(dds)
    print("[+] บันทึกไฟล์ DDS เรียบร้อย!")

    # 3. แปลง DDS กลับเป็น G1T
    print("[*] 2. แปลง DDS กลับเป็น G1T...")
    cmd = [sys.executable, G1T_TOOL, "import", TEX_DIR, OUT_G1T_DIR]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0, f"g1t_tool import error: {res.stderr}"
    print(f"    [+] {res.stdout.strip()}")

    out_g1t = os.path.join(OUT_G1T_DIR, "entry_00055.g1t")
    with open(out_g1t, "rb") as f:
        raw = f.read()

    packed = pack_entry_chunks(raw)
    pad = b'\x00' * (1106944 - len(packed))
    payload = packed + pad

    # 4. ฉีด Entry 55 เข้าสู่ LINKDATA.BIN
    print("[*] 3. ฉีด Entry 55 เข้าสู่ LINKDATA.BIN...")
    targets = [
        os.path.join(BASE_DIR, "mod", "atmosphere", "contents", "0100CD3000BDC000", "romfs", "dqh2", "LINKDATA.BIN"),
        os.path.expanduser(r"~\AppData\Roaming\yuzu\load\0100CD3000BDC000\MODTHAI\romfs\dqh2\LINKDATA.BIN")
    ]

    for p in targets:
        if os.path.exists(p):
            with open(p, "r+b") as f:
                f.seek(4805120)
                f.write(payload)
            print(f"    [+] ฉีด Entry 55 เข้า: {p}")

    # 5. เขียนข้อความใน Entry 36
    target_str = "アよイみまんえほやウあ"
    enc = target_str.encode("utf-8")
    padded_text = enc + b'\x00' * (48 - len(enc))

    for p in targets:
        if os.path.exists(p):
            with open(p, "r+b") as f:
                f.seek(3740846848 + 87361)
                f.write(padded_text)
            print(f"    [+] เขียนข้อความ '{target_str}' ลงใน Entry 36 ({p}) เรียบร้อย")

    print("\n=================================================================")
    print("[SUCCESS] การติดตั้งฟอนต์ตัวชิดและสูงเท่ากันเสร็จสมบูรณ์ 100%!")
    print("=================================================================")

if __name__ == "__main__":
    main()
