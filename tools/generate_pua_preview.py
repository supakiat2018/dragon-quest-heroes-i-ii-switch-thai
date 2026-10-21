import sys, os
from PIL import Image, ImageDraw, ImageFont
import numpy as np

FONT_TTF = r'D:\Game\dragon quest heroes i & ii\switch\fonts\Pridi-Bold.ttf'
f32 = ImageFont.truetype(FONT_TTF, 32)
f_mark = ImageFont.truetype(FONT_TTF, 28)
font_title = ImageFont.truetype(r'C:\Windows\Fonts\tahomabd.ttf', 20)
font_desc = ImageFont.truetype(r'C:\Windows\Fonts\tahoma.ttf', 13)
font_label = ImageFont.truetype(r'C:\Windows\Fonts\tahoma.ttf', 12)

UPPER_MARKS = set('\u0e31\u0e34\u0e35\u0e36\u0e37\u0e4d')
LOWER_MARKS = set('\u0e38\u0e39\u0e3a')
TONE_MARKS  = set('\u0e48\u0e49\u0e4a\u0e4b\u0e4c\u0e47')

def get_glyph_crop(ch):
    font = f_mark if (ch in UPPER_MARKS or ch in LOWER_MARKS or ch in TONE_MARKS) else f32
    t = Image.new('RGBA', (80, 80), (0, 0, 0, 0))
    if ch in UPPER_MARKS or ch in TONE_MARKS:
        ImageDraw.Draw(t).text((40, 44), ch, font=font, fill=(255, 255, 255, 255), anchor='ms')
    elif ch in LOWER_MARKS:
        ImageDraw.Draw(t).text((40, 76), ch, font=font, fill=(255, 255, 255, 255), anchor='ms')
    else:
        ImageDraw.Draw(t).text((40, 60), ch, font=font, fill=(255, 255, 255, 255), anchor='ms')
    coords = np.argwhere(np.array(t)[:, :, 3] > 20)
    if len(coords) == 0: return Image.new('RGBA', (5, 5), (0, 0, 0, 0))
    return t.crop((coords[:, 1].min(), coords[:, 0].min(), coords[:, 1].max() + 1, coords[:, 0].max() + 1))

def compose_pua_layer(lead='เ', base='ร', up='ิ', tone='่',
                      lead_adj=(0, 0, 0, 0), base_adj=(0, 0, 0, 0),
                      up_adj=(0, 0, 0, 0), tone_adj=(0, 0, 0, 0)):
    cell = Image.new('RGBA', (36, 36), (0, 0, 0, 0))
    can = Image.new('RGBA', (80, 80), (0, 0, 0, 0))
    
    # 1. Lead (e.g. เ)
    cr_l = get_glyph_crop(lead)
    lw = max(4, cr_l.width + lead_adj[2])
    lh = max(4, cr_l.height + lead_adj[3])
    sc_l = cr_l.resize((lw, lh), Image.Resampling.LANCZOS)
    x_l = 20 + lead_adj[0]
    y_l = 40 - lh + lead_adj[1]
    can.paste(sc_l, (x_l, y_l), sc_l)
    
    # 2. Base (e.g. ร)
    cr_b = get_glyph_crop(base)
    bw = max(4, cr_b.width + base_adj[2])
    bh = max(4, cr_b.height + base_adj[3])
    sc_b = cr_b.resize((bw, bh), Image.Resampling.LANCZOS)
    x_b = x_l + lw + 1 + base_adj[0]
    y_b = 40 - bh + base_adj[1]
    can.paste(sc_b, (x_b, y_b), sc_b)
    
    # 3. Up mark (e.g. ิ)
    y_top = y_b
    if up:
        cr_u = get_glyph_crop(up)
        uw = max(4, cr_u.width + up_adj[2])
        uh = max(4, cr_u.height + up_adj[3])
        sc_u = cr_u.resize((uw, uh), Image.Resampling.LANCZOS)
        x_u = x_b + (bw - uw)//2 + up_adj[0]
        y_u = y_b - uh + 2 + up_adj[1]
        can.paste(sc_u, (x_u, y_u), sc_u)
        y_top = y_u
        
    # 4. Tone mark (e.g. ่)
    if tone:
        cr_t = get_glyph_crop(tone)
        tw = max(4, cr_t.width + tone_adj[2])
        th = max(4, cr_t.height + tone_adj[3])
        sc_t = cr_t.resize((tw, th), Image.Resampling.LANCZOS)
        x_t = x_b + bw - tw - 1 + tone_adj[0]
        y_t = y_top - th - 1 + tone_adj[1]
        can.paste(sc_t, (x_t, y_t), sc_t)
        
    coords = np.argwhere(np.array(can)[:, :, 3] > 20)
    if len(coords) == 0: return cell
    crop = can.crop((coords[:, 1].min(), coords[:, 0].min(), coords[:, 1].max() + 1, coords[:, 0].max() + 1))
    
    # Fit into 36x36 cell
    scale_fit = min(1.0, 32.0 / max(crop.width, 1), 32.0 / max(crop.height, 1))
    fw = int(crop.width * scale_fit)
    fh = int(crop.height * scale_fit)
    scaled_cell = crop.resize((fw, fh), Image.Resampling.LANCZOS)
    
    cx = (36 - fw) // 2
    cy = (36 - fh) // 2
    cell.paste(scaled_cell, (cx, cy), scaled_cell)
    return cell

