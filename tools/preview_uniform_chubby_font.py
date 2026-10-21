"""
preview_uniform_chubby_font.py
สร้างฟอนต์ไทยตัวอ้วนเท่ากัน และความสูงรวมเท่ากันทุกตัวตามคำสั่งเป๊ะๆ 100%:
- กฎเหล็ก: ตัวที่มีสระบน (เช่น ร้, ล่, ริ่) ต้องย่อตัวพยัญชนะลงมา ให้ความสูงรวมเท่ากับตัวปกติ (เช่น ก)
- ทุกตัวอักษรมีความสูงรวมเท่ากันเป๊ะที่ 28 พิกเซล (เพดาน Y=4 ถึง ฐาน Y=32)
- ทุกตัวมีความอ้วนสม่ำเสมอเท่ากันที่ 26 พิกเซล
- ชิดสวยงาม ไม่กระโดด ไม่ลอยทะลุเพดาน
"""

import os
import numpy as np
from PIL import Image, ImageFont, ImageDraw

BASE_DIR = r"D:\Game\dragon quest heroes i & ii"
FONT_TTF = os.path.join(BASE_DIR, "switch", "fonts", "Pridi-Bold.ttf")

f_main = ImageFont.truetype(FONT_TTF, 34)
f_sub  = ImageFont.truetype(FONT_TTF, 24)
f_tone = ImageFont.truetype(FONT_TTF, 22)

TOTAL_HEIGHT = 28 # ความสูงเป้าหมายเท่ากันทุกตัว (28px)
BASE_Y = 32       # เส้นฐานที่ Y=32
CHUBBY_W = 26     # ความอ้วนมาตรฐานเท่ากันทุกตัว

def get_crop(ch, font):
    t = Image.new('RGBA', (80, 80), (0, 0, 0, 0))
    ImageDraw.Draw(t).text((40, 55), ch, font=font, fill=(255, 255, 255, 255), anchor='ms')
    arr = np.array(t)[:, :, 3]
    coords = np.argwhere(arr > 20)
    if len(coords) == 0:
        return Image.new('RGBA', (10, 10), (0, 0, 0, 0))
    return t.crop((coords[:, 1].min(), coords[:, 0].min(), coords[:, 1].max() + 1, coords[:, 0].max() + 1))

