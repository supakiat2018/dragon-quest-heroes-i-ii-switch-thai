"""
create_master_preview.py
สร้างภาพพรีวิวฟอนต์ไทยตัวอ้วนเท่ากันระดับสมบูรณ์แบบ (Masterpiece):
1. เปรียบเทียบ ก vs กิ่ (ย่อ ก ลงมา รวมสระ+วรรณยุกต์แล้วสูงเท่า ก เป๊ะ และอ้วนเท่ากันตามโจทย์ 100%)
2. พรีวิว 3 ปุ่มเมนูพร้อมเส้นไกด์วัดระดับ (เริ่มเล่น, สร้างเซฟ, ลบเซฟ)
3. พรีวิวจิ๊กซอว์เมนูในเกมจริง (In-Game Menu Simulation)
"""

import os
import numpy as np
from PIL import Image, ImageFont, ImageDraw

FONT_PATH = r"D:\Game\dragon quest heroes i & ii\switch\fonts\Pridi-Bold.ttf"

TARGET_H = 26
TOP_Y = 6
BASE_Y = 32

f_stand = ImageFont.truetype(FONT_PATH, 36)
f_base  = ImageFont.truetype(FONT_PATH, 30)
f_vowel = ImageFont.truetype(FONT_PATH, 22)
f_tone  = ImageFont.truetype(FONT_PATH, 20)

def get_crop(ch, font):
    t = Image.new('RGBA', (100, 100), (0, 0, 0, 0))
    ImageDraw.Draw(t).text((50, 60), ch, font=font, fill=(255, 255, 255, 255), anchor='ms')
    arr = np.array(t)[:, :, 3]
    coords = np.argwhere(arr > 20)
    return t.crop((coords[:, 1].min(), coords[:, 0].min(), coords[:, 1].max() + 1, coords[:, 0].max() + 1))

def make_perfect_cell(ch_type):
    cell = Image.new('RGBA', (36, 36), (0, 0, 0, 0))
    
    # 1. คลัสเตอร์ 3 ชั้น: ริ่, กิ่
    if ch_type in ['ริ่', 'กิ่']:
        base_ch = ch_type[0]
        cr_b = get_crop(base_ch, f_base)
        cr_v = get_crop('ิ', f_vowel)
        cr_t = get_crop('่', f_tone)
        
        can = Image.new('RGBA', (100, 100), (0, 0, 0, 0))
        x_b = 50 - cr_b.width // 2
        y_b = 70 - cr_b.height
        can.paste(cr_b, (x_b, y_b), cr_b)
        x_v = x_b + (cr_b.width - cr_v.width) // 2
        y_v = y_b - cr_v.height + 2
        can.paste(cr_v, (x_v, y_v), cr_v)
        x_t = x_b + cr_b.width - cr_t.width - 1
        y_t = y_v - cr_t.height + 2
        can.paste(cr_t, (x_t, y_t), cr_t)
        
        coords = np.argwhere(np.array(can)[:, :, 3] > 20)
        c_tot = can.crop((coords[:, 1].min(), coords[:, 0].min(), coords[:, 1].max() + 1, coords[:, 0].max() + 1))
        
        target_w = 23 # อิ่มหนาพอดี
        sc = c_tot.resize((target_w, TARGET_H), Image.Resampling.LANCZOS)
        cx = 5 if ch_type == 'ริ่' else 6
        cell.paste(sc, (cx, TOP_Y), sc)
        return cell

    # 2. คลัสเตอร์ 2 ชั้น: ร้, ล่
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
        
        coords = np.argwhere(np.array(can)[:, :, 3] > 20)
        c_tot = can.crop((coords[:, 1].min(), coords[:, 0].min(), coords[:, 1].max() + 1, coords[:, 0].max() + 1))
        
        target_w = 24
        sc = c_tot.resize((target_w, TARGET_H), Image.Resampling.LANCZOS)
        cx = 5
        cell.paste(sc, (cx, TOP_Y), sc)
        return cell

    # 3. สระหน้า: เ (ชิดขวารับพยัญชนะถัดไป)
    elif ch_type == 'เ':
        cr = get_crop('เ', f_stand)
        scale_y = TARGET_H / float(cr.height)
        w = int(round(cr.width * scale_y * 1.35))
        sc = cr.resize((w, TARGET_H), Image.Resampling.LANCZOS)
        cx = 36 - w - 2
        cell.paste(sc, (cx, TOP_Y), sc)
        return cell

    # 4. สระหลัง: า (ชิดซ้ายรับพยัญชนะข้างหน้า)
    elif ch_type == 'า':
        cr = get_crop('า', f_stand)
        scale_y = TARGET_H / float(cr.height)
        w = int(round(cr.width * scale_y * 1.35))
        sc = cr.resize((w, TARGET_H), Image.Resampling.LANCZOS)
        cx = 2
        cell.paste(sc, (cx, TOP_Y), sc)
        return cell

    # 5. ฟ (หางยาว)
    elif ch_type == 'ฟ':
        cr = get_crop('ฟ', f_stand)
        scale_y = TARGET_H / float(cr.height)
        w = int(round(cr.width * scale_y * 1.25))
        w = min(28, w)
        sc = cr.resize((w, TARGET_H), Image.Resampling.LANCZOS)
        cx = (36 - w) // 2
        cell.paste(sc, (cx, TOP_Y), sc)
        return cell

    # 6. ตัวปกติ 1 ชั้น: ก, ม, น, ง, บ, ส, ซ, ล
    else:
        cr = get_crop(ch_type, f_stand)
        scale_y = TARGET_H / float(cr.height)
        w = int(round(cr.width * scale_y * 1.30))
        w = min(28, w)
        sc = cr.resize((w, TARGET_H), Image.Resampling.LANCZOS)
        cx = (36 - w) // 2
        cell.paste(sc, (cx, TOP_Y), sc)
        return cell

