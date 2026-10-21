"""
generate_perfect_menu_preview.py
สร้างฟอนต์ 3 เมนูตามกฎเป๊ะๆ ของคุณ Supakiat:
"ก ต้อง กิ่ คือเท่า ก คือย่อ ก ลงมา และ ก เท่ากัน โดยสระบนหัวด้วย และต้องอ้วนเท่ากันอะ"

- Total Height: H = 26px (เพดาน Y=6, เส้นฐาน Y=32)
- ทุกตัวมีความสูงรวม 26px เท่ากันเป๊ะ 100%:
  1. ตัว 1 ชั้น (ก, ม, น, ง, บ, ส, ซ, ล, ฟ, เ, า): ตัวเต็ม สูง 26px
  2. ตัว 2 ชั้น (ร้, ล่): ย่อตัวพยัญชนะลงมา + วรรณยุกต์บนหัว = รวม 26px
  3. ตัว 3 ชั้น (ริ่, กิ่): ย่อตัวพยัญชนะลงมา + สระบน + วรรณยุกต์บนหัว = รวม 26px
- "อ้วนเท่ากัน": รักษาสัดส่วนลายเส้นให้อิ่มหนา (Bold) สม่ำเสมอ ไม่ลีบ ไม่เบี้ยว ไม่แบน
"""

import os
import numpy as np
from PIL import Image, ImageFont, ImageDraw, ImageFilter

FONT_PATH = r"D:\Game\dragon quest heroes i & ii\switch\fonts\Pridi-Bold.ttf"

BASE_Y = 32
TOP_Y = 6
H = BASE_Y - TOP_Y # 26px

def render_raw_glyph(ch, font_size, bold_extra=0):
    """เรนเดอร์ตัวอักษรดิบจาก Pridi-Bold พร้อมปรับความหนาลายเส้น"""
    f = ImageFont.truetype(FONT_PATH, font_size)
    # เรนเดอร์บน canvas ขนาดใหญ่
    t = Image.new('RGBA', (120, 120), (0, 0, 0, 0))
    d = ImageDraw.Draw(t)
    d.text((60, 60), ch, font=f, fill=(255, 255, 255, 255), anchor='mm',
           stroke_width=bold_extra, stroke_fill=(255, 255, 255, 255))
    
    arr = np.array(t)[:, :, 3]
    coords = np.argwhere(arr > 20)
    if len(coords) == 0:
        return Image.new('RGBA', (10, 10), (0, 0, 0, 0))
    ymin, xmin = coords.min(axis=0)
    ymax, xmax = coords.max(axis=0)
    return t.crop((xmin, ymin, xmax + 1, ymax + 1))

