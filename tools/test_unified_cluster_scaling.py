"""
test_unified_cluster_scaling.py
ทดสอบเทคนิค: ประกอบทั้งคลัสเตอร์ (พยัญชนะ+สระ+วรรณยุกต์) ให้เป็นชิ้นเดียวกันอย่างเป็นธรรมชาติ
แล้วสเกลความสูงรวมให้เท่ากับ H_target (26px) เท่ากันทุกตัว
พร้อมขยายความกว้างให้อิ่มหนา (WIDTH_SCALE = 1.25 - 1.30)
"""

import os
import numpy as np
from PIL import Image, ImageFont, ImageDraw

FONT_PATH = r"D:\Game\dragon quest heroes i & ii\switch\fonts\Pridi-Bold.ttf"

TARGET_H = 26  # ความสูงเป้าหมายเท่ากันทุกตัวเป๊ะ 26px
TOP_Y = 6      # เพดานบน
BASE_Y = 32    # เส้นฐานล่าง (32 - 6 = 26)

f_stand = ImageFont.truetype(FONT_PATH, 36) # สำหรับตัวเดี่ยว
f_base  = ImageFont.truetype(FONT_PATH, 30) # สำหรับฐานในคลัสเตอร์
f_vowel = ImageFont.truetype(FONT_PATH, 22) # สำหรับสระบน
f_tone  = ImageFont.truetype(FONT_PATH, 20) # สำหรับวรรณยุกต์

def get_crop(ch, font):
    t = Image.new('RGBA', (100, 100), (0, 0, 0, 0))
    d = ImageDraw.Draw(t)
    d.text((50, 60), ch, font=font, fill=(255, 255, 255, 255), anchor='ms')
    arr = np.array(t)[:, :, 3]
    coords = np.argwhere(arr > 20)
    if len(coords) == 0:
        return Image.new('RGBA', (10, 10), (0, 0, 0, 0))
    return t.crop((coords[:, 1].min(), coords[:, 0].min(), coords[:, 1].max() + 1, coords[:, 0].max() + 1))

def make_unified_cell(ch_type):
    cell = Image.new('RGBA', (36, 36), (0, 0, 0, 0))
    
    # 1. กลุ่ม 3 ชั้น: ริ่, กิ่
    if ch_type in ['ริ่', 'กิ่']:
        base_ch = ch_type[0]
        cr_b = get_crop(base_ch, f_base)
        cr_v = get_crop('ิ', f_vowel)
        cr_t = get_crop('่', f_tone)
        
        can = Image.new('RGBA', (100, 100), (0, 0, 0, 0))
        # ฐานพยัญชนะ
        x_b = 50 - cr_b.width // 2
        y_b = 70 - cr_b.height
        can.paste(cr_b, (x_b, y_b), cr_b)
        
        # สระ ิ บนหัวพยัญชนะ
        x_v = x_b + (cr_b.width - cr_v.width) // 2
        y_v = y_b - cr_v.height + 2
        can.paste(cr_v, (x_v, y_v), cr_v)
        
        # วรรณยุกต์ ่ บนสระ ิ
        x_t = x_b + cr_b.width - cr_t.width - 1
        y_t = y_v - cr_t.height + 2
        can.paste(cr_t, (x_t, y_t), cr_t)
        
        # Crop รวมทั้งคลัสเตอร์
        arr = np.array(can)[:, :, 3]
        coords = np.argwhere(arr > 20)
        c_tot = can.crop((coords[:, 1].min(), coords[:, 0].min(), coords[:, 1].max() + 1, coords[:, 0].max() + 1))
        
        # ย่อ/ขยายทั้งคลัสเตอร์เป็นชิ้นเดียว ให้สูง = TARGET_H (26px) เป๊ะ!
        scale_y = TARGET_H / float(c_tot.height)
        new_w = int(round(c_tot.width * scale_y * 1.30)) # อ้วนหนา 1.30x
        new_w = min(32, new_w)
        sc = c_tot.resize((new_w, TARGET_H), Image.Resampling.LANCZOS)
        
        cx = (36 - new_w) // 2
        cell.paste(sc, (cx, TOP_Y), sc)
        return cell

    # 2. กลุ่ม 2 ชั้น: ร้, ล่
    elif ch_type in ['ร้', 'ล่']:
        base_ch = ch_type[0]
        tone_ch = ch_type[1]
        cr_b = get_crop(base_ch, f_base)
        cr_t = get_crop(tone_ch, f_tone)
        
        can = Image.new('RGBA', (100, 100), (0, 0, 0, 0))
        x_b = 50 - cr_b.width // 2
        y_b = 70 - cr_b.height
        can.paste(cr_b, (x_b, y_b), cr_b)
        
        x_t = x_b + cr_b.width - cr_t.width
        y_t = y_b - cr_t.height + 2
        can.paste(cr_t, (x_t, y_t), cr_t)
        
        arr = np.array(can)[:, :, 3]
        coords = np.argwhere(arr > 20)
        c_tot = can.crop((coords[:, 1].min(), coords[:, 0].min(), coords[:, 1].max() + 1, coords[:, 0].max() + 1))
        
        scale_y = TARGET_H / float(c_tot.height)
        new_w = int(round(c_tot.width * scale_y * 1.30))
        new_w = min(32, new_w)
        sc = c_tot.resize((new_w, TARGET_H), Image.Resampling.LANCZOS)
        
        cx = (36 - new_w) // 2
        cell.paste(sc, (cx, TOP_Y), sc)
        return cell

    # 3. สระหน้า (เ)
    elif ch_type == 'เ':
        cr = get_crop('เ', f_stand)
        scale_y = TARGET_H / float(cr.height)
        new_w = int(round(cr.width * scale_y * 1.30))
        sc = cr.resize((new_w, TARGET_H), Image.Resampling.LANCZOS)
        cx = 36 - new_w - 2 # ชิดขวา
        cell.paste(sc, (cx, TOP_Y), sc)
        return cell

    # 4. สระหลัง (า)
    elif ch_type == 'า':
        cr = get_crop('า', f_stand)
        scale_y = TARGET_H / float(cr.height)
        new_w = int(round(cr.width * scale_y * 1.30))
        sc = cr.resize((new_w, TARGET_H), Image.Resampling.LANCZOS)
        cx = 2 # ชิดซ้าย
        cell.paste(sc, (cx, TOP_Y), sc)
        return cell

    # 5. ฟ (หางยาว)
    elif ch_type == 'ฟ':
        cr = get_crop('ฟ', f_stand)
        scale_y = TARGET_H / float(cr.height)
        new_w = int(round(cr.width * scale_y * 1.30))
        new_w = min(32, new_w)
        sc = cr.resize((new_w, TARGET_H), Image.Resampling.LANCZOS)
        cx = (36 - new_w) // 2
        cell.paste(sc, (cx, TOP_Y), sc)
        return cell

    # 6. ตัวปกติ 1 ชั้น: ก, ม, น, ง, บ, ส, ซ, ล
    else:
        cr = get_crop(ch_type, f_stand)
        scale_y = TARGET_H / float(cr.height)
        new_w = int(round(cr.width * scale_y * 1.30))
        new_w = min(32, new_w)
        sc = cr.resize((new_w, TARGET_H), Image.Resampling.LANCZOS)
        cx = (36 - new_w) // 2
        cell.paste(sc, (cx, TOP_Y), sc)
        return cell