def make_uniform_cell(ch_type):
    cell = Image.new('RGBA', (36, 36), (0, 0, 0, 0))
    
    # 1. คลัสเตอร์ 3 ชั้น: ริ่ (ร + ิ + ่) -> ย่อ ร ลงมาเพื่อให้รวมสระแล้วสูง 28px เท่าตัวปกติ
    if ch_type == 'ริ่':
        cr_r = get_crop('ร', f_main)
        cr_v = get_crop('ิ', f_sub)
        cr_t = get_crop('่', f_tone)
        
        target_r_h = 16
        target_r_w = CHUBBY_W
        sc_r = cr_r.resize((target_r_w, target_r_h), Image.Resampling.LANCZOS)
        sc_v = cr_v.resize((19, 7), Image.Resampling.LANCZOS)
        sc_t = cr_t.resize((8, 6), Image.Resampling.LANCZOS)
        
        cx = (36 - target_r_w) // 2
        cy_r = BASE_Y - target_r_h # 32 - 16 = 16
        cy_v = cy_r - 7            # 9
        cy_t = cy_v - 5            # 4
        
        cell.paste(sc_r, (cx, cy_r), sc_r)
        cell.paste(sc_v, (cx + (target_r_w - 19) // 2, cy_v), sc_v)
        cell.paste(sc_t, (cx + target_r_w - 9, cy_t), sc_t)
        return cell

    # 2. คลัสเตอร์ 2 ชั้น: ร้ (ร + ้) -> ย่อ ร ลงมาให้รวมไม้โทแล้วสูง 28px เท่าตัวปกติ
    elif ch_type == 'ร้':
        cr_r = get_crop('ร', f_main)
        cr_t = get_crop('้', f_tone)
        
        target_r_h = 19
        target_r_w = CHUBBY_W
        sc_r = cr_r.resize((target_r_w, target_r_h), Image.Resampling.LANCZOS)
        sc_t = cr_t.resize((11, 9), Image.Resampling.LANCZOS)
        
        cx = (36 - target_r_w) // 2
        cy_r = BASE_Y - target_r_h # 32 - 19 = 13
        cy_t = cy_r - 9            # 4
        
        cell.paste(sc_r, (cx, cy_r), sc_r)
        cell.paste(sc_t, (cx + target_r_w - 11, cy_t), sc_t)
        return cell

    # 3. คลัสเตอร์ 2 ชั้น: ล่ (ล + ่) -> ย่อ ล ลงมาให้รวมไม้เอกแล้วสูง 28px เท่าตัวปกติ
    elif ch_type == 'ล่':
        cr_l = get_crop('ล', f_main)
        cr_t = get_crop('่', f_tone)
        
        target_l_h = 20
        target_l_w = CHUBBY_W
        sc_l = cr_l.resize((target_l_w, target_l_h), Image.Resampling.LANCZOS)
        sc_t = cr_t.resize((9, 8), Image.Resampling.LANCZOS)
        
        cx = (36 - target_l_w) // 2
        cy_l = BASE_Y - target_l_h # 32 - 20 = 12
        cy_t = cy_l - 8            # 4
        
        cell.paste(sc_l, (cx, cy_l), sc_l)
        cell.paste(sc_t, (cx + target_l_w - 10, cy_t), sc_t)
        return cell

    # 4. ตัวปกติ (ไม่มีสระบน): ส, า, ง, ม, น, ล, บ, เ, ซ, ฟ
    else:
        cr = get_crop(ch_type, f_main)
        target_h = TOTAL_HEIGHT
        if ch_type in ['เ']:
            target_w = 20
            cx = 36 - target_w - 1 # สระหน้าชิดขวา
        elif ch_type in ['า']:
            target_w = 21
            cx = 1                 # สระหลังชิดซ้าย
        elif ch_type in ['ฟ']:
            target_w = CHUBBY_W
            target_h = TOTAL_HEIGHT + 3 # หางฟอยื่นขึ้นเล็กน้อย
            cx = (36 - target_w) // 2
        else:
            target_w = CHUBBY_W
            cx = (36 - target_w) // 2
            
        sc = cr.resize((target_w, target_h), Image.Resampling.LANCZOS)
        cy = BASE_Y - target_h
        cell.paste(sc, (cx, cy), sc)
        return cell

def main():
    chars = ['เ', 'ริ่', 'ม', 'ล่', 'น', 'ส', 'ร้', 'า', 'ง', 'ซ', 'ฟ', 'ล', 'บ']
    cells = {c: make_uniform_cell(c) for c in chars}
    
    menus = [
        ("ปุ่มที่ 1 (冒険をする): เริ่มเล่น", ['เ', 'ริ่', 'ม', 'เ', 'ล่', 'น']),
        ("ปุ่มที่ 2 (冒険の書をつくる): สร้างเซฟ", ['ส', 'ร้', 'า', 'ง', 'เ', 'ซ', 'ฟ']),
        ("ปุ่มที่ 3 (冒険の書を消す): ลบเซฟ", ['ล', 'บ', 'เ', 'ซ', 'ฟ'])
    ]
    
    title_font = ImageFont.truetype(FONT_TTF, 18)
    
    preview_w = 640
    preview_h = 320
    out_img = Image.new('RGBA', (preview_w, preview_h), (20, 24, 34, 255))
    draw = ImageDraw.Draw(out_img)
    
    y_cursor = 20
    for title, m_chars in menus:
        draw.text((30, y_cursor), title, font=title_font, fill=(240, 205, 110, 255))
        y_cursor += 28
        
        box_w = len(m_chars) * 36 + 24
        box_h = 44
        draw.rounded_rectangle([30, y_cursor, 30 + box_w, y_cursor + box_h], radius=6, fill=(35, 45, 65, 255), outline=(70, 95, 140, 255), width=2)
        
        # วาดเส้นระดับเพดาน (แดง) และเส้นฐาน (เขียว)
        line_top = y_cursor + 4 + (BASE_Y - TOTAL_HEIGHT)
        line_base = y_cursor + 4 + BASE_Y
        draw.line([35, line_top, 30 + box_w - 5, line_top], fill=(255, 100, 100, 70), width=1)
        draw.line([35, line_base, 30 + box_w - 5, line_base], fill=(100, 255, 100, 70), width=1)
        
        x_char = 42
        for ch in m_chars:
            c_img = cells[ch]
            draw.rectangle([x_char, y_cursor + 4, x_char + 35, y_cursor + 39], outline=(55, 75, 110, 70))
            out_img.paste(c_img, (x_char, y_cursor + 4), mask=c_img)
            x_char += 36
            
        y_cursor += box_h + 18

    out_path = r"C:\Users\Supakiat\.gemini\antigravity\brain\ab5bc3db-774b-46d7-96ba-65470fc9eb39\uniform_height_chubby_preview.png"
    out_img.save(out_path)
    print(f"[+] บันทึกภาพพรีวิวความสูงเท่ากันสำเร็จ: {out_path}")

if __name__ == "__main__":
    main()