def main():
    all_chars = ['ก', 'กิ่', 'เ', 'ริ่', 'ม', 'ล่', 'น', 'ส', 'ร้', 'า', 'ง', 'ซ', 'ฟ', 'ล', 'บ']
    cells = {c: make_perfect_cell(c) for c in all_chars}
    
    preview_w = 750
    preview_h = 560
    img = Image.new('RGBA', (preview_w, preview_h), (16, 20, 28, 255))
    draw = ImageDraw.Draw(img)
    
    f_header = ImageFont.truetype(FONT_PATH, 18)
    f_sub = ImageFont.truetype(FONT_PATH, 14)
    
    # -------------------------------------------------------------
    # ส่วนที่ 1: พิสูจน์หลักการ ก vs กิ่ ตามโจทย์ของคุณ Supakiat
    # -------------------------------------------------------------
    draw.text((32, 16), "หลักการตัวอ้วนเท่ากัน & ความสูงเท่ากัน: ก vs กิ่", font=f_header, fill=(255, 215, 100, 255))
    draw.text((32, 40), "- ก ปกติ (สูง 26px) เทียบกับ กิ่ (ย่อ ก ลงมา รวมสระ+วรรณยุกต์แล้วสูง 26px เท่ากันเป๊ะ ลายเส้นหนาอ้วนเท่ากัน)", 
              font=f_sub, fill=(180, 195, 215, 255))
    
    # กรอบ ก vs กิ่
    y_k = 66
    draw.rounded_rectangle([32, y_k, 32 + 2 * 36 + 24, y_k + 44], radius=6, fill=(26, 34, 48, 255), outline=(55, 80, 120, 255), width=2)
    # เส้นแดง = เพดานบน (y=6), เส้นเขียว = เส้นฐานล่าง (y=32)
    draw.line([38, y_k + 4 + TOP_Y, 32 + 2 * 36 + 18, y_k + 4 + TOP_Y], fill=(255, 70, 70, 200), width=1)
    draw.line([38, y_k + 4 + BASE_Y, 32 + 2 * 36 + 18, y_k + 4 + BASE_Y], fill=(70, 255, 70, 200), width=1)
    
    x_k = 44
    for ch in ['ก', 'กิ่']:
        c_img = cells[ch]
        draw.rectangle([x_k, y_k + 4, x_k + 35, y_k + 39], outline=(45, 65, 95, 120))
        img.paste(c_img, (x_k, y_k + 4), mask=c_img)
        x_k += 36

    # -------------------------------------------------------------
    # ส่วนที่ 2: พรีวิว 3 เมนู (พร้อมเส้นไกด์วัดระดับ)
    # -------------------------------------------------------------
    draw.text((32, 126), "พรีวิว 3 เมนู (เริ่มเล่น / สร้างเซฟ / ลบเซฟ): ความสูงระนาบเดียวกัน 100%", font=f_header, fill=(255, 215, 100, 255))
    
    menus = [
        ("ปุ่มที่ 1: เริ่มเล่น", ['เ', 'ริ่', 'ม', 'เ', 'ล่', 'น']),
        ("ปุ่มที่ 2: สร้างเซฟ", ['ส', 'ร้', 'า', 'ง', 'เ', 'ซ', 'ฟ']),
        ("ปุ่มที่ 3: ลบเซฟ", ['ล', 'บ', 'เ', 'ซ', 'ฟ']),
    ]
    
    y_menu = 154
    for title, m_chars in menus:
        draw.text((32, y_menu), title, font=f_sub, fill=(220, 230, 245, 255))
        y_menu += 22
        
        box_w = len(m_chars) * 36 + 24
        box_h = 44
        draw.rounded_rectangle([32, y_menu, 32 + box_w, y_menu + box_h], radius=6, fill=(26, 34, 48, 255), outline=(55, 80, 120, 255), width=2)
        
        draw.line([38, y_menu + 4 + TOP_Y, 32 + box_w - 6, y_menu + 4 + TOP_Y], fill=(255, 70, 70, 180), width=1)
        draw.line([38, y_menu + 4 + BASE_Y, 32 + box_w - 6, y_menu + 4 + BASE_Y], fill=(70, 255, 70, 180), width=1)
        
        x_char = 44
        for ch in m_chars:
            c_img = cells[ch]
            draw.rectangle([x_char, y_menu + 4, x_char + 35, y_menu + 39], outline=(45, 65, 95, 90))
            img.paste(c_img, (x_char, y_menu + 4), mask=c_img)
            x_char += 36
            
        y_menu += box_h + 12

    # -------------------------------------------------------------
    # ส่วนที่ 3: จำลองภาพในเกมจริง (In-Game Clean Look)
    # -------------------------------------------------------------
    draw.text((32, 386), "จำลองหน้าจอเมนูในเกมจริง (ไร้เส้นไกด์ สวย คม ชัด สไตล์ Dragon Quest)", font=f_header, fill=(255, 215, 100, 255))
    
    y_sim = 416
    for title, m_chars in menus:
        box_w = len(m_chars) * 36 + 32
        box_h = 42
        # กรอบปุ่มเกมจริง: ขอบทองสองชั้น พื้นหลังน้ำเงินเข้ม
        draw.rounded_rectangle([32, y_sim, 32 + box_w, y_sim + box_h], radius=5, fill=(18, 28, 48, 255), outline=(195, 160, 85, 255), width=2)
        draw.rounded_rectangle([34, y_sim + 2, 32 + box_w - 2, y_sim + box_h - 2], radius=4, outline=(40, 60, 95, 255), width=1)
        
        x_char = 48
        for ch in m_chars:
            c_img = cells[ch]
            img.paste(c_img, (x_char, y_sim + 3), mask=c_img)
            x_char += 36
            
        y_sim += box_h + 8

    out_path = r"C:\Users\Supakiat\.gemini\antigravity\brain\ab5bc3db-774b-46d7-96ba-65470fc9eb39\master_chubby_font_preview.png"
    img.save(out_path)
    print(f"[+] สร้างภาพพรีวิวสมบูรณ์แบบสำเร็จ: {out_path}")

if __name__ == '__main__':
    main()
