import os

gui_path = r"D:\Game\dragon quest heroes i & ii\switch\tools\thai_font_preview_gui.py"
with open(gui_path, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Add self.custom_preview_text in __init__
old_init_part = '''        self.current_cluster = "ริ่"
        self.current_layer_part = "whole"'''

new_init_part = '''        self.current_cluster = "ริ่"
        self.current_layer_part = "whole"
        self.custom_preview_text = ""'''

assert old_init_part in code, "old_init_part not found!"
code = code.replace(old_init_part, new_init_part)

# 2. Update on_load_custom_input and select_pua_cluster
old_methods = '''    def on_load_custom_input(self):
        txt = self.entry_custom_cluster.get().strip()
        if not txt:
            return
        LEAD_VOWELS = set('เแโใไ')
        TRAIL_VOWELS = set('ะาำฤฦๅ')
        
        # If user typed a phrase (more than 4 chars or has multiple words)
        if len(txt) > 4 or any(c in txt for c in [' ', '   ']):
            # Find clusters in this phrase to select
            found_clusters = []
            i = 0
            n = len(txt)
            while i < n:
                ch = txt[i]
                if ch in LEAD_VOWELS or ch in TRAIL_VOWELS or ch == ' ':
                    i += 1
                else:
                    combo = ch
                    j = i + 1
                    while j < n and (txt[j] in UPPER_MARKS or txt[j] in LOWER_MARKS or txt[j] in TONE_MARKS):
                        combo += txt[j]
                        j += 1
                    if len(combo) > 1 and combo not in found_clusters:
                        found_clusters.append(combo)
                    i = j
            if found_clusters:
                self.select_pua_cluster(found_clusters[0], sync_entry=False)
            else:
                self.select_pua_cluster("ริ่", sync_entry=False)
        else:
            # Single cluster: if it starts with leading vowel, strip it because เ is standalone!
            c_tune = txt
            if len(c_tune) > 1 and c_tune[0] in LEAD_VOWELS:
                c_tune = c_tune[1:]
            self.select_pua_cluster(c_tune, sync_entry=False)

    def select_pua_cluster(self, c_text, sync_entry=True):
        if not c_text:
            return
        LEAD_VOWELS = set('เแโใไ')
        # Leading vowels (เ, แ, โ, ใ, ไ) are standalone, never PUA clusters!
        if len(c_text) > 1 and c_text[0] in LEAD_VOWELS:
            c_text = c_text[1:]
            
        self.current_cluster = c_text
        if sync_entry:
            self.entry_custom_cluster.delete(0, tk.END)
            self.entry_custom_cluster.insert(0, c_text)
        self.lbl_pua_cluster_title.config(text=f"คลัสเตอร์: [ {c_text} ]")'''

new_methods = '''    def on_load_custom_input(self):
        txt = self.entry_custom_cluster.get().strip()
        if not txt:
            return
        self.custom_preview_text = txt
        self.select_pua_cluster(txt, sync_entry=False)
        self.update_pua_sentence()

    def select_pua_cluster(self, c_text, sync_entry=True):
        if not c_text:
            return
        # If user clicked a preset cluster like ริ่, reset custom preview so 3 menus show
        if sync_entry:
            self.custom_preview_text = ""
            self.entry_custom_cluster.delete(0, tk.END)
            self.entry_custom_cluster.insert(0, c_text)
            
        self.current_cluster = c_text
        self.lbl_pua_cluster_title.config(text=f"คำ / คลัสเตอร์: [ {c_text} ]")
        
        # Ensure config has entry if single cluster
        if len(c_text) <= 4 and c_text not in self.config_data['clusters']:
            self.config_data['clusters'][c_text] = {
                'whole_ox': 0, 'whole_oy': 0,
                'layers': {}
            }
            for ch in c_text:
                nw, nh = get_natural_glyph_metrics(ch)
                self.config_data['clusters'][c_text]['layers'][ch] = {
                    'offset_x': 0, 'offset_y': 0,
                    'width': nw, 'height': nh
                }

        # Rebuild layer buttons dynamically for whatever user typed!
        for w in self.layer_btn_frame.winfo_children():
            w.destroy()
            
        self.layer_buttons = {}
        btn_whole = tk.Button(self.layer_btn_frame, text="รวมทั้งก้อน", font=('Segoe UI', 9, 'bold'), bg="#374151", fg="#ffffff",
                              relief=tk.FLAT, cursor="hand2", command=lambda: self.select_pua_layer_part('whole'))
        btn_whole.pack(side=tk.LEFT, padx=2, pady=2)
        self.layer_buttons['whole'] = btn_whole
        
        # Add a button for each unique character/part in c_text
        added_parts = set()
        for ch in c_text:
            if ch in (' ', '   ') or ch in added_parts:
                continue
            added_parts.add(ch)
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
            
        # Select first character if available, else 'whole'
        first_part = list(added_parts)[0] if added_parts and len(c_text) > 4 else 'whole'
        self.select_pua_layer_part(first_part)'''

assert old_methods in code, "old_methods not found!"
code = code.replace(old_methods, new_methods)

# 3. Update select_pua_layer_part to load glyphs metrics seamlessly
old_layer_select = '''        c_info = self.config_data['clusters'][self.current_cluster]
        if part == 'whole':
            self.lbl_active_layer.config(text="กำลังปรับ: [ รวมทั้งก้อน (ตำแหน่งใน Cell 36x36) ]")
            ox = c_info.get('whole_ox', 0)
            oy = c_info.get('whole_oy', 0)
            w, h = 32, 32
        else:
            self.lbl_active_layer.config(text=f"กำลังปรับชิ้นส่วน: [ '{part}' ]")
            l_cfg = c_info.get('layers', {}).get(part, {})
            ox = l_cfg.get('offset_x', 0)
            oy = l_cfg.get('offset_y', 0)
            nw, nh = get_natural_glyph_metrics(part)
            w = l_cfg.get('width', nw)
            h = l_cfg.get('height', nh)'''

new_layer_select = '''        if part == 'whole':
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

assert old_layer_select in code, "old_layer_select not found!"
code = code.replace(old_layer_select, new_layer_select)

# 4. Update on_pua_slider_change to sync part changes to glyphs and refresh real-time
old_slider_change = '''        c_info = self.config_data['clusters'][self.current_cluster]
        part = self.current_layer_part
        if part == 'whole':
            c_info['whole_ox'] = ox
            c_info['whole_oy'] = oy
        else:
            if 'layers' not in c_info:
                c_info['layers'] = {}
            c_info['layers'][part] = {
                'offset_x': ox,
                'offset_y': oy,
                'width': w,
                'height': h
            }
            
        # ซิงค์อักขระเดี่ยวเข้า glyphs ทันทีถ้าเป็นตัวอักษรเดี่ยว
        if len(self.current_cluster) == 1:
            ch = self.current_cluster
            if 'glyphs' not in self.config_data:
                self.config_data['glyphs'] = {}
            if ch not in self.config_data['glyphs']:
                self.config_data['glyphs'][ch] = {}
            self.config_data['glyphs'][ch]['offset_x'] = ox
            self.config_data['glyphs'][ch]['offset_y'] = oy
            self.config_data['glyphs'][ch]['width'] = w
            self.config_data['glyphs'][ch]['height'] = h
            
        self.update_pua_displays()'''

new_slider_change = '''        part = self.current_layer_part
        # Always sync glyphs for the selected character part
        if part != 'whole':
            if 'glyphs' not in self.config_data:
                self.config_data['glyphs'] = {}
            if part not in self.config_data['glyphs']:
                self.config_data['glyphs'][part] = {}
            self.config_data['glyphs'][part]['offset_x'] = ox
            self.config_data['glyphs'][part]['offset_y'] = oy
            self.config_data['glyphs'][part]['width'] = w
            self.config_data['glyphs'][part]['height'] = h
            
        if self.current_cluster in self.config_data.get('clusters', {}):
            c_info = self.config_data['clusters'][self.current_cluster]
            if part == 'whole':
                c_info['whole_ox'] = ox
                c_info['whole_oy'] = oy
            else:
                if 'layers' not in c_info:
                    c_info['layers'] = {}
                c_info['layers'][part] = {
                    'offset_x': ox,
                    'offset_y': oy,
                    'width': w,
                    'height': h
                }
                
        self.update_pua_displays()
        self.update_pua_sentence()'''

assert old_slider_change in code, "old_slider_change not found!"
code = code.replace(old_slider_change, new_slider_change)

# 5. Update update_pua_displays for individual characters or phrases
old_displays = '''    def update_pua_displays(self):
        c_img, bounds = compose_pua_cluster_image(self.current_cluster, self.config_data, self.current_layer_part)'''

new_displays = '''    def update_pua_displays(self):
        part = self.current_layer_part
        if part != 'whole':
            c_img = render_tuned_single_glyph(part, self.config_data)
            bounds = {part: (0, 0, c_img.width, c_img.height)}
        elif self.current_cluster in self.config_data.get('clusters', {}) or len(self.current_cluster) <= 4:
            c_img, bounds = compose_pua_cluster_image(self.current_cluster, self.config_data, self.current_layer_part)
        else:
            c_img = render_tuned_single_glyph(self.current_cluster[0], self.config_data)
            bounds = {}'''

assert old_displays in code, "old_displays not found!"
code = code.replace(old_displays, new_displays)

# 6. Update update_pua_sentence to display custom text dynamically
old_sentence_fn = '''        menus_cells = [
            ("เริ่มเล่น", [cr_e, c_ri, cr_m, cr_e, c_lo, cr_n]),
            ("สร้างเซฟ", [cr_s, c_re, cr_a, cr_ng, cr_e, cr_so, cr_f]),
            ("ลบเซฟ", [cr_l, cr_b, cr_e, cr_so, cr_f])
        ]'''

new_sentence_fn = '''        custom_txt = getattr(self, 'custom_preview_text', '').strip()
        if custom_txt:
            raw_parts = [p for p in custom_txt.split('   ') if p]
            if len(raw_parts) == 1:
                parts = [p for p in custom_txt.split(' ') if p]
                if not parts:
                    parts = [custom_txt]
            else:
                parts = raw_parts
                
            LEAD_VOWELS = set('เแโใไ')
            TRAIL_VOWELS = set('ะาำฤฦๅ')
            menus_cells = []
            for p_idx, part in enumerate(parts):
                cells = []
                i = 0
                n = len(part)
                while i < n:
                    ch = part[i]
                    if ch in LEAD_VOWELS or ch in TRAIL_VOWELS:
                        cells.append(render_tuned_single_glyph(ch, self.config_data))
                        i += 1
                    elif ch in UPPER_MARKS or ch in LOWER_MARKS or ch in TONE_MARKS:
                        cells.append(render_tuned_single_glyph(ch, self.config_data))
                        i += 1
                    else:
                        combo = ch
                        j = i + 1
                        while j < n and (part[j] in UPPER_MARKS or part[j] in LOWER_MARKS or part[j] in TONE_MARKS):
                            combo += part[j]
                            j += 1
                        if len(combo) > 1:
                            c_img, _ = compose_pua_cluster_image(combo, self.config_data)
                            cells.append(c_img)
                            i = j
                        else:
                            cells.append(render_tuned_single_glyph(ch, self.config_data))
                            i += 1
                menus_cells.append((f"ปุ่มที่ {p_idx+1}: {part}", cells))
        else:
            menus_cells = [
                ("เริ่มเล่น", [cr_e, c_ri, cr_m, cr_e, c_lo, cr_n]),
                ("สร้างเซฟ", [cr_s, c_re, cr_a, cr_ng, cr_e, cr_so, cr_f]),
                ("ลบเซฟ", [cr_l, cr_b, cr_e, cr_so, cr_f])
            ]'''

assert old_sentence_fn in code, "old_sentence_fn not found!"
code = code.replace(old_sentence_fn, new_sentence_fn)

with open(gui_path, "w", encoding="utf-8") as f:
    f.write(code)

print("Applied dynamic custom text preview successfully!")
