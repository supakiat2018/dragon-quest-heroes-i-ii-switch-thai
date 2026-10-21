"""
test_perfect_chubby_font.py
ทดสอบสร้างฟอนต์ไทยตัวอ้วนเท่ากัน และความสูงรวมเท่ากันทุกตัวตามโจทย์เป๊ะ 100%:
- กฎเหล็ก:
  1. ตัวปกติ (เช่น ก, ม, ส, ง, บ, น, ซ, ล) มีความสูง 26-27px (เพดาน Y=5, ฐาน Y=32)
  2. ตัว 2 ชั้น (เช่น ร้, ล่): ย่อพยัญชนะลงมา วรรณยุกต์อยู่บนหัว -> รวมกันแล้วเพดาน Y=5, ฐาน Y=32 เท่ากับตัวปกติเป๊ะ!
  3. ตัว 3 ชั้น (เช่น กิ่, ริ่): ย่อพยัญชนะลงมา สระบน+วรรณยุกต์อยู่บนหัว -> รวมกันแล้วเพดาน Y=5, ฐาน Y=32 เท่ากับตัวปกติเป๊ะ!
  4. ทุกตัวต้อง 'อ้วนเท่ากัน' (ความหนาลายเส้น Bold หนาเท่ากัน ไม่แบน ไม่ลีบ ไม่เบี้ยว)
"""

import os
import numpy as np
from PIL import Image, ImageFont, ImageDraw

FONT_PATH = r"D:\Game\dragon quest heroes i & ii\switch\fonts\Pridi-Bold.ttf"

def get_crop(ch, font, stroke=0):
    t = Image.new('RGBA', (100, 100), (0, 0, 0, 0))
    d = ImageDraw.Draw(t)
    d.text((50, 60), ch, font=font, fill=(255, 255, 255, 255), anchor='ms',
           stroke_width=stroke, stroke_fill=(255, 255, 255, 255))
    arr = np.array(t)[:, :, 3]
    coords = np.argwhere(arr > 20)
    if len(coords) == 0:
        return Image.new('RGBA', (10, 10), (0, 0, 0, 0))
    return t.crop((coords[:, 1].min(), coords[:, 0].min(), coords[:, 1].max() + 1, coords[:, 0].max() + 1))