def make_cell(ch_type):
    cell = Image.new('RGBA', (36, 36), (0, 0, 0, 0))
    
    # ----------------------------------------------------
    # กลุ่ม 3 ชั้น: ริ่, กิ่ (รวม = H = 26px)
    # พยัญชนะ: สูง ~15px
    # สระบน (ิ): สูง ~5.5px
    # วรรณยุกต์ (่): สูง ~5.5px
    # ----------------------------------------------------
    if ch_type in ['ริ่', 'กิ่']:
        base_char = ch_type[0]
        # เพื่อให้อ้วนเท่ากัน: ใช้ bold_extra=1 บนตัวที่ย่อ
        cr_b = render_raw_glyph(base_char, 24, bold_extra=1)
        cr_v = render_raw_glyph('ิ', 20, bold_extra=1)
        cr_t = render_raw_glyph('่', 18, bold_extra=1)
        
        # ปรับความสูงองค์ประกอบ
        target_b_h = 15
        scale_b = target_b_h / float(cr_b.height)
        w_b = int(round(cr_b.width * scale_b * 1.15)) # อ้วนขึ้น 15%
        sc_b = cr_b.resize((w_b, target_b_h), Image.Resampling.LANCZOS)
        
        target_v_h = 6
        scale_v = target_v_h / float(cr_v.height)
        w_v = int(round(cr_v.width * scale_v))
        sc_v = cr_v.resize((w_v, target_v_h), Image.Resampling.LANCZOS)
        
        target_t_h = 5
        scale_t = target_t_h / float(cr_t.height)
        w_t = int(round(cr_t.width * scale_t))
        sc_t = cr_t.resize((w_t, target_t_h), Image.Resampling.LANCZOS)
        
        # ประกอบใน cell (ความสูงรวม = 15 + 6 + 5 = 26px พอดีเป๊ะ!)
        # ฐานอยู่ที่ BASE_Y = 32
        y_b = BASE_Y - target_b_h # 32 - 15 = 17
        y_v = y_b - target_v_h    # 17 - 6 = 11
        y_t = y_v - target_t_h    # 11 - 5 = 6 (= TOP_Y พอดีเป๊ะ!)
        
        # กึ่งกลางพยัญชนะ
        cx_b = (36 - w_b) // 2
        cx_v = cx_b + (w_b - w_v) // 2
        cx_t = cx_b + w_b - w_t - 1
        
        cell.paste(sc_b, (cx_b, y_b), sc_b)
        cell.paste(sc_v, (cx_v, y_v), sc_v)
        cell.paste(sc_t, (cx_t, y_t), sc_t)
        return cell

    # ----------------------------------------------------
    # กลุ่ม 2 ชั้น: ร้, ล่ (รวม = H = 26px)
    # พยัญชนะ: สูง ~18px
    # วรรณยุกต์: สูง ~8px
    # ----------------------------------------------------
    elif ch_type in ['ร้', 'ล่']:
        base_char = ch_type[0]
        tone_char = ch_type[1]
        
        cr_b = render_raw_glyph(base_char, 28, bold_extra=1)
        cr_t = render_raw_glyph(tone_char, 22, bold_extra=1)
        
        target_b_h = 18
        scale_b = target_b_h / float(cr_b.height)
        w_b = int(round(cr_b.width * scale_b * 1.15))
        sc_b = cr_b.resize((w_b, target_b_h), Image.Resampling.LANCZOS)
        
        target_t_h = 8
        scale_t = target_t_h / float(cr_t.height)
        w_t = int(round(cr_t.width * scale_t))
        sc_t = cr_t.resize((w_t, target_t_h), Image.Resampling.LANCZOS)
        
        # ประกอบใน cell (ความสูงรวม = 18 + 8 = 26px พอดีเป๊ะ!)
        y_b = BASE_Y - target_b_h # 32 - 18 = 14
        y_t = y_b - target_t_h    # 14 - 8 = 6 (= TOP_Y พอดีเป๊ะ!)
        
        cx_b = (36 - w_b) // 2
        cx_t = cx_b + w_b - w_t
        
        cell.paste(sc_b, (cx_b, y_b), sc_b)
        cell.paste(sc_t, (cx_t, y_t), sc_t)
        return cell

    # ----------------------------------------------------
    # กลุ่มสระหน้า: เ (สูง = H = 26px, ชิดขวาแนบพยัญชนะถัดไป)
    # ----------------------------------------------------
    elif ch_type == 'เ':
        cr = render_raw_glyph('เ', 44, bold_extra=0)
        scale = H / float(cr.height)
        w = int(round(cr.width * scale * 1.15))
        sc = cr.resize((w, H), Image.Resampling.LANCZOS)
        cx = 36 - w - 2 # ชิดขวา
        cell.paste(sc, (cx, TOP_Y), sc)
        return cell

    # ----------------------------------------------------
    # กลุ่มสระหลัง: า (สูง = H = 26px, ชิดซ้ายแนบพยัญชนะข้างหน้า)
    # ----------------------------------------------------
    elif ch_type == 'า':
        cr = render_raw_glyph('า', 44, bold_extra=0)
        scale = H / float(cr.height)
        w = int(round(cr.width * scale * 1.15))
        sc = cr.resize((w, H), Image.Resampling.LANCZOS)
        cx = 2 # ชิดซ้าย
        cell.paste(sc, (cx, TOP_Y), sc)
        return cell

    # ----------------------------------------------------
    # กลุ่มตัวหางยาว: ฟ (สูง = H = 26px พอดีเพดาน)
    # ----------------------------------------------------
    elif ch_type == 'ฟ':
        cr = render_raw_glyph('ฟ', 36, bold_extra=0)
        scale = H / float(cr.height)
        w = int(round(cr.width * scale * 1.15))
        sc = cr.resize((w, H), Image.Resampling.LANCZOS)
        cx = (36 - w) // 2
        cell.paste(sc, (cx, TOP_Y), sc)
        return cell

    # ----------------------------------------------------
    # กลุ่มตัวปกติ 1 ชั้น: ก, ม, น, ง, บ, ส, ซ, ล (สูง = H = 26px)
    # ----------------------------------------------------
    else:
        cr = render_raw_glyph(ch_type, 44, bold_extra=0)
        scale = H / float(cr.height)
        w = int(round(cr.width * scale * 1.12))
        w = min(28, w) # ไม่ให้อ้วนเกินขอบ cell
        sc = cr.resize((w, H), Image.Resampling.LANCZOS)
        cx = (36 - w) // 2
        cell.paste(sc, (cx, TOP_Y), sc)
        return cell

