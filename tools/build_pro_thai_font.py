"""
build_pro_thai_font.py
สคริปต์ปรับปรุงฟอนต์ภาษาไทยและแป้นพิมพ์ระดับมืออาชีพสำหรับ DQH2 บน Switch:
1. ปรับยกวรรณยุกต์ (่ ้ ๊ ๋ ์ ็) ให้ลอยสูงเด่นชัดขึ้นชิดขอบบนของปุ่ม (Y = 5px)
2. ปรับพยางค์สระซ้อน 3 ชั้น (เช่น ชื่) ให้ไม้เอกยกสูงลอยเหนือสระอือชัดเจน ไม่ทับซ้อนกัน
3. ขยายขนาดพยัญชนะให้เต็มเซลล์ (Width 26-30px) และลดขอบว่างด้านข้าง ทำให้ตัวหนังสือเรียงชิดติดกันเป็นคำสวยงาม
4. แพ็กเข้า G1T และฉีดเข้าตัวเกม (ทั้ง Atmosphere และ Yuzu) ทันที
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

# 3 คลัสเตอร์ในช่อง Katakana สำหรับคำว่า "ชื่อตัวละครหลัก"
SPECIAL_CLUSTERS = [
    ('ชื่', 2, 67), # Katakana ア
    ('ตั', 2, 69), # Katakana イ
    ('ลั', 2, 71), # Katakana ウ
]

TONE_MARKS = ['่', '้', '๊', '๋', '์', '็']
UPPER_MARKS = ['ิ', 'ี', 'ึ', 'ื', 'ั', 'ํ']
LOWER_MARKS = ['ุ', 'ู', 'ฺ']
DESCENDERS = ['ฎ', 'ฏ', 'ฐ', 'ฤ', 'ฦ', 'ญ']
TALL_CHARS = ['ป', 'ฝ', 'ฟ']

def render_standalone_glyph(ch, font_large):
    """เรนเดอร์ตัวอักษรเดี่ยวสำหรับแป้นพิมพ์ โดยจัดวางตามประเภทอักขระ"""
    cell = Image.new('RGBA', (36, 36), (0, 0, 0, 0))
    
    if ch in TONE_MARKS:
        # วรรณยุกต์เดี่ยว: วางชิดด้านบน (Y = 4-5px) เพื่อให้เห็นชัดเจนว่าเป็นวรรณยุกต์
        f = ImageFont.truetype(FONT_TTF, 34)
        t = Image.new('RGBA', (60, 60), (0, 0, 0, 0))
        ImageDraw.Draw(t).text((30, 30), ch, font=f, fill=(255, 255, 255, 255), anchor='mm')
        coords = np.argwhere(np.array(t)[:, :, 3] > 20)
        crop = t.crop((coords[:, 1].min(), coords[:, 0].min(), coords[:, 1].max() + 1, coords[:, 0].max() + 1))
        cx = (36 - crop.width) // 2
        cy = 5 # วางสูงขึ้นชิดบน!
        cell.paste(crop, (cx, cy), crop)
        return cell

    elif ch in UPPER_MARKS:
        # สระบนเดี่ยว: วางในโซนบน (Y = 8-10px)
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
        # สระล่าง: วางในโซนล่าง (Y = 22-24px)
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
        # พยัญชนะเดี่ยวและสระแนวบรรทัด: ขยายให้กว้าง 26-30px เต็มเซลล์ ตัวหนังสือจะชิดกันสวยงาม
        f = ImageFont.truetype(FONT_TTF, 34)
        t = Image.new('RGBA', (80, 80), (0, 0, 0, 0))
        ImageDraw.Draw(t).text((40, 60), ch, font=f, fill=(255, 255, 255, 255), anchor='ms')
        coords = np.argwhere(np.array(t)[:, :, 3] > 20)
        if len(coords) == 0:
            return cell
        crop = t.crop((coords[:, 1].min(), coords[:, 0].min(), coords[:, 1].max() + 1, coords[:, 0].max() + 1))
        
        target_h = 32 if ch in TALL_CHARS or ch in DESCENDERS else 27
        scale = min(target_h / crop.height, 31.0 / crop.width)
        nw, nh = int(round(crop.width * scale)), int(round(crop.height * scale))
        scaled = crop.resize((nw, nh), Image.Resampling.LANCZOS)
        
        # จัดตำแหน่ง Optical Kerning
        if ch in ['ะ', 'า', 'ำ']:
            cx = 2 # สระหลัง ชิดซ้าย เพื่อดูดติดพยัญชนะหน้า
        elif ch in ['เ', 'แ', 'โ', 'ใ', 'ไ']:
            cx = 36 - nw - 2 # สระหน้า ชิดขวา เพื่อดูดติดพยัญชนะหลัง
        elif ch in ['ร', 'ว']:
            cx = (36 - nw) // 2 - 2 # ชิดซ้ายเล็กน้อย
        else:
            cx = (36 - nw) // 2
            
        cy = 32 - nh # Baseline แถว Y=32
        cell.paste(scaled, (cx, cy), scaled)
        return cell

def render_composite_cluster(base, vowel='', tone=''):
    """เรนเดอร์พยางค์สระซ้อน โดยแยกเลเยอร์วรรณยุกต์ให้ลอยสูงเด่นชัด ไม่ทับสระ"""
    cell = Image.new('RGBA', (36, 36), (0, 0, 0, 0))
    f_base = ImageFont.truetype(FONT_TTF, 34)
    f_mark = ImageFont.truetype(FONT_TTF, 30)
    
    # 1. พยัญชนะฐาน
    t_base = Image.new('RGBA', (80, 80), (0, 0, 0, 0))
    ImageDraw.Draw(t_base).text((40, 60), base, font=f_base, fill=(255, 255, 255, 255), anchor='ms')
    coords_b = np.argwhere(np.array(t_base)[:, :, 3] > 20)
    b_top, b_bot = coords_b[:, 0].min(), coords_b[:, 0].max()
    b_left, b_right = coords_b[:, 1].min(), coords_b[:, 1].max()
    crop_b = t_base.crop((b_left, b_top, b_right + 1, b_bot + 1))
    
    can = Image.new('RGBA', (80, 80), (0, 0, 0, 0))
    y_b = 80 - crop_b.height
    x_b = (80 - crop_b.width) // 2
    can.paste(crop_b, (x_b, y_b), crop_b)
    
    v_top = y_b
    # 2. สระบน
    if vowel:
        t_v = Image.new('RGBA', (80, 80), (0, 0, 0, 0))
        ImageDraw.Draw(t_v).text((40, 60), vowel, font=f_base, fill=(255, 255, 255, 255), anchor='ms')
        coords_v = np.argwhere(np.array(t_v)[:, :, 3] > 20)
        crop_v = t_v.crop((coords_v[:, 1].min(), coords_v[:, 0].min(), coords_v[:, 1].max() + 1, coords_v[:, 0].max() + 1))
        y_v = y_b - crop_v.height + 3
        x_v = x_b + (crop_b.width - crop_v.width) // 2
        can.paste(crop_v, (x_v, y_v), crop_v)
        v_top = y_v
        
    # 3. วรรณยุกต์ (ยกสูงขึ้น 2px เหนือสระบน)
    if tone:
        t_t = Image.new('RGBA', (80, 80), (0, 0, 0, 0))
        ImageDraw.Draw(t_t).text((40, 60), tone, font=f_mark, fill=(255, 255, 255, 255), anchor='ms')
        coords_t = np.argwhere(np.array(t_t)[:, :, 3] > 20)
        crop_t = t_t.crop((coords_t[:, 1].min(), coords_t[:, 0].min(), coords_t[:, 1].max() + 1, coords_t[:, 0].max() + 1))
        y_t = v_top - crop_t.height - 2 # ยกสูง มีช่องว่าง 2px!
        x_t = x_b + crop_b.width - crop_t.width - 2
        can.paste(crop_t, (x_t, y_t), crop_t)
        
    coords = np.argwhere(np.array(can)[:, :, 3] > 20)
    cropped = can.crop((coords[:, 1].min(), coords[:, 0].min(), coords[:, 1].max() + 1, coords[:, 0].max() + 1))
    scale = min(33.0 / cropped.height, 32.0 / cropped.width)
    nw, nh = int(round(cropped.width * scale)), int(round(cropped.height * scale))
    scaled = cropped.resize((nw, nh), Image.Resampling.LANCZOS)
    
    cx = (36 - nw) // 2
    cy = 34 - nh
    cell.paste(scaled, (cx, cy), scaled)
    return cell

def main():
    print("=================================================================")
    print("[*] 1. เริ่มกระบวนการสร้าง Pro Thai Font (ตัวชิด + วรรณยุกต์สูง)...")
    print("=================================================================")
    
    with open(DDS_PATH, "rb") as f:
        dds = bytearray(f.read())

    WIDTH_BLOCKS = 1024
    BLOCK_BYTES = 16

    # ก) อัปเดต 83 ปุ่มแป้นพิมพ์ทั้งหมด
    print(f"[*] กำลังเรนเดอร์แป้นพิมพ์ 83 ปุ่ม (ขยายขนาดเต็มช่อง + ยกวรรณยุกต์สูง)...")
    for kana, (row, col), thai in KEYBOARD_MAPPING:
        cell = render_standalone_glyph(thai, None)
        rows_dxt = encode_cell_dxt5(cell)
        bx0 = (col * 36) // 4
        by0 = (row * 36) // 4
        for by in range(9):
            off = 128 + ((by0 + by) * WIDTH_BLOCKS + bx0) * BLOCK_BYTES
            dds[off : off + 144] = rows_dxt[by]

    print("[+] อัปเดตแป้นพิมพ์ 83 ปุ่มลงใน DDS เรียบร้อย!")

    # ข) เรนเดอร์ 3 คลัสเตอร์พิเศษในช่อง Katakana (ア, イ, ウ)
    print(f"[*] กำลังเรนเดอร์คลัสเตอร์ 'ชื่', 'ตั', 'ลั' (ยกไม้เอกสูง คมชัด ไม่ทับสระ)...")
    clusters_data = [
        ('ชื่', 2, 67, 'ช', 'ื', '่'),
        ('ตั', 2, 69, 'ต', 'ั', ''),
        ('ลั', 2, 71, 'ล', 'ั', ''),
    ]

    for name, row, col, base, vowel, tone in clusters_data:
        cell = render_composite_cluster(base, vowel, tone)
        
        # บันทึกพรีวิว
        bg = Image.new('RGB', (36, 36), (0, 0, 0))
        bg.paste(cell, (0, 0), cell)
        bg.resize((108, 108), Image.Resampling.NEAREST).save(os.path.join(SWITCH_DIR, "workspace", f"pro_preview_{name}.png"))
        
        rows_dxt = encode_cell_dxt5(cell)
        bx0 = (col * 36) // 4
        by0 = (row * 36) // 4
        for by in range(9):
            off = 128 + ((by0 + by) * WIDTH_BLOCKS + bx0) * BLOCK_BYTES
            dds[off : off + 144] = rows_dxt[by]
        print(f"    [+] แพตช์คลัสเตอร์ '{name}' ลงที่ Row {row}, Col {col} สำเร็จ")

    with open(DDS_PATH, "wb") as f:
        f.write(dds)
    print("[+] บันทึกไฟล์ DDS เรียบร้อย!")

    # 2. แปลง DDS กลับเป็น G1T
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

    # 3. ฉีด Entry 55 เข้าสู่ LINKDATA.BIN
    print("[*] 3. ฉีด Entry 55 เข้าสู่ LINKDATA.BIN ทั้งหมด...")
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

    # 4. เขียนข้อความ 'ชื่อตัวละครหลัก' (アよイみまんえほやウあ) ลงใน Entry 36
    print("[*] 4. อัปเดตข้อความหัวข้อใน Entry 36...")
    target_str = "アよイみまんえほやウあ"
    enc = target_str.encode("utf-8")
    padded_text = enc + b'\x00' * (48 - len(enc))

    for p in targets:
        if os.path.exists(p):
            with open(p, "r+b") as f:
                f.seek(3740846848 + 87361)
                f.write(padded_text)
            print(f"    [+] เขียนข้อความ '{target_str}' ลงใน Entry 36 ({p}) สำเร็จ")

    print("\n=================================================================")
    print("[SUCCESS] การติดตั้ง Pro Thai Font เสร็จสมบูรณ์ 100%!")
    print("=================================================================")

if __name__ == "__main__":
    main()
