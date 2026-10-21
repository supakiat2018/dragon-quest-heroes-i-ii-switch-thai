"""
preview_pridi_pro_3menus.py
สร้างภาพพรีวิว 3 เมนู (เริ่มเล่น, สร้างเซฟ, ลบเซฟ) ด้วยฟอนต์ Pridi-Bold สูตรแท้ 100%
- ใช้ขนาดฟอนต์ 32-34pt และ WIDTH_SCALE = 1.32 (อ้วนหนาคมชัดระดับเดียวกับ 'ชื่อตัวละครหลัก')
- ทำการยกสระบนและวรรณยุกต์ลอยสูง (Option A) ไร้การเบียด
- จัดชิดช่องไฟ (Optical Kerning: สระหน้าชิดขวา สระหลังชิดซ้าย)
"""

import os
import numpy as np
from PIL import Image, ImageFont, ImageDraw

BASE_DIR = r"D:\Game\dragon quest heroes i & ii"
FONT_TTF = os.path.join(BASE_DIR, "switch", "fonts", "Pridi-Bold.ttf")

f34 = ImageFont.truetype(FONT_TTF, 34)
f32 = ImageFont.truetype(FONT_TTF, 32)
f_vowel = ImageFont.truetype(FONT_TTF, 22)
f_tone = ImageFont.truetype(FONT_TTF, 22)

WIDTH_SCALE = 1.30 # ขยายความกว้างให้อิ่มหนาเต็มช่อง

def get_glyph_crop(ch, font):
    t = Image.new('RGBA', (80, 80), (0, 0, 0, 0))
    ImageDraw.Draw(t).text((40, 55), ch, font=font, fill=(255, 255, 255, 255), anchor='ms')
    arr = np.array(t)[:, :, 3]
    coords = np.argwhere(arr > 20)
    if len(coords) == 0:
        return Image.new('RGBA', (10, 10), (0, 0, 0, 0))
    return t.crop((coords[:, 1].min(), coords[:, 0].min(), coords[:, 1].max() + 1, coords[:, 0].max() + 1))

def render_standalone(ch, align='center'):
    cell = Image.new('RGBA', (36, 36), (0, 0, 0, 0))
    t = Image.new('RGBA', (60, 60), (0, 0, 0, 0))
    ImageDraw.Draw(t).text((30, 48), ch, font=f34, fill=(255, 255, 255, 255), anchor='ms')
    coords = np.argwhere(np.array(t)[:, :, 3] > 20)
    if len(coords) == 0:
        return cell
    crop = t.crop((coords[:, 1].min(), coords[:, 0].min(), coords[:, 1].max() + 1, coords[:, 0].max() + 1))
    
    nw = int(round(crop.width * WIDTH_SCALE))
    nh = crop.height
    scaled = crop.resize((nw, nh), Image.Resampling.LANCZOS)
    
    # จัดชิดช่องไฟ (Optical Kerning)
    if align == 'left' or ch in ['ะ', 'า', 'ำ']:
        cx = 2
    elif align == 'right' or ch in ['เ', 'แ', 'โ', 'ใ', 'ไ']:
        cx = 36 - nw - 1
    else:
        cx = (36 - nw) // 2
        
    cy = 33 - nh
    cell.paste(scaled, (cx, cy), scaled)
    return cell

