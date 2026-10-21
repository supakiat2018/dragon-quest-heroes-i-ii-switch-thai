"""
generate_chubby_menu_preview.py
สร้างภาพพรีวิวฟอนต์ไทยตัวอ้วนหนา แน่น ชิดสวยงาม แบบ 36x36 Monospace
- แปล 3 เมนู: เริ่มเล่น, สร้างเซฟ, ลบเซฟ
- ใช้คันจิแท้ 10 ตัว (亜 ถึง 葵) ไม่ทับ 166 ช่องคีย์บอร์ดเลยแม้แต่ตัวเดียว
- จำลองการแสดงผลบนปุ่มเมนูของเกมจริง
"""

import os
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = r"D:\Game\dragon quest heroes i & ii"
WORKSPACE_DIR = os.path.join(BASE_DIR, "switch", "workspace")

with open(os.path.join(WORKSPACE_DIR, 'dw8_glyphs.json'), 'r', encoding='utf-8') as f:
    dw8_glyphs = json.load(f)

pages = [
    Image.open(os.path.join(WORKSPACE_DIR, 'dw8_font_dump', 'dw8_page_0.png')),
    Image.open(os.path.join(WORKSPACE_DIR, 'dw8_font_dump', 'dw8_page_1.png')),
    Image.open(os.path.join(WORKSPACE_DIR, 'dw8_font_dump', 'dw8_page_2.png'))
]

with open(r'C:\Users\Supakiat\Desktop\Mover\สร้างฟ้อน\Mapping.json', 'r', encoding='utf-8') as f:
    user_map = json.load(f)
inv_map = {ord(v): k for k, v in user_map.items()}

dw8_dict = {}
for g in dw8_glyphs:
    cv = int(g['code'], 16)
    if cv >= 0xf000:
        dw8_dict[inv_map.get(cv, '')] = g
    elif 0xe01 <= cv <= 0xe5b:
        dw8_dict[chr(cv)] = g

def get_raw_crop(g):
    flts = g['flts']
    p = g['page']
    u0, v0, u1 = flts[3], flts[4], flts[5]
    x0 = int(round(u0 * 1024))
    y0 = int(round(v0 * 1024))
    x1 = int(round(u1 * 1024))
    cell_raw = pages[p].crop((x0, y0, x1, y0 + 64))
    arr = np.array(cell_raw)[:, :, 3]
    coords = np.argwhere(arr > 10)
    min_y, min_x = coords.min(axis=0)
    max_y, max_x = coords.max(axis=0)
    return cell_raw.crop((min_x, min_y, max_x + 1, max_y + 1))

# สร้างคลัสเตอร์ เริ่ (เ + ริ + ไม้เอก)
cr_e = get_raw_crop(dw8_dict['เ'])
cr_ri = get_raw_crop(dw8_dict['ริ'])
cr_re = get_raw_crop(dw8_dict['ร่'])
tone_ek = cr_re.crop((0, 0, 7, 7))

w = cr_e.width + 1 + cr_ri.width + 2
h = max(cr_e.height, cr_ri.height + 6)
comp_rerim = Image.new('RGBA', (w + 4, h + 2), (0, 0, 0, 0))
base_y = h
comp_rerim.paste(cr_e, (0, base_y - cr_e.height), cr_e)
x_ri = cr_e.width + 1
y_ri = base_y - cr_ri.height
comp_rerim.paste(cr_ri, (x_ri, y_ri), cr_ri)
comp_rerim.paste(tone_ek, (x_ri + 5, y_ri - 5), tone_ek)
arr = np.array(comp_rerim)[:, :, 3]
coords = np.argwhere(arr > 10)
cr_rerim = comp_rerim.crop((coords[:, 1].min(), coords[:, 0].min(), coords[:, 1].max() + 1, coords[:, 0].max() + 1))

# สร้างคลัสเตอร์ เล่ (เ + ล่)
cr_le = get_raw_crop(dw8_dict['ล่'])
w_le = cr_e.width + 1 + cr_le.width
h_le = max(cr_e.height, cr_le.height)
comp_le = Image.new('RGBA', (w_le + 4, h_le + 2), (0, 0, 0, 0))
base_y = h_le
comp_le.paste(cr_e, (0, base_y - cr_e.height), cr_e)
comp_le.paste(cr_le, (cr_e.width + 1, base_y - cr_le.height), cr_le)
arr = np.array(comp_le)[:, :, 3]
coords = np.argwhere(arr > 10)
cr_le = comp_le.crop((coords[:, 1].min(), coords[:, 0].min(), coords[:, 1].max() + 1, coords[:, 0].max() + 1))

