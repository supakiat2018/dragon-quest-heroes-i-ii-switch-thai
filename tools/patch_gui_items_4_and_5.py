import re

gui_path = r"D:\Game\dragon quest heroes i & ii\switch\tools\thai_font_preview_gui.py"
with open(gui_path, "r", encoding="utf-8") as f:
    code = f.read()

# Replace tokenize_414 with full multi-layer tokenizer
old_token_fn = """def tokenize_414(text):
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
        elif ch in TONE_MARKS:
            tokens.append(('TONE', ch))
            i += 1
        elif ch in UPPER_MARKS:
            tokens.append(('UPPER', ch))
            i += 1
        elif ch in LOWER_MARKS:
            tokens.append(('LOWER', ch))
            i += 1
        elif ch == ' ':
            tokens.append(('SPACE', ' '))
            i += 1
        else:
            if i + 1 < n and text[i+1] in UPPER_MARKS:
                tokens.append(('BASE_UPPER', ch + text[i+1]))
                i += 2
            elif i + 1 < n and text[i+1] in LOWER_MARKS:
                tokens.append(('BASE_LOWER', ch + text[i+1]))
                i += 2
            else:
                tokens.append(('BASE', ch))
                i += 1
    return tokens"""

new_token_fn = """def tokenize_414(text):
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
    return tokens"""

assert old_token_fn in code, "old_token_fn not found!"
code = code.replace(old_token_fn, new_token_fn)

# Replace render_cell_414
old_render_fn = """def render_cell_414(tok_type, tok_val, lead_ox=8, trail_ox=-6, tone_ox=-6, tone_oy=-8, baseline=32):
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
    elif tok_type == 'TONE':
        cr = get_glyph_crop(tok_val)
        cx = max(0, min(36 - cr.width, 2 + (tone_ox + 6)))
        cy = max(0, min(36 - cr.height, baseline - 19 - cr.height + tone_oy))
        cell.paste(cr, (cx, cy), cr)
    elif tok_type == 'BASE_UPPER':
        b_ch, u_ch = tok_val[0], tok_val[1]
        cr_b = get_glyph_crop(b_ch)
        cr_u = get_glyph_crop(u_ch)
        cx_b = (36 - cr_b.width) // 2
        cy_b = baseline - cr_b.height
        cell.paste(cr_b, (cx_b, cy_b), cr_b)
        cx_u = cx_b + (cr_b.width - cr_u.width) // 2
        cy_u = cy_b - cr_u.height + 2
        cell.paste(cr_u, (cx_u, cy_u), cr_u)
    elif tok_type == 'BASE_LOWER':
        b_ch, l_ch = tok_val[0], tok_val[1]
        cr_b = get_glyph_crop(b_ch)
        cr_l = get_glyph_crop(l_ch)
        cx_b = (36 - cr_b.width) // 2
        cy_b = baseline - cr_b.height
        cell.paste(cr_b, (cx_b, cy_b), cr_b)
        cx_l = cx_b + (cr_b.width - cr_l.width) // 2
        cy_l = cy_b + cr_b.height - 4
        cell.paste(cr_l, (cx_l, cy_l), cr_l)
    elif tok_type in ('BASE', 'UPPER', 'LOWER'):
        cr = get_glyph_crop(tok_val)
        cx = (36 - cr.width) // 2
        cy = baseline - cr.height
        cell.paste(cr, (cx, cy), cr)
    return cell"""

new_render_fn = """def render_cell_414(tok_type, tok_val, lead_ox=8, trail_ox=-6, config=None, baseline=32):
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
    else: # CLUSTER_* (ข้อ 4 และ ข้อ 5: รวมร่าง 2-3 ชั้นในช่อง 36x36 เดียวกัน!)
        cfg = config if config else {}
        cell, _ = compose_pua_cluster_image(tok_val, cfg, baseline=baseline)
    return cell"""

assert old_render_fn in code, "old_render_fn not found!"
code = code.replace(old_render_fn, new_render_fn)

# Replace tab title and text
code = code.replace(
    'self.notebook.add(self.tab_414, text="  🌟 ทดสอบสูตร 414 ตัว (สระติดพยัญชนะ + วรรณยุกต์ยกสูง)  ")',
    'self.notebook.add(self.tab_414, text="  🌟 ทดสอบสูตรสมบูรณ์ (รวมข้อ 4 และ 5: ซ้อนวรรณยุกต์สมบูรณ์)  ")'
)

