import os

gui_path = r"D:\Game\dragon quest heroes i & ii\switch\tools\thai_font_preview_gui.py"
with open(gui_path, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Update render_tuned_single_glyph default offsets to 18, 1
old_render_offsets = '''    elif ch == 'เ':
        default_ox, default_oy, default_w, default_h = 14, 1, 10, 19
    elif ch == 'แ':
        default_ox, default_oy, default_w, default_h = 14, 1, 18, 19
    elif ch in 'โใไ':
        default_ox, default_oy, default_w, default_h = 14, 1, 14, 26'''

new_render_offsets = '''    elif ch in 'เแโใไ':
        default_w = 18 if ch == 'แ' else (14 if ch in 'โใไ' else 10)
        default_h = 26 if ch in 'โใไ' else 19
        default_ox, default_oy = 18, 1'''

assert old_render_offsets in code, "old_render_offsets not found!"
code = code.replace(old_render_offsets, new_render_offsets)

# 2. In tight_presets, ensure all leading vowels are ox=18, oy=1
old_tight = '''            'เ': {'offset_x': 14, 'offset_y': 1, 'width': 10, 'height': 19},
            'แ': {'offset_x': 14, 'offset_y': 1, 'width': 18, 'height': 19},
            'โ': {'offset_x': 14, 'offset_y': 1, 'width': 14, 'height': 26},
            'ใ': {'offset_x': 14, 'offset_y': 1, 'width': 14, 'height': 26},
            'ไ': {'offset_x': 14, 'offset_y': 1, 'width': 14, 'height': 26},'''

new_tight = '''            'เ': {'offset_x': 18, 'offset_y': 1, 'width': 10, 'height': 19},
            'แ': {'offset_x': 18, 'offset_y': 1, 'width': 18, 'height': 19},
            'โ': {'offset_x': 18, 'offset_y': 1, 'width': 14, 'height': 26},
            'ใ': {'offset_x': 18, 'offset_y': 1, 'width': 14, 'height': 26},
            'ไ': {'offset_x': 18, 'offset_y': 1, 'width': 14, 'height': 26},'''

assert old_tight in code, "old_tight not found!"
code = code.replace(old_tight, new_tight)

# 3. Remove duplicate block lines 563-617 and fix select_pua_layer_part
old_dup_and_layer = '''        # Select first character if available, else 'whole'
        first_part = list(added_parts)[0] if added_parts and len(c_text) > 4 else 'whole'
        self.select_pua_layer_part(first_part)
        
        if c_text not in self.config_data['clusters']:
            self.config_data['clusters'][c_text] = {
                'whole_ox': 0, 'whole_oy': 0,
                'layers': {}
            }
            for ch in c_text:
                if ch in UPPER_MARKS:
                    ox, oy, nw, nh = 0, -3, 15, 6
                elif ch == 'เ':
                    ox, oy, nw, nh = -2, 0, 10, 19
                elif ch == 'แ':
                    ox, oy, nw, nh = -2, 0, 18, 19
                elif ch in 'โใไ':
                    ox, oy, nw, nh = -2, 0, 14, 26
                elif ch in 'าะ':
                    ox, oy, nw, nh = -2, 0, 14, 19
                elif ch == 'ำ':
                    ox, oy, nw, nh = -2, 0, 21, 27
                elif ch == 'ๅ':
                    ox, oy, nw, nh = -2, 0, 14, 25
                else:
                    nw, nh = get_natural_glyph_metrics(ch)
                    ox, oy = 0, 0
                self.config_data['clusters'][c_text]['layers'][ch] = {
                    'offset_x': ox, 'offset_y': oy,
                    'width': nw, 'height': nh
                }
            if len(c_text) == 1 and c_text in 'เแโใไาำะๅ':
                self.config_data['clusters'][c_text]['whole_ox'] = -2
                
        # Rebuild layer buttons
        for w in self.layer_btn_frame.winfo_children():
            w.destroy()
            
        self.layer_buttons = {}
        btn_whole = tk.Button(self.layer_btn_frame, text="รวมทั้งก้อน", font=('Segoe UI', 9, 'bold'), bg="#374151", fg="#ffffff",
                              relief=tk.FLAT, cursor="hand2", command=lambda: self.select_pua_layer_part('whole'))
        btn_whole.pack(side=tk.LEFT, padx=2, pady=2)
        self.layer_buttons['whole'] = btn_whole
        
        for ch in c_text:
            label_desc = f"'{ch}'"
            if ch in 'เแโใไ': label_desc = f"สระ '{ch}'"
            elif ch in UPPER_MARKS: label_desc = f"สระบน '{ch}'"
            elif ch in TONE_MARKS: label_desc = f"วรรณยุกต์ '{ch}'"
            elif ch in LOWER_MARKS: label_desc = f"สระล่าง '{ch}'"
            else: label_desc = f"พยัญชนะ '{ch}'"
            
            b = tk.Button(self.layer_btn_frame, text=label_desc, font=('Segoe UI', 9, 'bold'), bg="#2b354c", fg="#cbd5e1",
                          relief=tk.FLAT, cursor="hand2", command=lambda p=ch: self.select_pua_layer_part(p))
            b.pack(side=tk.LEFT, padx=2, pady=2)
            self.layer_buttons[ch] = b
            
        self.select_pua_layer_part('whole')
        
    def select_pua_layer_part(self, part):
        self.current_layer_part = part
        for p_key, btn in self.layer_buttons.items():
            if p_key == part:
                btn.config(bg="#2563eb", fg="#ffffff")
            else:
                btn.config(bg="#2b354c", fg="#cbd5e1")
                
        if part == 'whole':
            self.lbl_active_layer.config(text="กำลังปรับ: [ รวมทั้งก้อน (ตำแหน่งใน Cell 36x36) ]")
            if self.current_cluster in self.config_data.get('clusters', {}):
                c_info = self.config_data['clusters'][self.current_cluster]
                ox = c_info.get('whole_ox', 0)
                oy = c_info.get('whole_oy', 0)
            else:
                ox, oy = 0, 0
            w, h = 32, 32
        else:
            self.lbl_active_layer.config(text=f"กำลังปรับชิ้นส่วน: [ '{part}' ]")
            # Load from glyphs first
            g_info = self.config_data.get('glyphs', {}).get(part, {})
            nw, nh = get_natural_glyph_metrics(part)
            ox = g_info.get('offset_x', 0)
            oy = g_info.get('offset_y', 0)
            w = g_info.get('width', nw)
            h = g_info.get('height', nh)
            
            # Check cluster layer override if present
            if self.current_cluster in self.config_data.get('clusters', {}):
                l_cfg = self.config_data['clusters'][self.current_cluster].get('layers', {}).get(part, {})
                if 'offset_x' in l_cfg: ox = l_cfg['offset_x']
                if 'offset_y' in l_cfg: oy = l_cfg['offset_y']
                if 'width' in l_cfg: w = l_cfg['width']
                if 'height' in l_cfg: h = l_cfg['height']'''

new_dup_and_layer = '''        # Select first character if available, else 'whole'
        first_part = list(added_parts)[0] if added_parts else 'whole'
        self.select_pua_layer_part(first_part)
        
    def select_pua_layer_part(self, part):
        self.current_layer_part = part
        for p_key, btn in self.layer_buttons.items():
            if p_key == part:
                btn.config(bg="#2563eb", fg="#ffffff")
            else:
                btn.config(bg="#2b354c", fg="#cbd5e1")
                
        LEAD_VOWELS = set('เแโใไ')
        TRAIL_VOWELS = set('ะาำฤฦๅ')
        
        if part == 'whole':
            self.lbl_active_layer.config(text="กำลังปรับ: [ รวมทั้งก้อน (ตำแหน่งใน Cell 36x36) ]")
            if self.current_cluster in self.config_data.get('clusters', {}):
                c_info = self.config_data['clusters'][self.current_cluster]
                ox = c_info.get('whole_ox', 0)
                oy = c_info.get('whole_oy', 0)
            else:
                ox, oy = 0, 0
            w, h = 32, 32
        elif part in LEAD_VOWELS:
            # สระนำหน้า: ล็อกค่ามาตรฐานถาวร Offset X = +18 px, Offset Y = +1 px ทันทีเสมอ ไม่ต้องปรับใหม่!
            self.lbl_active_layer.config(text=f"กำลังปรับชิ้นส่วน: [ สระนำหน้า '{part}' ] (ล็อกชิดขวาสุดถาวร)")
            g_info = self.config_data.get('glyphs', {}).get(part, {})
            nw, nh = get_natural_glyph_metrics(part)
            ox = g_info.get('offset_x', 18)
            oy = g_info.get('offset_y', 1)
            w = g_info.get('width', nw)
            h = g_info.get('height', nh)
        elif part in TRAIL_VOWELS:
            # สระตาม: ดันชิดซ้ายสุด
            self.lbl_active_layer.config(text=f"กำลังปรับชิ้นส่วน: [ สระตาม '{part}' ]")
            g_info = self.config_data.get('glyphs', {}).get(part, {})
            nw, nh = get_natural_glyph_metrics(part)
            ox = g_info.get('offset_x', -7)
            oy = g_info.get('offset_y', 0)
            w = g_info.get('width', nw)
            h = g_info.get('height', nh)
        else:
            self.lbl_active_layer.config(text=f"กำลังปรับชิ้นส่วน: [ '{part}' ]")
            # Load from glyphs first
            g_info = self.config_data.get('glyphs', {}).get(part, {})
            nw, nh = get_natural_glyph_metrics(part)
            ox = g_info.get('offset_x', 0)
            oy = g_info.get('offset_y', 0)
            w = g_info.get('width', nw)
            h = g_info.get('height', nh)
            
            # Check cluster layer override if present for true PUA clusters
            if self.current_cluster in self.config_data.get('clusters', {}):
                l_cfg = self.config_data['clusters'][self.current_cluster].get('layers', {}).get(part, {})
                if 'offset_x' in l_cfg: ox = l_cfg['offset_x']
                if 'offset_y' in l_cfg: oy = l_cfg['offset_y']
                if 'width' in l_cfg: w = l_cfg['width']
                if 'height' in l_cfg: h = l_cfg['height']'''

assert old_dup_and_layer in code, "old_dup_and_layer not found!"
code = code.replace(old_dup_and_layer, new_dup_and_layer)

with open(gui_path, "w", encoding="utf-8") as f:
    f.write(code)

print("Applied permanent leading vowel fix successfully!")
