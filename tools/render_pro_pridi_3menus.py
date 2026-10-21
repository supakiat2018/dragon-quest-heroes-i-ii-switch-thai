"""
render_pro_pridi_3menus.py
เรนเดอร์ 3 เมนู (เริ่มเล่น, สร้างเซฟ, ลบเซฟ) ด้วยฟอนต์ Pridi-Bold มาตรฐาน Option A
แบบเดียวกับภาพ "ชื่อตัวละครหลัก" ที่คมชัด สวยงาม สมบูรณ์แบบ 100%
"""

import os
import numpy as np
from PIL import Image, ImageFont, ImageDraw

BASE_DIR = r"D:\Game\dragon quest heroes i & ii"
FONT_TTF = os.path.join(BASE_DIR, "switch", "fonts", "Pridi-Bold.ttf")

f32 = ImageFont.truetype(FONT_TTF, 32)
f_vowel = ImageFont.truetype(FONT_TTF, 24)
f_tone = ImageFont.truetype(FONT_TTF, 22)
f_mark_stand = ImageFont.truetype(FONT_TTF, 26)

def get_glyph_crop(ch, font):
    t = Image.new('RGBA', (80, 80), (0, 0, 0, 0))
    ImageDraw.Draw(t).text((40, 55), ch, font=font, fill=(255, 255, 255, 255), anchor='ms')
    arr = np.array(t)[:, :, 3]
    coords = np.argwhere(arr > 20)
    if len(coords) == 0:
        return Image.new('RGBA', (10, 10), (0, 0, 0, 0))
    return t.crop((coords[:, 1].min(), coords[:, 0].min(), coords[:, 1].max() + 1, coords[:, 0].max() + 1))

def render_cell(ch_type):
    cell = Image.new('RGBA', (36, 36), (0, 0, 0, 0))
    
    # 1. คลัสเตอร์ 3 ชั้น: เริ่ (เ + ร + ิ + ่)
    if ch_type == 'เริ่':
        target_w = 32
        cr_e = get_glyph_crop('เ', f32)
        cr_r = get_glyph_crop('ร', f32)
        cr_v = get_glyph_crop('ิ', f_vowel)
        cr_t = get_glyph_crop('่', f_tone)
        
        can = Image.new('RGBA', (80, 80), (0, 0, 0, 0))
        y_base = 33
        # เ
        can.paste(cr_e, (5, y_base - cr_e.height), cr_e)
        # ร
        x_r = 5 + cr_e.width + 1
        can.paste(cr_r, (x_r, y_base - cr_r.height), cr_r)
        # ิ ลอยเหนือ ร
        y_v = y_base - cr_r.height - cr_v.height + 4
        can.paste(cr_v, (x_r - 1, y_v), cr_v)
        # ่ ลอยเหนือ ิ
        y_t = y_v - cr_t.height + 3
        can.paste(cr_t, (x_r + cr_r.width - cr_t.width, y_t), cr_t)
        
        coords = np.argwhere(np.array(can)[:, :, 3] > 20)
        cr = can.crop((coords[:, 1].min(), coords[:, 0].min(), coords[:, 1].max() + 1, coords[:, 0].max() + 1))
        scale = target_w / float(cr.width)
        sc = cr.resize((target_w, int(round(cr.height * scale))), Image.Resampling.LANCZOS)
        cx = (36 - target_w) // 2
        cy = max(1, 33 - sc.height)
        cell.paste(sc, (cx, cy), sc)
        return cell

    # 2. คลัสเตอร์ 3 ชั้น: เล่ (เ + ล + ่)
    elif ch_type == 'เล่':
        target_w = 32
        cr_e = get_glyph_crop('เ', f32)
        cr_l = get_glyph_crop('ล', f32)
        cr_t = get_glyph_crop('่', f_tone)
        
        can = Image.new('RGBA', (80, 80), (0, 0, 0, 0))
        y_base = 33
        # เ
        can.paste(cr_e, (5, y_base - cr_e.height), cr_e)
        # ล
        x_l = 5 + cr_e.width + 1
        can.paste(cr_l, (x_l, y_base - cr_l.height), cr_l)
        # ่ ลอยเหนือ ล
        y_t = y_base - cr_l.height - cr_t.height + 4
        can.paste(cr_t, (x_l + cr_l.width - cr_t.width - 2, y_t), cr_t)
        
        coords = np.argwhere(np.array(can)[:, :, 3] > 20)
        cr = can.crop((coords[:, 1].min(), coords[:, 0].min(), coords[:, 1].max() + 1, coords[:, 0].max() + 1))
        scale = target_w / float(cr.width)
        sc = cr.resize((target_w, int(round(cr.height * scale))), Image.Resampling.LANCZOS)
        cx = (36 - target_w) // 2
        cy = max(1, 33 - sc.height)
        cell.paste(sc, (cx, cy), sc)
        return cell

    # 3. คลัสเตอร์: สร้า (ส + ร้ + า)
    elif ch_type == 'สร้า':
        target_w = 34
        cr_s = get_glyph_crop('ส', f32)
        cr_r = get_glyph_crop('ร', f32)
        cr_t = get_glyph_crop('้', f_tone)
        cr_a = get_glyph_crop('า', f32)
        
        can = Image.new('RGBA', (100, 80), (0, 0, 0, 0))
        y_base = 33
        # ส
        can.paste(cr_s, (2, y_base - cr_s.height), cr_s)
        # ร
        x_r = 2 + cr_s.width + 1
        can.paste(cr_r, (x_r, y_base - cr_r.height), cr_r)
        # ้
        y_t = y_base - cr_r.height - cr_t.height + 4
        can.paste(cr_t, (x_r + cr_r.width - cr_t.width - 1, y_t), cr_t)
        # า
        x_a = x_r + cr_r.width + 1
        can.paste(cr_a, (x_a, y_base - cr_a.height), cr_a)
        
        coords = np.argwhere(np.array(can)[:, :, 3] > 20)
        cr = can.crop((coords[:, 1].min(), coords[:, 0].min(), coords[:, 1].max() + 1, coords[:, 0].max() + 1))
        scale = target_w / float(cr.width)
        sc = cr.resize((target_w, int(round(cr.height * scale))), Image.Resampling.LANCZOS)
        cx = (36 - target_w) // 2
        cy = max(1, 33 - sc.height)
        cell.paste(sc, (cx, cy), sc)
        return cell

    # 4. คลัสเตอร์: เซ (เ + ซ)
    elif ch_type == 'เซ':
        target_w = 30
        cr_e = get_glyph_crop('เ', f32)
        cr_s = get_glyph_crop('ซ', f32)
        
        can = Image.new('RGBA', (80, 80), (0, 0, 0, 0))
        y_base = 33
        can.paste(cr_e, (5, y_base - cr_e.height), cr_e)
        can.paste(cr_s, (5 + cr_e.width + 1, y_base - cr_s.height), cr_s)
        
        coords = np.argwhere(np.array(can)[:, :, 3] > 20)
        cr = can.crop((coords[:, 1].min(), coords[:, 0].min(), coords[:, 1].max() + 1, coords[:, 0].max() + 1))
        scale = target_w / float(cr.width)
        sc = cr.resize((target_w, int(round(cr.height * scale))), Image.Resampling.LANCZOS)
        cx = (36 - target_w) // 2
        cy = max(1, 33 - sc.height)
        cell.paste(sc, (cx, cy), sc)
        return cell

    # 5. พยัญชนะเดี่ยว: ม, น, ง, ฟ, ล, บ
    else:
        cr = get_glyph_crop(ch_type, f32)
        target_w = 28 if cr.width > 18 else 22
        scale_x = target_w / float(cr.width)
        scale_y = 26 / float(cr.height)
        nw = target_w
        nh = int(round(cr.height * scale_y))
        sc = cr.resize((nw, nh), Image.Resampling.LANCZOS)
        
        cx = (36 - nw) // 2
        cy = max(1, 33 - nh)
        cell.paste(sc, (cx, cy), sc)
        return cell