def create_glyph(ch_type):
    cell = Image.new('RGBA', (36, 36), (0, 0, 0, 0))
    BASE_Y = 32
    TOP_Y = 5
    TARGET_H = BASE_Y - TOP_Y # 27px
    
    # กรณี 3 ชั้น: ริ่ (ร + ิ + ่) หรือ กิ่ (ก + ิ + ่)
    if ch_type in ['ริ่', 'กิ่']:
        base_char = ch_type[0]
        # เพื่อให้ตัวพยัญชนะที่ย่อลงมายังคง 'อ้วนหนา' เท่ากับตัวปกติ
        # เราใช้ฟอนต์ขนาด 22pt + stroke_width=1 เพื่อชดเชยความหนาของเส้น
        f_b = ImageFont.truetype(FONT_PATH, 20)
        f_v = ImageFont.truetype(FONT_PATH, 18)
        f_t = ImageFont.truetype(FONT_PATH, 16)
        
        cr_b = get_crop(base_char, f_b, stroke=1)
        cr_v = get_crop('ิ', f_v, stroke=1)
        cr_t = get_crop('่', f_t, stroke=1)
        
        # ปรับสัดส่วนให้พอดี 27px รวม
        # ร สูงประมาณ 15px, สระ ิ สูง 6px, ไม้เอก สูง 6px -> รวม 27px!
        can = Image.new('RGBA', (80, 80), (0, 0, 0, 0))
        # วางจากล่างขึ้นบน
        # ฐานพยัญชนะอยู่ที่ y=60
        can.paste(cr_b, (40 - cr_b.width // 2, 60 - cr_b.height), cr_b)
        # สระ ิ อยู่เหนือพยัญชนะ
        y_v = 60 - cr_b.height - cr_v.height + 2
        can.paste(cr_v, (40 - cr_v.width // 2, y_v), cr_v)
        # ไม้เอก อยู่เหนือสระ ิ
        y_t = y_v - cr_t.height + 2
        can.paste(cr_t, (40 + cr_b.width // 2 - cr_t.width, y_t), cr_t)
        
        # Crop รวม
        arr = np.array(can)[:, :, 3]
        coords = np.argwhere(arr > 20)
        c_tot = can.crop((coords[:, 1].min(), coords[:, 0].min(), coords[:, 1].max() + 1, coords[:, 0].max() + 1))
        
        # ปรับสเกลให้อยู่ในความสูง 27px พอดี โดยรักษาสัดส่วนความอ้วน (ขยายกว้าง 1.25x)
        scale_y = TARGET_H / float(c_tot.height)
        new_h = TARGET_H
        new_w = int(round(c_tot.width * scale_y * 1.25))
        sc = c_tot.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        cx = (36 - new_w) // 2
        cell.paste(sc, (cx, TOP_Y), sc)
        return cell

    # กรณี 2 ชั้น: ร้ (ร + ้) หรือ ล่ (ล + ่)
    elif ch_type in ['ร้', 'ล่']:
        base_char = ch_type[0]
        tone_char = ch_type[1]
        
        f_b = ImageFont.truetype(FONT_PATH, 24)
        f_t = ImageFont.truetype(FONT_PATH, 18)
        
        cr_b = get_crop(base_char, f_b, stroke=1)
        cr_t = get_crop(tone_char, f_t, stroke=1)
        
        can = Image.new('RGBA', (80, 80), (0, 0, 0, 0))
        can.paste(cr_b, (40 - cr_b.width // 2, 60 - cr_b.height), cr_b)
        y_t = 60 - cr_b.height - cr_t.height + 2
        can.paste(cr_t, (40 + cr_b.width // 2 - cr_t.width, y_t), cr_t)
        
        arr = np.array(can)[:, :, 3]
        coords = np.argwhere(arr > 20)
        c_tot = can.crop((coords[:, 1].min(), coords[:, 0].min(), coords[:, 1].max() + 1, coords[:, 0].max() + 1))
        
        scale_y = TARGET_H / float(c_tot.height)
        new_h = TARGET_H
        new_w = int(round(c_tot.width * scale_y * 1.25))
        sc = c_tot.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        cx = (36 - new_w) // 2
        cell.paste(sc, (cx, TOP_Y), sc)
        return cell

    # สระหน้า (เ)
    elif ch_type in ['เ']:
        f = ImageFont.truetype(FONT_PATH, 32)
        cr = get_crop(ch_type, f, stroke=1)
        scale_y = TARGET_H / float(cr.height)
        new_h = TARGET_H
        new_w = int(round(cr.width * scale_y * 1.25))
        sc = cr.resize((new_w, new_h), Image.Resampling.LANCZOS)
        cx = 36 - new_w - 2 # ชิดขวาแนบพยัญชนะถัดไป
        cell.paste(sc, (cx, TOP_Y), sc)
        return cell

    # สระหลัง (า)
    elif ch_type in ['า']:
        f = ImageFont.truetype(FONT_PATH, 32)
        cr = get_crop(ch_type, f, stroke=1)
        scale_y = TARGET_H / float(cr.height)
        new_h = TARGET_H
        new_w = int(round(cr.width * scale_y * 1.25))
        sc = cr.resize((new_w, new_h), Image.Resampling.LANCZOS)
        cx = 2 # ชิดซ้ายแนบพยัญชนะข้างหน้า
        cell.paste(sc, (cx, TOP_Y), sc)
        return cell

    # ฟ (หางยาว)
    elif ch_type in ['ฟ']:
        f = ImageFont.truetype(FONT_PATH, 32)
        cr = get_crop(ch_type, f, stroke=1)
        scale_y = TARGET_H / float(cr.height)
        new_h = TARGET_H
        new_w = int(round(cr.width * scale_y * 1.20))
        sc = cr.resize((new_w, new_h), Image.Resampling.LANCZOS)
        cx = (36 - new_w) // 2
        cell.paste(sc, (cx, TOP_Y), sc)
        return cell

    # ตัวปกติ 1 ชั้น (ม, น, ง, บ, ส, ซ, ล, ก)
    else:
        f = ImageFont.truetype(FONT_PATH, 34)
        cr = get_crop(ch_type, f, stroke=1)
        scale_y = TARGET_H / float(cr.height)
        new_h = TARGET_H
        new_w = int(round(cr.width * scale_y * 1.20))
        # จำกัดความกว้างไม่ให้ล้น 34px
        new_w = min(32, new_w)
        sc = cr.resize((new_w, new_h), Image.Resampling.LANCZOS)
        cx = (36 - new_w) // 2
        cell.paste(sc, (cx, TOP_Y), sc)
        return cell

def main():
    test_chars = ['ก', 'กิ่', 'เ', 'ริ่', 'ม', 'ล่', 'น', 'ส', 'ร้', 'า', 'ง', 'ซ', 'ฟ', 'ล', 'บ']
    for c in test_chars:
        cell = create_glyph(c)
        arr = np.array(cell)[:, :, 3]
        coords = np.argwhere(arr > 20)
        ymin, xmin = coords.min(axis=0)
        ymax, xmax = coords.max(axis=0)
        print(f"Char '{c:2s}': y={ymin:2d}..{ymax:2d} (h={ymax-ymin+1:2d}), x={xmin:2d}..{xmax:2d} (w={xmax-xmin+1:2d})")

if __name__ == '__main__':
    main()