def main():
    test_chars = ['ก', 'กิ่', 'เ', 'ริ่', 'ม', 'ล่', 'น', 'ส', 'ร้', 'า', 'ง', 'ซ', 'ฟ', 'ล', 'บ']
    cells = {c: make_unified_cell(c) for c in test_chars}
    
    # Render Preview Graphic
    preview_w = 720
    preview_h = 420
    img = Image.new('RGBA', (preview_w, preview_h), (18, 22, 32, 255))
    draw = ImageDraw.Draw(img)
    
    t_font = ImageFont.truetype(FONT_PATH, 16)
    
    sections = [
        ("ตัวอย่างตามโจทย์: ก vs กิ่ (ย่อ ก ลงมา รวมสระ+วรรณยุกต์แล้วสูงเท่า ก เป๊ะ และอ้วนเท่ากัน)", ['ก', 'กิ่']),
        ("ปุ่มที่ 1: เริ่มเล่น (冒険をする)", ['เ', 'ริ่', 'ม', 'เ', 'ล่', 'น']),
        ("ปุ่มที่ 2: สร้างเซฟ (冒険の書をつくる)", ['ส', 'ร้', 'า', 'ง', 'เ', 'ซ', 'ฟ']),
        ("ปุ่มที่ 3: ลบเซฟ (冒険の書を消す)", ['ล', 'บ', 'เ', 'ซ', 'ฟ']),
    ]
    
    y_cur = 16
    for sec_title, sec_chars in sections:
        draw.text((32, y_cur), sec_title, font=t_font, fill=(245, 215, 120, 255))
        y_cur += 25
        
        box_w = len(sec_chars) * 36 + 24
        box_h = 44
        draw.rounded_rectangle([32, y_cur, 32 + box_w, y_cur + box_h], radius=7, 
                               fill=(28, 38, 56, 255), outline=(65, 95, 145, 255), width=2)
        
        line_top = y_cur + 4 + TOP_Y
        line_base = y_cur + 4 + BASE_Y
        draw.line([38, line_top, 32 + box_w - 6, line_top], fill=(255, 70, 70, 160), width=1)
        draw.line([38, line_base, 32 + box_w - 6, line_base], fill=(70, 255, 70, 160), width=1)
        
        x_char = 44
        for ch in sec_chars:
            c_img = cells[ch]
            draw.rectangle([x_char, y_cur + 4, x_char + 35, y_cur + 39], outline=(50, 70, 105, 70))
            img.paste(c_img, (x_char, y_cur + 4), mask=c_img)
            x_char += 36
            
        y_cur += box_h + 16
        
    out_path = r"C:\Users\Supakiat\.gemini\antigravity\brain\ab5bc3db-774b-46d7-96ba-65470fc9eb39\unified_cluster_preview.png"
    img.save(out_path)
    print(f"\n[+] บันทึกภาพพรีวิว: {out_path}")

if __name__ == '__main__':
    main()
