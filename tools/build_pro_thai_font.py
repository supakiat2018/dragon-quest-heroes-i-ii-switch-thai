"""
build_pro_thai_font.py
สคริปต์สร้าง Pro Thai Font (Ultra-Tight Edition):
1. ขยายความกว้างตัวอักษร 1.32x ให้ตัวหนาอวบอิ่มเต็มเซลล์ 30px เทียบเท่าตัวอักษรญี่ปุ่นเดิม
2. เพิ่มแรงดึงกลุ่มคำ (Word-Group Optical Kerning) ดึงตัวอักษรในคำเดียวกันเข้าหากันสนิท
3. ล็อกความสูงลำตัวพยัญชนะ (Consonant Body Height) ให้เท่ากัน 100% ทุกตัว
4. ฉีดเข้า Atmosphere Mod และ Yuzu ทันที
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

WIDTH_SCALE = 1.32 # ขยายความกว้างให้อิ่มเต็มช่อง

def render_standalone_glyph(ch):
    cell = Image.new('RGBA', (36, 36), (0, 0, 0, 0))
    
    if ch in TONE_MARKS:
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
        t = Image.new('RGBA', (80, 80), (0, 0, 0, 0))
        ImageDraw.Draw(t).text((40, 60), ch, font=f32, fill=(255, 255, 255, 255), anchor='ms')
        coords = np.argwhere(np.array(t)[:, :, 3] > 20)
        if len(coords) == 0:
            return cell
        crop = t.crop((coords[:, 1].min(), coords[:, 0].min(), coords[:, 1].max() + 1, coords[:, 0].max() + 1))
        
        nw = int(round(crop.width * WIDTH_SCALE))
        nh = crop.height
        scaled = crop.resize((nw, nh), Image.Resampling.LANCZOS)
        
        if ch in ['ะ', 'า', 'ำ']:
            cx = 1
        elif ch in ['เ', 'แ', 'โ', 'ใ', 'ไ']:
            cx = 36 - nw - 1
        else:
            cx = (36 - nw) // 2
            
        cy = 33 - nh
        cell.paste(scaled, (cx, cy), scaled)
        return cell

def render_phrase_cell(ch):
    """เรนเดอร์ตัวอักษรสำหรับข้อความ 'ชื่อตัวละครหลัก' ด้วย Uniform Monospace Kerning (แบบที่ 3: ตัวผอมลง 4px สัดส่วนเพรียวสวย)"""
    cell = Image.new('RGBA', (36, 36), (0, 0, 0, 0))
    
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
        target_w = 27
        scaled = cropped.resize((target_w, cropped.height), Image.Resampling.LANCZOS)
        cx = (36 - target_w) // 2
        cy = coords[:, 0].min()
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
        target_w = 27
        scaled = cropped.resize((target_w, cropped.height), Image.Resampling.LANCZOS)
        cx = (36 - target_w) // 2
        cy = coords[:, 0].min()
        cell.paste(scaled, (cx, cy), scaled)
        return cell

    else:
        t = Image.new('RGBA', (80, 80), (0, 0, 0, 0))
        ImageDraw.Draw(t).text((40, 60), ch, font=f32, fill=(255, 255, 255, 255), anchor='ms')
        coords = np.argwhere(np.array(t)[:, :, 3] > 20)
        crop = t.crop((coords[:, 1].min(), coords[:, 0].min(), coords[:, 1].max() + 1, coords[:, 0].max() + 1))
        
        if ch in ['ะ']:
            target_w = 27
        elif ch in ['ว', 'ร']:
            target_w = 25
        elif ch in ['ค', 'ห', 'ก']:
            target_w = 28
        else: # อ, ล
            target_w = 27
            
        scaled = crop.resize((target_w, crop.height), Image.Resampling.LANCZOS)
        cx = (36 - target_w) // 2
        cy = 33 - crop.height
        cell.paste(scaled, (cx, cy), scaled)
        return cell

def main():
    print("=================================================================")
    print("[*] 1. เริ่มเรนเดอร์ Pro Thai Font (Uniform Monospace Kerning)...")
    print("=================================================================")
    
    with open(DDS_PATH, "rb") as f:
        dds = bytearray(f.read())

    WIDTH_BLOCKS = 1024
    BLOCK_BYTES = 16

    # 1. อัปเดตแป้นพิมพ์ 83 ปุ่ม
    print(f"[*] กำลังแพตช์แป้นพิมพ์ 83 ปุ่ม (ขยายขนาด 1.32x + วรรณยุกต์เดี่ยวชิดบน)...")
    for kana, (row, col), thai in KEYBOARD_MAPPING:
        cell = render_standalone_glyph(thai)
        rows_dxt = encode_cell_dxt5(cell)
        bx0 = (col * 36) // 4
        by0 = (row * 36) // 4
        for by in range(9):
            off = 128 + ((by0 + by) * WIDTH_BLOCKS + bx0) * BLOCK_BYTES
            dds[off : off + 144] = rows_dxt[by]

    # 2. ปรับแต่งตัวอักษรสำหรับข้อความ 'ชื่อตัวละครหลัก' ด้วย Uniform Monospace Kerning
    phrase_chars = [
        ('ชื่', 2, 67),
        ('อ',  2, 54),
        ('ตั', 2, 69),
        ('ว',  2, 45),
        ('ล',  2, 44),
        ('ะ',  2, 65),
        ('ค',  1, 103),
        ('ร',  2, 41),
        ('ห',  2, 50),
        ('ลั', 2, 71),
        ('ก',  1, 97),
    ]

    print("[*] กำลังแพตช์ตัวอักษร 'ชื่อตัวละครหลัก' แบบ Uniform Kerning เกลี่ยช่องไฟเท่ากันทุกตัว...")
    for ch, row, col in phrase_chars:
        cell = render_phrase_cell(ch)
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
    print("[SUCCESS] การติดตั้ง Pro Thai Font (Ultra-Tight) เสร็จสมบูรณ์ 100%!")
    print("=================================================================")

if __name__ == "__main__":
    main()