def render_cluster(base_ch, upper_vowel=None, tone=None, align='center'):
    cell = Image.new('RGBA', (36, 36), (0, 0, 0, 0))
    target_w = 28
    
    t_b = Image.new('RGBA', (80, 80), (0, 0, 0, 0))
    ImageDraw.Draw(t_b).text((40, 60), base_ch, font=f32, fill=(255, 255, 255, 255), anchor='ms')
    c_b = np.argwhere(np.array(t_b)[:, :, 3] > 20)
    crop_b = t_b.crop((c_b[:, 1].min(), c_b[:, 0].min(), c_b[:, 1].max() + 1, c_b[:, 0].max() + 1))
    
    can = Image.new('RGBA', (80, 80), (0, 0, 0, 0))
    y_b = 33 - crop_b.height
    x_b = 40 - crop_b.width // 2
    can.paste(crop_b, (x_b, y_b), crop_b)
    
    # สระบน (ลอยเหนือพยัญชนะ)
    y_v = y_b
    if upper_vowel:
        t_v = Image.new('RGBA', (80, 80), (0, 0, 0, 0))
        ImageDraw.Draw(t_v).text((40, 60), upper_vowel, font=f_vowel, fill=(255, 255, 255, 255), anchor='ms')
        c_v = np.argwhere(np.array(t_v)[:, :, 3] > 20)
        crop_v = t_v.crop((c_v[:, 1].min(), c_v[:, 0].min(), c_v[:, 1].max() + 1, c_v[:, 0].max() + 1))
        y_v = 7
        x_v = x_b + (crop_b.width - crop_v.width) // 2
        can.paste(crop_v, (x_v, y_v), crop_v)
        
    # วรรณยุกต์ (ลอยสูงสุดเพดาน ไร้การชน)
    if tone:
        t_t = Image.new('RGBA', (80, 80), (0, 0, 0, 0))
        ImageDraw.Draw(t_t).text((40, 60), tone, font=f_tone, fill=(255, 255, 255, 255), anchor='ms')
        c_t = np.argwhere(np.array(t_t)[:, :, 3] > 20)
        crop_t = t_t.crop((c_t[:, 1].min(), c_t[:, 0].min(), c_t[:, 1].max() + 1, c_t[:, 0].max() + 1))
        y_t = (y_v - crop_t.height - 1) if upper_vowel else (y_b - crop_t.height + 2)
        y_t = max(0, y_t)
        x_t = x_b + crop_b.width - crop_t.width
        can.paste(crop_t, (x_t, y_t), crop_t)
        
    coords = np.argwhere(np.array(can)[:, :, 3] > 20)
    cropped = can.crop((coords[:, 1].min(), coords[:, 0].min(), coords[:, 1].max() + 1, coords[:, 0].max() + 1))
    scale = target_w / float(cropped.width)
    scaled = cropped.resize((target_w, int(round(cropped.height * scale))), Image.Resampling.LANCZOS)
    
    if align == 'left':
        cx = 2
    else:
        cx = (36 - target_w) // 2
    cy = max(1, 33 - scaled.height)
    cell.paste(scaled, (cx, cy), scaled)
    return cell

def build_menu_preview():
    # สร้างเซลล์ 13 ตัว
    cells = {
        'เ': render_standalone('เ', align='right'),
        'ริ่': render_cluster('ร', 'ิ', '่', align='left'),
        'ม': render_standalone('ม', align='center'),
        'ล่': render_cluster('ล', None, '่', align='left'),
        'น': render_standalone('น', align='center'),
        'ส': render_standalone('ส', align='center'),
        'ร้': render_cluster('ร', None, '้', align='center'),
        'า': render_standalone('า', align='left'),
        'ง': render_standalone('ง', align='left'),
        'ซ': render_standalone('ซ', align='left'),
        'ฟ': render_standalone('ฟ', align='left'),
        'ล': render_standalone('ล', align='center'),
        'บ': render_standalone('บ', align='left'),
    }
    
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
        
        x_char = 42
        for ch in m_chars:
            c_img = cells[ch]
            draw.rectangle([x_char, y_cursor + 4, x_char + 35, y_cursor + 39], outline=(55, 75, 110, 100))
            out_img.paste(c_img, (x_char, y_cursor + 4), mask=c_img)
            x_char += 36
            
        y_cursor += box_h + 18

    out_path = r"C:\Users\Supakiat\.gemini\antigravity\brain\ab5bc3db-774b-46d7-96ba-65470fc9eb39\pridi_pure_3menus_preview.png"
    out_img.save(out_path)
    print(f"[+] บันทึกพรีวิวสำเร็จ: {out_path}")

if __name__ == "__main__":
    build_menu_preview()
