import sys, os
from PIL import Image, ImageFont, ImageDraw

sys.path.append(r"D:\Game\dragon quest heroes i & ii\switch\tools")
from thai_font_preview_gui import tokenize_414, render_cell_414, FONT_TTF

img = Image.new('RGBA', (1100, 480), (16, 20, 30, 255))
draw = ImageDraw.Draw(img)

font_h1 = ImageFont.truetype(FONT_TTF, 18)
font_lbl = ImageFont.truetype(FONT_TTF, 13)
font_sub = ImageFont.truetype(FONT_TTF, 11)

draw.text((25, 15), "🌟 อัปเดตสูตรสมบูรณ์: รวมข้อ 4 และ ข้อ 5 ซ้อนวรรณยุกต์บนหัวพยัญชนะเรียบร้อย!", font=font_h1, fill=(245, 158, 11))
draw.text((25, 45), "เปรียบเทียบคำว่า 'เริ่มเล่น' และ 'สร้างเซฟ' ก่อนทำ VS หลังทำข้อ 4, 5", font=font_lbl, fill=(148, 163, 184))

# Section 1: In game buttons
draw.text((25, 80), "[1] พรีวิวปุ่มเมนูในเกม (หลังรวมข้อ 4 และ 5): ชิดแน่น สระและวรรณยุกต์ซ้อนบนหัวพยัญชนะตรงเป๊ะ 100%", font=font_lbl, fill=(56, 189, 248))

phrases = ["เริ่มเล่น", "สร้างเซฟ", "ลบเซฟ", "กินยา", "ผู้กล้า", "น้ำมนต์"]
xc = 25
yc = 110
for phrase in phrases:
    toks = tokenize_414(phrase)
    cells = [render_cell_414(tt, tv) for (tt, tv) in toks]
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

# Section 2: Deconstruction for 'เริ่มเล่น'
draw.text((25, 190), "[2] ชำแหละเซลล์ 36x36 px ของคำว่า 'เริ่มเล่น' (ลดเหลือ 6 เซลล์ ไม่มีช่องโหว่):", font=font_lbl, fill=(253, 224, 71))

demo_toks = tokenize_414("เริ่มเล่น")
type_names = {
    'LEAD': ('สระหน้า (ขวา)', (56, 189, 248)),
    'TRAIL': ('สระตาม (ซ้าย)', (251, 146, 60)),
    'CLUSTER_UP_TONE': ('ข้อ 5: พยัญชนะ+สระ+วรรณยุกต์', (74, 222, 128)),
    'CLUSTER_TONE': ('ข้อ 4: พยัญชนะ+วรรณยุกต์', (250, 204, 21)),
    'BASE': ('พยัญชนะเดี่ยว', (167, 139, 250)),
}

xd = 25
yd = 220
for i, (tt, tv) in enumerate(demo_toks):
    c_img = render_cell_414(tt, tv)
    c_2x = c_img.resize((54, 54), Image.Resampling.NEAREST)
    t_label, t_color = type_names.get(tt, (tt, (200, 200, 200)))
    
    draw.rectangle([xd, yd, xd + 54, yd + 54], outline=t_color, width=2)
    draw.line([xd, yd + 46, xd + 54, yd + 46], fill=(34, 197, 94, 120), width=1)
    img.paste(c_2x, (xd, yd), c_2x)
    
    draw.text((xd + 27, yd + 70), f"'{tv}'", font=font_lbl, fill=(255, 255, 255), anchor='ms')
    draw.text((xd + 27, yd + 86), t_label, font=font_sub, fill=t_color, anchor='ms')
    draw.text((xd + 27, yd + 100), f"Cell #{i+1}", font=font_sub, fill=(148, 163, 184), anchor='ms')
    xd += 140

# Section 3: Deconstruction for 'สร้างเซฟ'
draw.text((25, 335), "[3] ชำแหละเซลล์ 36x36 px ของคำว่า 'สร้างเซฟ' (ข้อ 4: 'ร้' รวมร่างในช่องเดียว 36x36):", font=font_lbl, fill=(253, 224, 71))

demo_toks2 = tokenize_414("สร้างเซฟ")
xd = 25
yd = 365
for i, (tt, tv) in enumerate(demo_toks2):
    c_img = render_cell_414(tt, tv)
    c_2x = c_img.resize((54, 54), Image.Resampling.NEAREST)
    t_label, t_color = type_names.get(tt, (tt, (200, 200, 200)))
    
    draw.rectangle([xd, yd, xd + 54, yd + 54], outline=t_color, width=2)
    draw.line([xd, yd + 46, xd + 54, yd + 46], fill=(34, 197, 94, 120), width=1)
    img.paste(c_2x, (xd, yd), c_2x)
    
    draw.text((xd + 27, yd + 70), f"'{tv}'", font=font_lbl, fill=(255, 255, 255), anchor='ms')
    draw.text((xd + 27, yd + 86), t_label, font=font_sub, fill=t_color, anchor='ms')
    draw.text((xd + 27, yd + 100), f"Cell #{i+1}", font=font_sub, fill=(148, 163, 184), anchor='ms')
    xd += 120

out_path = r"C:\Users\Supakiat\.gemini\antigravity\brain\ab5bc3db-774b-46d7-96ba-65470fc9eb39\updated_full_formula_preview.png"
img.save(out_path)
print("Saved updated preview image:", out_path)
