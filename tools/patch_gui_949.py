import os

gui_path = r"D:\Game\dragon quest heroes i & ii\switch\tools\thai_font_preview_gui.py"
with open(gui_path, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Change current_cluster default
code = code.replace('self.current_cluster = "เริ่"', 'self.current_cluster = "ริ่"')

# 2. Change cluster lists
code = code.replace(
    'for c in ["เริ่", "ร้", "ล่", "เล่", "เซ", "ชื่", "ตั้"]:',
    'for c in ["ริ่", "ร้", "ล่", "ชื่", "ตั้", "กิ่", "กิ้"]:'
)
code = code.replace(
    'for c_name in ["เริ่", "ร้", "ล่", "เล่", "เซ", "ชื่", "ตั้"]:',
    'for c_name in ["ริ่", "ร้", "ล่", "ชื่", "ตั้", "กิ่", "กิ้"]:'
)
code = code.replace('self.entry_custom_cluster.insert(0, "เริ่")', 'self.entry_custom_cluster.insert(0, "ริ่")')
code = code.replace('text="คลัสเตอร์: [ เริ่ ]"', 'text="คลัสเตอร์: [ ริ่ ]"')

# 3. In atlas groups
code = code.replace(
    '("1. คลัสเตอร์ PUA พิเศษ:", ["เริ่", "ร้", "ล่", "เล่", "เซ", "ชื่", "ตั้"])',
    '("1. คลัสเตอร์ PUA ซ้อนชั้น (สูตร 949 ตัว):", ["ริ่", "ร้", "ล่", "ชื่", "ตั้", "กิ่", "กิ้"])'
)

# 4. In default single glyph rendering offsets for เ, แ, า
code = code.replace(
    "elif ch == 'เ':\n        default_ox, default_oy, default_w, default_h = -2, 0, 10, 19",
    "elif ch == 'เ':\n        default_ox, default_oy, default_w, default_h = 7, 0, 10, 19"
)
code = code.replace(
    "elif ch == 'แ':\n        default_ox, default_oy, default_w, default_h = -2, 0, 18, 19",
    "elif ch == 'แ':\n        default_ox, default_oy, default_w, default_h = 6, 0, 18, 19"
)
code = code.replace(
    "elif ch in 'าะ':\n        default_ox, default_oy, default_w, default_h = -2, 0, 14, 19",
    "elif ch in 'าะ':\n        default_ox, default_oy, default_w, default_h = -7, 0, 14, 19"
)

# 5. Update update_pua_sentence
old_sentence = '''    def update_pua_sentence(self):
        # Render simulated buttons using full real-time tuning for all characters
        def get_cell(tok):
            if tok in self.config_data.get('clusters', {}) and (len(tok) > 1 or self.config_data['clusters'][tok].get('layers')):
                img, _ = compose_pua_cluster_image(tok, self.config_data)
                return img
            return render_tuned_single_glyph(tok, self.config_data)
            
        c_eri = get_cell("เริ่")
        c_le  = get_cell("เล่")
        c_re  = get_cell("ร้")
        c_se  = get_cell("เซ")
        
        cr_m  = get_cell('ม')
        cr_n  = get_cell('น')
        cr_s  = get_cell('ส')
        cr_a  = get_cell('า')
        cr_ng = get_cell('ง')
        cr_f  = get_cell('ฟ')
        cr_l  = get_cell('ล')
        cr_b  = get_cell('บ')
        
        menus_cells = [
            ("เริ่มเล่น / เริ่มเกม", [c_eri, cr_m, c_le, cr_n]),
            ("สร้างเซฟ", [cr_s, c_re, cr_a, cr_ng, c_se, cr_f]),
            ("ลบเซฟ", [cr_l, cr_b, c_se, cr_f])
        ]'''

new_sentence = '''    def update_pua_sentence(self):
        # Render simulated buttons using full 949 cluster formula (Leading vowels are standalone!)
        def get_cell(tok):
            if tok in self.config_data.get('clusters', {}) and (len(tok) > 1 or self.config_data['clusters'][tok].get('layers')):
                img, _ = compose_pua_cluster_image(tok, self.config_data)
                return img
            return render_tuned_single_glyph(tok, self.config_data)
            
        cr_e  = get_cell('เ') # สระหน้าเดี่ยว ดันชิดขวาสุด
        c_ri  = get_cell("ริ่") # PUA คลัสเตอร์ 3 ชั้น (ร + ิ + ่)
        c_lo  = get_cell("ล่") # PUA คลัสเตอร์ 2 ชั้น (ล + ่)
        c_re  = get_cell("ร้") # PUA คลัสเตอร์ 2 ชั้น (ร + ้)
        
        cr_m  = get_cell('ม')
        cr_n  = get_cell('น')
        cr_s  = get_cell('ส')
        cr_a  = get_cell('า') # สระตามเดี่ยว ดันชิดซ้ายสุด
        cr_ng = get_cell('ง')
        cr_so = get_cell('ซ') # พยัญชนะเดี่ยว
        cr_f  = get_cell('ฟ')
        cr_l  = get_cell('ล')
        cr_b  = get_cell('บ')
        
        menus_cells = [
            ("เริ่มเล่น", [cr_e, c_ri, cr_m, cr_e, c_lo, cr_n]),
            ("สร้างเซฟ", [cr_s, c_re, cr_a, cr_ng, cr_e, cr_so, cr_f]),
            ("ลบเซฟ", [cr_l, cr_b, cr_e, cr_so, cr_f])
        ]'''

assert old_sentence in code, 'old_sentence not found!'
code = code.replace(old_sentence, new_sentence)

# 6. Update apply_auto_tight_spacing
old_tight = '''        tight_presets = {
            'ส': {'offset_x': 0, 'offset_y': 0, 'width': 18, 'height': 20},
            'ร้': {'whole_ox': 0, 'whole_oy': 0, 'layers': {'ร': {'offset_x': 0, 'offset_y': 0, 'width': 15, 'height': 19}, '้': {'offset_x': 0, 'offset_y': 0, 'width': 9, 'height': 9}}},
            'า': {'offset_x': -2, 'offset_y': 0, 'width': 14, 'height': 19},
            'ง': {'offset_x': 0, 'offset_y': 0, 'width': 16, 'height': 19},
            'เซ': {'whole_ox': 0, 'whole_oy': 0, 'layers': {'เ': {'offset_x': 0, 'offset_y': 0, 'width': 10, 'height': 19}, 'ซ': {'offset_x': 0, 'offset_y': 0, 'width': 18, 'height': 19}}},
            'ฟ': {'offset_x': 0, 'offset_y': 0, 'width': 19, 'height': 25},
            'ล': {'offset_x': 0, 'offset_y': 0, 'width': 17, 'height': 19},
            'บ': {'offset_x': 0, 'offset_y': 0, 'width': 19, 'height': 19},
            'เริ่': {'whole_ox': 0, 'whole_oy': 0, 'layers': {'เ': {'offset_x': 0, 'offset_y': 0, 'width': 10, 'height': 19}, 'ร': {'offset_x': 0, 'offset_y': 0, 'width': 15, 'height': 19}, 'ิ': {'offset_x': 0, 'offset_y': -3, 'width': 15, 'height': 6}, '่': {'offset_x': 0, 'offset_y': 0, 'width': 8, 'height': 8}}},
            'ม': {'offset_x': 0, 'offset_y': 0, 'width': 18, 'height': 19},
            'เล่': {'whole_ox': 0, 'whole_oy': 0, 'layers': {'เ': {'offset_x': 0, 'offset_y': 0, 'width': 10, 'height': 19}, 'ล': {'offset_x': 0, 'offset_y': 0, 'width': 17, 'height': 19}, '่': {'offset_x': 0, 'offset_y': 0, 'width': 8, 'height': 8}}},
            'น': {'offset_x': 0, 'offset_y': 0, 'width': 18, 'height': 19},
        }'''

new_tight = '''        tight_presets = {
            'ส': {'offset_x': 0, 'offset_y': 0, 'width': 18, 'height': 20},
            'ร้': {'whole_ox': 0, 'whole_oy': 0, 'layers': {'ร': {'offset_x': 0, 'offset_y': 0, 'width': 15, 'height': 19}, '้': {'offset_x': 0, 'offset_y': 0, 'width': 9, 'height': 9}}},
            'า': {'offset_x': -7, 'offset_y': 0, 'width': 14, 'height': 19},
            'ง': {'offset_x': 0, 'offset_y': 0, 'width': 16, 'height': 19},
            'เ': {'offset_x': 7, 'offset_y': 0, 'width': 10, 'height': 19},
            'แ': {'offset_x': 6, 'offset_y': 0, 'width': 18, 'height': 19},
            'ซ': {'offset_x': 0, 'offset_y': 0, 'width': 18, 'height': 19},
            'ฟ': {'offset_x': 0, 'offset_y': 0, 'width': 19, 'height': 25},
            'ล': {'offset_x': 0, 'offset_y': 0, 'width': 17, 'height': 19},
            'บ': {'offset_x': 0, 'offset_y': 0, 'width': 19, 'height': 19},
            'ริ่': {'whole_ox': 0, 'whole_oy': 0, 'layers': {'ร': {'offset_x': 0, 'offset_y': 0, 'width': 15, 'height': 19}, 'ิ': {'offset_x': 0, 'offset_y': -3, 'width': 15, 'height': 6}, '่': {'offset_x': 0, 'offset_y': 0, 'width': 8, 'height': 8}}},
            'ม': {'offset_x': 0, 'offset_y': 0, 'width': 18, 'height': 19},
            'ล่': {'whole_ox': 0, 'whole_oy': 0, 'layers': {'ล': {'offset_x': 0, 'offset_y': 0, 'width': 17, 'height': 19}, '่': {'offset_x': 0, 'offset_y': 0, 'width': 8, 'height': 8}}},
            'น': {'offset_x': 0, 'offset_y': 0, 'width': 18, 'height': 19},
            'ชื่': {'whole_ox': 0, 'whole_oy': 0, 'layers': {'ช': {'offset_x': 0, 'offset_y': 0, 'width': 18, 'height': 19}, 'ื': {'offset_x': 0, 'offset_y': -3, 'width': 16, 'height': 6}, '่': {'offset_x': 0, 'offset_y': 0, 'width': 8, 'height': 8}}},
            'ตั้': {'whole_ox': 0, 'whole_oy': 0, 'layers': {'ต': {'offset_x': 0, 'offset_y': 0, 'width': 17, 'height': 19}, 'ั': {'offset_x': 0, 'offset_y': -3, 'width': 15, 'height': 6}, '้': {'offset_x': 0, 'offset_y': 0, 'width': 9, 'height': 9}}},
        }'''

assert old_tight in code, 'old_tight not found!'
code = code.replace(old_tight, new_tight)

# 7. Update update_word_test with full dynamic 949 tokenizer
old_word_test = '''    def update_word_test(self):
        text = self.entry_test.get().strip()
        if not text: text = "เริ่มเล่น"
        lines = text.split('\\n')
        board_w = 1100
        board_h = max(260, len(lines) * 100 + 40)
        img = Image.new('RGBA', (board_w, board_h), (18, 22, 34, 255))
        draw = ImageDraw.Draw(img)
        
        yc = 25
        for line in lines:
            parts = [p for p in line.split('   ') if p]
            if len(parts) == 1: parts = [line]
            xc = 30
            for part in parts:
                cells = []
                # Check for special clusters first
                if "เริ่มเล่น" in part:
                    c_eri, _ = compose_pua_cluster_image("เริ่", self.config_data)
                    c_lo, _ = compose_pua_cluster_image("ล่", self.config_data)
                    cells = [c_eri, render_tuned_single_glyph('ม', self.config_data), render_tuned_single_glyph('เ', self.config_data), c_lo, render_tuned_single_glyph('น', self.config_data)]
                elif "สร้างเซฟ" in part:
                    c_re, _ = compose_pua_cluster_image("ร้", self.config_data)
                    cells = [render_tuned_single_glyph('ส', self.config_data), c_re, render_tuned_single_glyph('า', self.config_data), render_tuned_single_glyph('ง', self.config_data),
                             render_tuned_single_glyph('เ', self.config_data), render_tuned_single_glyph('ซ', self.config_data), render_tuned_single_glyph('ฟ', self.config_data)]
                elif "ลบเซฟ" in part:
                    cells = [render_tuned_single_glyph('ล', self.config_data), render_tuned_single_glyph('บ', self.config_data),
                             render_tuned_single_glyph('เ', self.config_data), render_tuned_single_glyph('ซ', self.config_data), render_tuned_single_glyph('ฟ', self.config_data)]
                else:
                    for ch in part:
                        cells.append(render_tuned_single_glyph(ch, self.config_data))
                        
                btn_w = len(cells) * 36 + 24
                draw.rectangle([xc, yc, xc + btn_w, yc + 48], fill=(22, 35, 60), outline=(218, 165, 32), width=2)
                draw.line([xc + 4, yc + 8, xc + btn_w - 4, yc + 8], fill=(220, 50, 50, 120), width=1)
                draw.line([xc + 4, yc + 41, xc + btn_w - 4, yc + 41], fill=(50, 120, 220, 120), width=1)
                
                x_char = xc + 12
                for cell in cells:
                    draw.rectangle([x_char, yc + 6, x_char + 35, yc + 41], outline=(55, 75, 110, 80))
                    img.paste(cell, (x_char, yc + 6), cell)
                    x_char += 36
                xc += btn_w + 18
            yc += 75
            
        self.tk_test_img = ImageTk.PhotoImage(img)
        self.canvas_test.delete("all")
        self.canvas_test.create_image(10, 10, anchor=tk.NW, image=self.tk_test_img)'''

new_word_test = '''    def update_word_test(self):
        text = self.entry_test.get().strip()
        if not text: text = "เริ่มเล่น   สร้างเซฟ   ลบเซฟ"
        lines = text.split('\\n')
        board_w = 1100
        board_h = max(260, len(lines) * 100 + 40)
        img = Image.new('RGBA', (board_w, board_h), (18, 22, 34, 255))
        draw = ImageDraw.Draw(img)
        
        LEAD_VOWELS = set('เแโใไ')
        TRAIL_VOWELS = set('ะาำฤฦๅ')
        
        yc = 25
        for line in lines:
            parts = [p for p in line.split('   ') if p]
            if len(parts) == 1: parts = [line]
            xc = 30
            for part in parts:
                cells = []
                i = 0
                n = len(part)
                while i < n:
                    ch = part[i]
                    if ch == ' ':
                        # ช่องว่าง 16px
                        space_cell = Image.new('RGBA', (16, 36), (0, 0, 0, 0))
                        cells.append(space_cell)
                        i += 1
                    elif ch in LEAD_VOWELS or ch in TRAIL_VOWELS:
                        # สระหน้า หรือ สระตาม เป็นตัวเดี่ยว 1 ช่องเสมอ (ตามสูตร 949)
                        cells.append(render_tuned_single_glyph(ch, self.config_data))
                        i += 1
                    elif ch in UPPER_MARKS or ch in LOWER_MARKS or ch in TONE_MARKS:
                        # เครื่องหมายลอยหลุดมาเดี่ยวๆ
                        cells.append(render_tuned_single_glyph(ch, self.config_data))
                        i += 1
                    else:
                        # พยัญชนะ: ดูว่ามีสระบน/ล่าง หรือวรรณยุกต์ตามหลังหรือไม่
                        combo = ch
                        j = i + 1
                        while j < n and (part[j] in UPPER_MARKS or part[j] in LOWER_MARKS or part[j] in TONE_MARKS):
                            combo += part[j]
                            j += 1
                        if len(combo) > 1:
                            # PUA คลัสเตอร์รวมร่าง (ริ่, ร้, ล่, ตั้, กิ่, ฯลฯ)
                            c_img, _ = compose_pua_cluster_image(combo, self.config_data)
                            cells.append(c_img)
                            i = j
                        else:
                            # พยัญชนะเดี่ยว
                            cells.append(render_tuned_single_glyph(ch, self.config_data))
                            i += 1
                        
                btn_w = sum(c.width for c in cells) + 24
                draw.rectangle([xc, yc, xc + btn_w, yc + 48], fill=(22, 35, 60), outline=(218, 165, 32), width=2)
                draw.line([xc + 4, yc + 8, xc + btn_w - 4, yc + 8], fill=(220, 50, 50, 120), width=1)
                draw.line([xc + 4, yc + 41, xc + btn_w - 4, yc + 41], fill=(50, 120, 220, 120), width=1)
                
                x_char = xc + 12
                for cell in cells:
                    cw = cell.width
                    draw.rectangle([x_char, yc + 6, x_char + cw - 1, yc + 41], outline=(55, 75, 110, 80))
                    img.paste(cell, (x_char, yc + 6), cell)
                    x_char += cw
                xc += btn_w + 18
            yc += 75
            
        self.tk_test_img = ImageTk.PhotoImage(img)
        self.canvas_test.delete("all")
        self.canvas_test.create_image(10, 10, anchor=tk.NW, image=self.tk_test_img)'''

assert old_word_test in code, 'old_word_test not found!'
code = code.replace(old_word_test, new_word_test)

with open(gui_path, "w", encoding="utf-8") as f:
    f.write(code)

print("Patch applied successfully to thai_font_preview_gui.py!")
