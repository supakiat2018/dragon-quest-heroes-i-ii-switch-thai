import sys, os
from PIL import Image, ImageFont, ImageDraw

sys.path.append(r"D:\Game\dragon quest heroes i & ii\switch\tools")
from thai_font_preview_gui import tokenize_414, render_cell_414, FONT_TTF

img = Image.new('RGBA', (1050, 360), (18, 24, 38, 255))
draw = ImageDraw.Draw(img)

font_h1 = ImageFont.truetype(FONT_TTF, 18)
font_lbl = ImageFont.truetype(FONT_TTF, 12)
font_sub = ImageFont.truetype(FONT_TTF, 10)

draw.text((25, 15), "🌟 พรีวิวจำลองสูตร 414 ตัว (Vowel-Attached + Floating Tone)", font=font_h1, fill=(245, 158, 11))
draw.text((25, 45), "สระหน้าชิดขวา + สระตามชิดซ้าย + พยัญชนะติดสระบน/ล่าง (กิ/กุ) + วรรณยุกต์เดี่ยวยกสูงชิดซ้าย", font=font_lbl, fill=(148, 163, 184))

# Section 1: In game buttons
draw.text((25, 75), "[1] ตัวอย่างปุ่มเมนูในเกม (Simulated Game Menus):", font=font_lbl, fill=(56, 189, 248))

phrases = ["เริ่มเล่น", "สร้างเซฟ", "ลบเซฟ", "กินยาฟื้นพลัง"]
xc = 25
yc = 100
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
draw.text((25, 175), "[2] ชำแหละเซลล์ 36x36 px ของคำว่า 'เริ่มเล่น' ตามสูตร 414 ตัว:", font=font_lbl, fill=(253, 224, 71))

demo_toks = tokenize_414("เริ่มเล่น")
type_names = {
    'LEAD': ('สระหน้า (ขวา)', (56, 189, 248)),
    'TRAIL': ('สระตาม (ซ้าย)', (251, 146, 60)),
    'TONE': ('วรรณยุกต์ (ยก)', (239, 68, 68)),
    'BASE_UPPER': ('พยัญชนะ+สระบน', (74, 222, 128)),
    'BASE_LOWER': ('พยัญชนะ+สระล่าง', (74, 222, 128)),
    'BASE': ('พยัญชนะเดี่ยว', (167, 139, 250)),
}

xd = 25
yd = 205
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
    xd += 85

out_path = r"C:\Users\Supakiat\.gemini\antigravity\brain\ab5bc3db-774b-46d7-96ba-65470fc9eb39\gui_414_formula_preview.png"
img.save(out_path)
print("Saved GUI preview:", out_path)
