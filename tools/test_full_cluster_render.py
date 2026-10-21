import sys, os
from PIL import Image, ImageFont, ImageDraw

sys.path.append(r"D:\Game\dragon quest heroes i & ii\switch\tools")
from thai_font_preview_gui import compose_pua_cluster_image, get_glyph_crop, FONT_TTF, UPPER_MARKS, LOWER_MARKS, TONE_MARKS, LEAD_VOWELS, TRAIL_VOWELS

cfg = {}

def render_token_cell(tok_type, tok_val, lead_ox=8, trail_ox=-6, baseline=32):
    cell = Image.new('RGBA', (36, 36), (0, 0, 0, 0))
    if tok_type == 'SPACE':
        return cell
    if tok_type == 'LEAD':
        cr = get_glyph_crop(tok_val)
        cx = max(0, min(36 - cr.width, 36 - cr.width - 2 + (lead_ox - 8)))
        cy = baseline - cr.height
        cell.paste(cr, (cx, cy), cr)
    elif tok_type == 'TRAIL':
        cr = get_glyph_crop(tok_val)
        cx = max(0, min(36 - cr.width, 2 + (trail_ox + 6)))
        cy = baseline - cr.height
        cell.paste(cr, (cx, cy), cr)
    elif tok_type == 'BASE':
        cr = get_glyph_crop(tok_val)
        cx = (36 - cr.width) // 2
        cy = baseline - cr.height
        cell.paste(cr, (cx, cy), cr)
    else: # CLUSTER_*
        cell, _ = compose_pua_cluster_image(tok_val, cfg, baseline=baseline)
    return cell

def tokenize_full_thai(text):
    tokens = []
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if ch in LEAD_VOWELS:
            tokens.append(('LEAD', ch))
            i += 1
        elif ch in TRAIL_VOWELS:
            tokens.append(('TRAIL', ch))
            i += 1
        elif ch == ' ':
            tokens.append(('SPACE', ' '))
            i += 1
        else:
            combo = ch
            j = i + 1
            has_up = False
            has_low = False
            has_tone = False
            while j < n and (text[j] in UPPER_MARKS or text[j] in LOWER_MARKS or text[j] in TONE_MARKS):
                if text[j] in UPPER_MARKS: has_up = True
                if text[j] in LOWER_MARKS: has_low = True
                if text[j] in TONE_MARKS: has_tone = True
                combo += text[j]
                j += 1
            if len(combo) > 1:
                if has_up and has_tone: tokens.append(('CLUSTER_UP_TONE', combo))
                elif has_low and has_tone: tokens.append(('CLUSTER_LOW_TONE', combo))
                elif has_up: tokens.append(('CLUSTER_UP', combo))
                elif has_low: tokens.append(('CLUSTER_LOW', combo))
                elif has_tone: tokens.append(('CLUSTER_TONE', combo))
                else: tokens.append(('CLUSTER_OTHER', combo))
                i = j
            else:
                tokens.append(('BASE', ch))
                i += 1
    return tokens

img = Image.new('RGBA', (1100, 340), (18, 24, 38, 255))
draw = ImageDraw.Draw(img)

font_h1 = ImageFont.truetype(FONT_TTF, 18)
font_lbl = ImageFont.truetype(FONT_TTF, 12)
font_sub = ImageFont.truetype(FONT_TTF, 10)

draw.text((25, 15), "🌟 สูตรสมบูรณ์ (รวมข้อ 4 และ 5: สระและวรรณยุกต์ซ้อนบนหัวพยัญชนะ)", font=font_h1, fill=(245, 158, 11))
draw.text((25, 45), "สระหน้าชิดขวา + สระตามชิดซ้าย + พยัญชนะรวมร่างกับวรรณยุกต์และสระบน/ล่างในช่อง 36x36 เดียวกัน", font=font_lbl, fill=(148, 163, 184))

phrases = ["เริ่มเล่น", "สร้างเซฟ", "ลบเซฟ", "กินยา", "ผู้กล้า", "น้ำมนต์"]
xc = 25
yc = 85
for phrase in phrases:
    toks = tokenize_full_thai(phrase)
    cells = [render_token_cell(tt, tv) for (tt, tv) in toks]
    btn_w = len(cells) * 36 + 24
    draw.rectangle([xc, yc, xc + btn_w, yc + 52], fill=(22, 35, 60), outline=(218, 165, 32), width=2)
    draw.line([xc + 4, yc + 8, xc + btn_w - 4, yc + 8], fill=(220, 50, 50, 100), width=1)
    draw.line([xc + 4, yc + 44, xc + btn_w - 4, yc + 44], fill=(50, 120, 220, 100), width=1)
    
    x_char = xc + 12
    for cell in cells:
        draw.rectangle([x_char, yc + 8, x_char + 35, yc + 43], outline=(60, 80, 120, 80), width=1)
        img.paste(cell, (x_char, yc + 8), cell)
        x_char += 36
    xc += btn_w + 16

# Deconstruction of เริ่มเล่น
draw.text((25, 160), "ชำแหละเซลล์ 36x36 px ของคำว่า 'เริ่มเล่น' แบบรวมข้อ 4 และ 5:", font=font_lbl, fill=(253, 224, 71))

demo_toks = tokenize_full_thai("เริ่มเล่น")
type_names = {
    'LEAD': ('สระหน้า (ขวา)', (56, 189, 248)),
    'TRAIL': ('สระตาม (ซ้าย)', (251, 146, 60)),
    'CLUSTER_UP_TONE': ('ข้อ 5: พยัญชนะ+สระ+วรรณยุกต์', (74, 222, 128)),
    'CLUSTER_TONE': ('ข้อ 4: พยัญชนะ+วรรณยุกต์', (250, 204, 21)),
    'BASE': ('พยัญชนะเดี่ยว', (167, 139, 250)),
}

xd = 25
yd = 190
for i, (tt, tv) in enumerate(demo_toks):
    c_img = render_token_cell(tt, tv)
    c_2x = c_img.resize((54, 54), Image.Resampling.NEAREST)
    t_label, t_color = type_names.get(tt, (tt, (200, 200, 200)))
    
    draw.rectangle([xd, yd, xd + 54, yd + 54], outline=t_color, width=2)
    draw.line([xd, yd + 46, xd + 54, yd + 46], fill=(34, 197, 94, 120), width=1)
    img.paste(c_2x, (xd, yd), c_2x)
    
    draw.text((xd + 27, yd + 70), f"'{tv}'", font=font_lbl, fill=(255, 255, 255), anchor='ms')
    draw.text((xd + 27, yd + 86), t_label, font=font_sub, fill=t_color, anchor='ms')
    draw.text((xd + 27, yd + 100), f"Cell #{i+1}", font=font_sub, fill=(148, 163, 184), anchor='ms')
    xd += 140

out_path = r"C:\Users\Supakiat\.gemini\antigravity\brain\ab5bc3db-774b-46d7-96ba-65470fc9eb39\preview_full_cluster_formula.png"
img.save(out_path)
print("Saved test preview:", out_path)