code = code.replace(
    'tk.Label(info_f, text="🌟 สูตร 414 ตัว:", bg="#131926", fg="#f59e0b", font=(\'Segoe UI\', 11, \'bold\')).pack(side=tk.LEFT)',
    'tk.Label(info_f, text="🌟 สูตรสมบูรณ์ (รวมข้อ 4 และ 5):", bg="#131926", fg="#f59e0b", font=(\'Segoe UI\', 11, \'bold\')).pack(side=tk.LEFT)'
)

code = code.replace(
    'tk.Label(info_f, text=" สระหน้าชิดขวา + สระตามชิดซ้าย + พยัญชนะติดสระบน/ล่าง (กิ/กุ รวม 352 ตัว) + วรรณยุกต์ยกสูงชิดซ้าย", bg="#131926", fg="#cbd5e1", font=(\'Segoe UI\', 10)).pack(side=tk.LEFT)',
    'tk.Label(info_f, text=" สระหน้าชิดขวา + สระตามชิดซ้าย + วรรณยุกต์และสระซ้อนบนหัวพยัญชนะ (รวมข้อ 4 และ 5 ครบ 100%)", bg="#131926", fg="#cbd5e1", font=(\'Segoe UI\', 10)).pack(side=tk.LEFT)'
)

# Update deconstruction type_names in update_414_view
old_types = """        type_names = {
            'LEAD': ('สระหน้า (ขวา)', (56, 189, 248)),
            'TRAIL': ('สระตาม (ซ้าย)', (251, 146, 60)),
            'TONE': ('วรรณยุกต์ (ยก)', (239, 68, 68)),
            'BASE_UPPER': ('พยัญชนะ+สระบน', (74, 222, 128)),
            'BASE_LOWER': ('พยัญชนะ+สระล่าง', (74, 222, 128)),
            'BASE': ('พยัญชนะเดี่ยว', (167, 139, 250)),
            'SPACE': ('เว้นวรรค', (148, 163, 184))
        }"""

new_types = """        type_names = {
            'LEAD': ('สระหน้า (ขวา)', (56, 189, 248)),
            'TRAIL': ('สระตาม (ซ้าย)', (251, 146, 60)),
            'CLUSTER_UP_TONE': ('ข้อ 5: พยัญชนะ+สระ+วรรณยุกต์', (74, 222, 128)),
            'CLUSTER_LOW_TONE': ('ข้อ 5: พยัญชนะ+สระล่าง+วรรณยุกต์', (74, 222, 128)),
            'CLUSTER_UP': ('ข้อ 2: พยัญชนะ+สระบน', (52, 211, 153)),
            'CLUSTER_LOW': ('ข้อ 3: พยัญชนะ+สระล่าง', (52, 211, 153)),
            'CLUSTER_TONE': ('ข้อ 4: พยัญชนะ+วรรณยุกต์', (250, 204, 21)),
            'BASE': ('พยัญชนะเดี่ยว', (167, 139, 250)),
            'SPACE': ('เว้นวรรค', (148, 163, 184))
        }"""

assert old_types in code, "old_types not found!"
code = code.replace(old_types, new_types)

# Update render_cell_414 call inside update_414_view
code = code.replace(
    'c = render_cell_414(tt, tv, lead_ox, trail_ox, tone_ox, tone_oy)',
    'c = render_cell_414(tt, tv, lead_ox, trail_ox, self.config_data)'
)
code = code.replace(
    'c_img = render_cell_414(tt, tv, lead_ox, trail_ox, tone_ox, tone_oy)',
    'c_img = render_cell_414(tt, tv, lead_ox, trail_ox, self.config_data)'
)

# Update stat text
code = code.replace(
    '📊 สถิติสูตร 414 ตัว:',
    '📊 สถิติสูตรสมบูรณ์ (รวมข้อ 4 และ 5):'
)

# Update card 2 title
code = code.replace(
    '[2] รายละเอียดการแยกเซลล์ฟอนต์ 36x36 พิกเซลตามสูตร 414 ตัว',
    '[2] รายละเอียดการแยกเซลล์ฟอนต์ 36x36 พิกเซลตามสูตรสมบูรณ์ (รวมข้อ 4 และ 5)'
)

with open(gui_path, "w", encoding="utf-8") as f:
    f.write(code)

print("Updated thai_font_preview_gui.py with full items 4 & 5 successfully!")