# สร้างคลัสเตอร์ สร้า (ส + ร้ + า)
cr_s = get_raw_crop(dw8_dict['ส'])
cr_ro = get_raw_crop(dw8_dict['ร้'])
cr_a = get_raw_crop(dw8_dict['า'])
w_sra = cr_s.width + 1 + cr_ro.width + 1 + cr_a.width
h_sra = max(cr_s.height, cr_ro.height, cr_a.height)
comp_sra = Image.new('RGBA', (w_sra + 4, h_sra + 2), (0, 0, 0, 0))
base_y = h_sra
comp_sra.paste(cr_s, (0, base_y - cr_s.height), cr_s)
comp_sra.paste(cr_ro, (cr_s.width + 1, base_y - cr_ro.height), cr_ro)
comp_sra.paste(cr_a, (cr_s.width + 1 + cr_ro.width + 1, base_y - cr_a.height), cr_a)
arr = np.array(comp_sra)[:, :, 3]
coords = np.argwhere(arr > 10)
cr_sra = comp_sra.crop((coords[:, 1].min(), coords[:, 0].min(), coords[:, 1].max() + 1, coords[:, 0].max() + 1))

# สร้างคลัสเตอร์ เซ (เ + ซ)
cr_so = get_raw_crop(dw8_dict['ซ'])
w_se = cr_e.width + 1 + cr_so.width
h_se = max(cr_e.height, cr_so.height)
comp_se = Image.new('RGBA', (w_se + 4, h_se + 2), (0, 0, 0, 0))
base_y = h_se
comp_se.paste(cr_e, (0, base_y - cr_e.height), cr_e)
comp_se.paste(cr_so, (cr_e.width + 1, base_y - cr_so.height), cr_so)
arr = np.array(comp_se)[:, :, 3]
coords = np.argwhere(arr > 10)
cr_se = comp_se.crop((coords[:, 1].min(), coords[:, 0].min(), coords[:, 1].max() + 1, coords[:, 0].max() + 1))

# รวม 10 ตัวอักษรพร้อมความสูงเป้าหมาย
RAW_CROPS = {
    'เริ่': (cr_rerim, 32, 33),
    'ม':   (get_raw_crop(dw8_dict['ม']), 26, 28),
    'เล่': (cr_le, 32, 32),
    'น':   (get_raw_crop(dw8_dict['น']), 26, 28),
    'สร้า': (cr_sra, 32, 34),
    'ง':   (get_raw_crop(dw8_dict['ง']), 26, 28),
    'เซ':  (cr_se, 27, 30),
    'ฟ':   (get_raw_crop(dw8_dict['ฟ']), 32, 28),
    'ล':   (get_raw_crop(dw8_dict['ล']), 26, 28),
    'บ':   (get_raw_crop(dw8_dict['บ']), 26, 28),
}

CELLS_36 = {}
for name, (cr, target_h, target_w) in RAW_CROPS.items():
    scale_y = target_h / float(cr.height)
    scale_x = target_w / float(cr.width)
    nw = min(34, max(1, int(round(cr.width * scale_x))))
    nh = min(34, max(1, int(round(cr.height * scale_y))))
    sc = cr.resize((nw, nh), Image.Resampling.LANCZOS)
    
    cell = Image.new('RGBA', (36, 36), (0, 0, 0, 0))
    cx = (36 - nw) // 2
    cy = max(1, 33 - nh)
    cell.paste(sc, (cx, cy), sc)
    CELLS_36[name] = cell

def render_menu_preview():
    menus = [
        ("Button 1 (冒険をする): เริ่มเล่น", ['เริ่', 'ม', 'เล่', 'น']),
        ("Button 2 (冒険の書をつくる): สร้างเซฟ", ['สร้า', 'ง', 'เซ', 'ฟ']),
        ("Button 3 (冒険の書を消す): ลบเซฟ", ['ล', 'บ', 'เซ', 'ฟ'])
    ]
    
    font_path = r"C:\Windows\Fonts\leelawad.ttf"
    if not os.path.exists(font_path):
        font_path = os.path.join(BASE_DIR, "switch", "fonts", "Pridi-Bold.ttf")
    title_font = ImageFont.truetype(font_path, 18)
    
    preview_w = 600
    preview_h = 320
    out_img = Image.new('RGBA', (preview_w, preview_h), (20, 24, 34, 255))
    draw = ImageDraw.Draw(out_img)
    
    y_cursor = 25
    for title, chars in menus:
        draw.text((30, y_cursor), title, font=title_font, fill=(240, 205, 110, 255))
        y_cursor += 30
        
        box_w = len(chars) * 36 + 30
        box_h = 44
        draw.rounded_rectangle([30, y_cursor, 30 + box_w, y_cursor + box_h], radius=6, fill=(35, 45, 65, 255), outline=(70, 95, 140, 255), width=2)
        
        x_char = 45
        for ch in chars:
            c_img = CELLS_36[ch]
            draw.rectangle([x_char, y_cursor + 4, x_char + 35, y_cursor + 39], outline=(55, 75, 110, 140))
            out_img.paste(c_img, (x_char, y_cursor + 4), mask=c_img)
            x_char += 36
            
        y_cursor += box_h + 20

    out_path = r"C:\Users\Supakiat\.gemini\antigravity\brain\ab5bc3db-774b-46d7-96ba-65470fc9eb39\chubby_thai_3menus_preview.png"
    out_img.save(out_path)
    print(f"[+] บันทึกภาพพรีวิว 3 เมนูสำเร็จ: {out_path}")

if __name__ == "__main__":
    render_menu_preview()