canvas = Image.new('RGB', (1050, 480), (22, 26, 36))
draw = ImageDraw.Draw(canvas)

draw.text((30, 20), 'ฟีเจอร์ใหม่: ระบบรวม PUA แบบแยกเลเยอร์อิสระ (Multi-Layer PUA Composer)', font=font_title, fill=(255, 215, 0))
draw.text((30, 55), 'ในตัวผสมอย่าง "เริ่" คุณสามารถปรับตำแหน่งและขนาดของ เ, ร, ิ, ่ แต่ละตัวแยกกันได้ 100% ตามใจชอบ', font=font_desc, fill=(180, 210, 255))

variations = [
    ('1. ค่าเริ่มต้นธรรมชาติ', '(Natural)', (0,0,0,0), (0,0,0,0), (0,0,0,0), (0,0,0,0)),
    ('2. สระ เ ชิด ร + ร อ้วนขึ้น', '(Tighter เ & Chubby ร)', (2,0,0,0), (0,0,2,0), (0,0,0,0), (0,0,0,0)),
    ('3. ยก ิ สูง + ่ หลบขวา', '(Raised ิ & Shifted ่)', (0,0,0,0), (0,0,0,0), (0,-3,0,0), (3,-4,0,0)),
    ('4. ปรับแต่งรวมสมบูรณ์แบบ', '(Fully Tuned)', (2,0,0,0), (0,0,1,0), (1,-2,0,0), (3,-3,0,0))
]

xc = 30
for title, sub, l_adj, b_adj, u_adj, t_adj in variations:
    cell = compose_pua_layer(lead_adj=l_adj, base_adj=b_adj, up_adj=u_adj, tone_adj=t_adj)
    cell_big = cell.resize((36 * 5, 36 * 5), Image.Resampling.NEAREST)
    
    draw.rectangle([xc, 95, xc + 180 + 20, 95 + 180 + 20], fill=(16, 20, 30), outline=(60, 90, 140), width=1)
    draw.line([xc + 10, 95 + 10 + 6*5, xc + 190, 95 + 10 + 6*5], fill=(220, 50, 50, 120), width=1)
    draw.line([xc + 10, 95 + 10 + 32*5, xc + 190, 95 + 10 + 32*5], fill=(50, 220, 100, 120), width=1)
    canvas.paste(cell_big, (xc + 10, 95 + 10), cell_big)
    
    draw.text((xc, 305), title, font=font_label, fill=(255, 230, 140))
    draw.text((xc, 325), sub, font=font_desc, fill=(160, 190, 230))
    xc += 245

draw.text((30, 370), 'ตัวอย่างเมื่อนำไปแสดงผลในปุ่มเมนูเกมจริง (คำว่า "เริ่มเล่น"):', font=font_label, fill=(200, 220, 255))
btn_x = 30
cr_m = get_glyph_crop('ม')
cr_e = get_glyph_crop('เ')
cr_l = get_glyph_crop('ล')
cr_t = get_glyph_crop('่')
cr_n = get_glyph_crop('น')

# Compose 'ล่'
can_l = Image.new('RGBA', (36, 36), (0, 0, 0, 0))
can_l.paste(cr_l, ((36 - cr_l.width)//2, 32 - cr_l.height), cr_l)
can_l.paste(cr_t, ((36 - cr_l.width)//2 + cr_l.width - cr_t.width, 32 - cr_l.height - cr_t.height), cr_t)

for title, sub, l_adj, b_adj, u_adj, t_adj in variations:
    cell_eri = compose_pua_layer(lead_adj=l_adj, base_adj=b_adj, up_adj=u_adj, tone_adj=t_adj)
    
    btn = Image.new('RGB', (210, 48), (22, 35, 60))
    b_draw = ImageDraw.Draw(btn)
    b_draw.rectangle([0, 0, 209, 47], outline=(218, 165, 32), width=2)
    
    # [เริ่] [ม] [เ] [ล่] [น]
    btn.paste(cell_eri, (10, 6), cell_eri)
    
    m_box = Image.new('RGBA', (36, 36), (0, 0, 0, 0))
    m_box.paste(cr_m, ((36 - cr_m.width)//2, 32 - cr_m.height), cr_m)
    btn.paste(m_box, (48, 6), m_box)
    
    e_box = Image.new('RGBA', (36, 36), (0, 0, 0, 0))
    e_box.paste(cr_e, ((36 - cr_e.width)//2, 32 - cr_e.height), cr_e)
    btn.paste(e_box, (86, 6), e_box)
    
    btn.paste(can_l, (124, 6), can_l)
    
    n_box = Image.new('RGBA', (36, 36), (0, 0, 0, 0))
    n_box.paste(cr_n, ((36 - cr_n.width)//2, 32 - cr_n.height), cr_n)
    btn.paste(n_box, (162, 6), n_box)
    
    canvas.paste(btn, (btn_x, 395))
    btn_x += 245

out_path = r'C:\Users\Supakiat\.gemini\antigravity\brain\ab5bc3db-774b-46d7-96ba-65470fc9eb39\pua_multi_layer_preview.png'
canvas.save(out_path)
print('Saved multi-layer PUA preview to:', out_path)
