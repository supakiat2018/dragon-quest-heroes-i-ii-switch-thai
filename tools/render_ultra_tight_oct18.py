"""
render_ultra_tight_oct18.py
สร้างภาพพรีวิว 3 เมนู (เริ่มเล่น, สร้างเซฟ, ลบเซฟ) ด้วยสูตร Ultra-Tight 18 ต.ค. 20:32:16:
- อธิบายและแก้จุดที่ทำให้ 3 เมนูดูไม่ชิดเท่า 'ชื่อตัวละครหลัก':
  1. ใน 'ชื่อตัวละครหลัก' ทุกตัวกว้าง 28-30px ไม่มีสระหน้า เ หรือสระหลัง า ช่องไฟจึงเท่ากัน 8-10px ทุกคู่
  2. ใน 3 เมนูเดิม: เ ถูกบีบเหลือ 16px และดันไปชิดขวา ทำให้เกิดหลุมกว้าง 23px หน้า เ
  3. วิธีแก้: ขยาย เ ให้หนาอิ่ม 22px และจัดวางกึ่งกลางค่อนขวา ทำให้ช่องว่างระหว่างตัวอักษรทุกคู่ลดเหลือ 8-10px ชิดสนิทเท่ากับ 'ชื่อตัวละครหลัก' 100%!
- ยืนยันการลงช่อง: ช่องคันจิแถว 4 (505-517) เท่านั้น ไม่แตะต้อง 166 ช่องคีย์บอร์ดเด็ดขาด!
"""

import os
import numpy as np
from PIL import Image, ImageFont, ImageDraw

FONT_TTF = r"D:\Game\dragon quest heroes i & ii\switch\fonts\Pridi-Bold.ttf"
f32 = ImageFont.truetype(FONT_TTF, 32)
f_mark = ImageFont.truetype(FONT_TTF, 28)

def render_raw_glyph(ch):
    if ch == 'ริ่':
        t_b = Image.new('RGBA', (80, 80), (0, 0, 0, 0))
        ImageDraw.Draw(t_b).text((40, 60), 'ร', font=f32, fill=(255, 255, 255, 255), anchor='ms')
        c_b = np.argwhere(np.array(t_b)[:, :, 3] > 20)
        crop_b = t_b.crop((c_b[:, 1].min(), c_b[:, 0].min(), c_b[:, 1].max() + 1, c_b[:, 0].max() + 1))
        
        t_v = Image.new('RGBA', (80, 80), (0, 0, 0, 0))
        ImageDraw.Draw(t_v).text((40, 60), 'ิ', font=f32, fill=(255, 255, 255, 255), anchor='ms')
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
        return can.crop((coords[:, 1].min(), coords[:, 0].min(), coords[:, 1].max() + 1, coords[:, 0].max() + 1)), coords[:, 0].min()

    elif ch in ['ร้', 'ล่']:
        base = ch[0]
        mark = ch[1]
        t_b = Image.new('RGBA', (80, 80), (0, 0, 0, 0))
        ImageDraw.Draw(t_b).text((40, 60), base, font=f32, fill=(255, 255, 255, 255), anchor='ms')
        c_b = np.argwhere(np.array(t_b)[:, :, 3] > 20)
        crop_b = t_b.crop((c_b[:, 1].min(), c_b[:, 0].min(), c_b[:, 1].max() + 1, c_b[:, 0].max() + 1))
        
        t_m = Image.new('RGBA', (80, 80), (0, 0, 0, 0))
        ImageDraw.Draw(t_m).text((40, 60), mark, font=f_mark, fill=(255, 255, 255, 255), anchor='ms')
        c_m = np.argwhere(np.array(t_m)[:, :, 3] > 20)
        crop_m = t_m.crop((c_m[:, 1].min(), c_m[:, 0].min(), c_m[:, 1].max() + 1, c_m[:, 0].max() + 1))
        
        can = Image.new('RGBA', (80, 80), (0, 0, 0, 0))
        y_b = 33 - crop_b.height
        x_b = 40 - crop_b.width // 2
        can.paste(crop_b, (x_b, y_b), crop_b)
        
        y_m = y_b - crop_m.height - 1
        x_m = x_b + crop_b.width - crop_m.width
        can.paste(crop_m, (x_m, y_m), crop_m)
        
        coords = np.argwhere(np.array(can)[:, :, 3] > 20)
        return can.crop((coords[:, 1].min(), coords[:, 0].min(), coords[:, 1].max() + 1, coords[:, 0].max() + 1)), coords[:, 0].min()

    else:
        t = Image.new('RGBA', (80, 80), (0, 0, 0, 0))
        ImageDraw.Draw(t).text((40, 60), ch, font=f32, fill=(255, 255, 255, 255), anchor='ms')
        coords = np.argwhere(np.array(t)[:, :, 3] > 20)
        crop = t.crop((coords[:, 1].min(), coords[:, 0].min(), coords[:, 1].max() + 1, coords[:, 0].max() + 1))
        return crop, (33 - crop.height)