def main():
    test_chars = ['ก', 'กิ่', 'เ', 'ริ่', 'ม', 'ล่', 'น', 'ส', 'ร้', 'า', 'ง', 'ซ', 'ฟ', 'ล', 'บ']
    cells = {}
    print("--- Character Metrics ---")
    for c in test_chars:
        cells[c] = make_cell(c)
        arr = np.array(cells[c])[:, :, 3]
        coords = np.argwhere(arr > 20)
        ymin, xmin = coords.min(axis=0)
        ymax, xmax = coords.max(axis=0)
        print(f"Char '{c:2s}': y={ymin:2d}..{ymax:2d} (h={ymax-ymin+1:2d}), x={xmin:2d}..{xmax:2d} (w={xmax-xmin+1:2d})")

    # Render Preview Graphic
    preview_w = 720
    preview_h = 420
    img = Image.new('RGBA', (preview_w, preview_h), (18, 22, 32, 255))
    draw = ImageDraw.Draw(img)
    
    t_font = ImageFont.truetype(FONT_PATH, 16)
    sub_font = ImageFont.truetype(FONT_PATH, 13)
    
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
        # กรอบปุ่มเกมสีน้ำเงินเข้มสไตล์ Dragon Quest
        draw.rounded_rectangle([32, y_cur, 32 + box_w, y_cur + box_h], radius=7, 
                               fill=(28, 38, 56, 255), outline=(65, 95, 145, 255), width=2)
        
        # เส้นไกด์: สีแดง = เพดานบน (y=6), สีเขียว = เส้นฐานล่าง (y=32)
        line_top = y_cur + 4 + TOP_Y
        line_base = y_cur + 4 + BASE_Y
        draw.line([38, line_top, 32 + box_w - 6, line_top], fill=(255, 70, 70, 160), width=1)
        draw.line([38, line_base, 32 + box_w - 6, line_base], fill=(70, 255, 70, 160), width=1)
        
        x_char = 44
        for ch in sec_chars:
            c_img = cells[ch]
            # ช่องกรอบอักษร 36x36
            draw.rectangle([x_char, y_cur + 4, x_char + 35, y_cur + 39], outline=(50, 70, 105, 70))
            img.paste(c_img, (x_char, y_cur + 4), mask=c_img)
            x_char += 36
            
        y_cur += box_h + 16
        
    out_path = r"C:\Users\Supakiat\.gemini\antigravity\brain\ab5bc3db-774b-46d7-96ba-65470fc9eb39\perfect_chubby_uniform_preview.png"
    img.save(out_path)
    print(f"\n[+] บันทึกภาพพรีวิวสมบูรณ์แบบ: {out_path}")

if __name__ == '__main__':
    main()