def main():
    chars = ['เริ่', 'ม', 'เล่', 'น', 'สร้า', 'ง', 'เซ', 'ฟ', 'ล', 'บ']
    cells = {c: render_cell(c) for c in chars}
    
    menus = [
        ("ปุ่มที่ 1 (冒険をする): เริ่มเล่น", ['เริ่', 'ม', 'เล่', 'น']),
        ("ปุ่มที่ 2 (冒険の書をつくる): สร้างเซฟ", ['สร้า', 'ง', 'เซ', 'ฟ']),
        ("ปุ่มที่ 3 (冒険の書を消す): ลบเซฟ", ['ล', 'บ', 'เซ', 'ฟ'])
    ]
    
    font_path = r"C:\Windows\Fonts\leelawad.ttf"
    title_font = ImageFont.truetype(font_path, 18)
    
    preview_w = 600
    preview_h = 320
    out_img = Image.new('RGBA', (preview_w, preview_h), (20, 24, 34, 255))
    draw = ImageDraw.Draw(out_img)
    
    y_cursor = 25
    for title, m_chars in menus:
        draw.text((30, y_cursor), title, font=title_font, fill=(240, 205, 110, 255))
        y_cursor += 30
        
        box_w = len(m_chars) * 36 + 30
        box_h = 44
        draw.rounded_rectangle([30, y_cursor, 30 + box_w, y_cursor + box_h], radius=6, fill=(35, 45, 65, 255), outline=(70, 95, 140, 255), width=2)
        
        x_char = 45
        for ch in m_chars:
            c_img = cells[ch]
            draw.rectangle([x_char, y_cursor + 4, x_char + 35, y_cursor + 39], outline=(55, 75, 110, 140))
            out_img.paste(c_img, (x_char, y_cursor + 4), mask=c_img)
            x_char += 36
            
        y_cursor += box_h + 20

    out_path = r"C:\Users\Supakiat\.gemini\antigravity\brain\ab5bc3db-774b-46d7-96ba-65470fc9eb39\pridi_bold_3menus_perfect.png"
    out_img.save(out_path)
    print(f"[+] บันทึกภาพพรีวิว Pridi-Bold สำเร็จ: {out_path}")

if __name__ == "__main__":
    main()