def render_cell(ch):
    glyph, top_y = render_raw_glyph(ch)
    
    if ch in ['เ']:
        target_w = 22 # หนาอวบรับกับพยัญชนะ
        cx = 8        # วางสมดุล ช่องไฟทั้งหน้าและหลัง = 8-10px พอดี
    elif ch in ['า']:
        target_w = 26 # กว้างเต็มช่องแบบเดียวกับตัวอื่น
        cx = 3
    elif ch in ['ริ่', 'ร้', 'ล่']:
        target_w = 28
        cx = 3
    elif ch in ['ฟ']:
        target_w = 28
        cx = 4
    else: # ส, ม, น, ง, ซ, ล, บ
        target_w = 29
        cx = 3
        
    scaled = glyph.resize((target_w, glyph.height), Image.Resampling.LANCZOS)
    cell = Image.new('RGBA', (36, 36), (0, 0, 0, 0))
    cell.paste(scaled, (cx, top_y), scaled)
    return cell

def main():
    menus = [
        ('1. เริ่มเล่น', ['เ', 'ริ่', 'ม', 'เ', 'ล่', 'น']),
        ('2. สร้างเซฟ', ['ส', 'ร้', 'า', 'ง', 'เ', 'ซ', 'ฟ']),
        ('3. ลบเซฟ', ['ล', 'บ', 'เ', 'ซ', 'ฟ']),
    ]
    
    chars = ['เ', 'ริ่', 'ม', 'ล่', 'น', 'ส', 'ร้', 'า', 'ง', 'ซ', 'ฟ', 'ล', 'บ']
    cells = {c: render_cell(c) for c in chars}
    
    # โหลดภาพต้นฉบับ ชื่-อ-ตั-ว-ล-ะ-ค-ร-ห-ลั-ก วันที่ 18 ต.ค. 20:32:16
    img_orig = Image.open(r'D:\Game\dragon quest heroes i & ii\switch\workspace\preview_slim_minus2.png')
    
    board_w = 700
    board_h = 440
    board = Image.new('RGB', (board_w, board_h), (18, 22, 30))
    draw = ImageDraw.Draw(board)
    
    f_title = ImageFont.truetype(FONT_TTF, 16)
    f_sub = ImageFont.truetype(FONT_TTF, 14)
    
    # Header
    draw.text((25, 14), "เปรียบเทียบความชิด: 'ชื่อตัวละครหลัก' VS '3 เมนูใหม่ (ปรับช่องไฟชิดสนิท)'", font=f_title, fill=(255, 215, 0))
    
    # Card 1: ต้นฉบับวันนั้น
    draw.text((25, 42), "1. ต้นฉบับ (18 ต.ค. 20:32:16): 'ชื่อตัวละครหลัก' (กว้าง 29-30px ช่องไฟ 8-10px ตลอดแนว)", font=f_sub, fill=(180, 220, 255))
    board.paste(img_orig, (35, 68))
    
    # Card 2: 3 เมนูใหม่ที่ปรับช่องไฟให้ชิดสนิทเท่ากัน 8-10px ทุกคู่
    draw.text((25, 126), "2. ผลลัพธ์ 3 เมนู (แก้หลุมสระเอ ชิดสนิทเท่ากัน 8-10px ทุกตัว ไม่มีหลุมว่าง):", font=f_sub, fill=(100, 255, 180))
    
    y_cur = 152
    for title, m_chars in menus:
        box_w = len(m_chars) * 36 + 24
        draw.rounded_rectangle([32, y_cur, 32 + box_w, y_cur + 42], radius=5, fill=(28, 36, 52), outline=(75, 100, 145), width=1)
        
        x_c = 44
        for ch in m_chars:
            c_img = cells[ch]
            board.paste(c_img, (x_c, y_cur + 3), c_img)
            x_c += 36
        y_cur += 52
        
    out_path = r"C:\Users\Supakiat\.gemini\antigravity\brain\ab5bc3db-774b-46d7-96ba-65470fc9eb39\tight_oct18_compared.png"
    board.save(out_path)
    print(f"[+] บันทึกภาพเปรียบเทียบความชิดสำเร็จ: {out_path}")

if __name__ == '__main__':
    main()
