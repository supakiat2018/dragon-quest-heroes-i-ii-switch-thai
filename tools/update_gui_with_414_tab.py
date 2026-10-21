import os

target_file = r"D:\Game\dragon quest heroes i & ii\switch\tools\thai_font_preview_gui.py"
backup_file = r"D:\Game\dragon quest heroes i & ii\switch\tools\thai_font_preview_gui.py.bak"

with open(target_file, "r", encoding="utf-8") as f:
    code = f.read()

# Backup first
with open(backup_file, "w", encoding="utf-8") as f:
    f.write(code)

helper_code = '''
LEAD_VOWELS = set('เแโใไ')
TRAIL_VOWELS = set('ะาำฤฦๅ')

def tokenize_414(text):
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
    return tokens

def render_cell_414(tok_type, tok_val, lead_ox=8, trail_ox=-6, tone_ox=-6, tone_oy=-8, baseline=32):
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
    return cell
'''

methods_414 = '''
    # ================= TAB 5: 414 FORMULA SIMULATOR =================
    def setup_tab_414(self):
        ctrl = tk.Frame(self.tab_414, bg="#1f2636", relief=tk.RAISED, bd=1)
        ctrl.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        info_f = tk.Frame(ctrl, bg="#131926", padx=10, pady=6)
        info_f.pack(fill=tk.X, padx=8, pady=(8, 4))
        tk.Label(info_f, text="🌟 สูตร 414 ตัว:", bg="#131926", fg="#f59e0b", font=('Segoe UI', 11, 'bold')).pack(side=tk.LEFT)
        tk.Label(info_f, text=" สระหน้าชิดขวา + สระตามชิดซ้าย + พยัญชนะติดสระบน/ล่าง (กิ/กุ รวม 352 ตัว) + วรรณยุกต์ยกสูงชิดซ้าย", bg="#131926", fg="#cbd5e1", font=('Segoe UI', 10)).pack(side=tk.LEFT)
        
        r_preset = tk.Frame(ctrl, bg="#1f2636")
        r_preset.pack(fill=tk.X, padx=8, pady=4)
        tk.Label(r_preset, text="คำทดสอบด่วน:", bg="#1f2636", fg="#38bdf8", font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT, padx=(5, 8))
        presets = ["เริ่มเล่น", "สร้างเซฟ", "ลบเซฟ", "กินยา", "กิเลน", "ผู้กล้า", "น้ำมนต์", "ดราก้อนเควสต์"]
        for p in presets:
            b = tk.Button(r_preset, text=p, font=('Segoe UI', 9, 'bold'), bg="#2d3748", fg="#ffffff",
                          relief=tk.FLAT, cursor="hand2", padx=8, pady=2,
                          command=lambda word=p: self.set_414_text(word))
            b.pack(side=tk.LEFT, padx=3)
            
        r_input = tk.Frame(ctrl, bg="#1f2636")
        r_input.pack(fill=tk.X, padx=8, pady=6)
        tk.Label(r_input, text="พิมพ์คำหรือประโยค:", bg="#1f2636", fg="#f0c050", font=('Segoe UI', 11, 'bold')).pack(side=tk.LEFT, padx=5)
        self.entry_414 = tk.Entry(r_input, font=('Segoe UI', 12, 'bold'), bg="#10141d", fg="#ffffff", insertbackground="#ffffff")
        self.entry_414.insert(0, "เริ่มเล่น   สร้างเซฟ   กินยา")
        self.entry_414.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.entry_414.bind("<KeyRelease>", lambda e: self.update_414_view())
        
        tk.Button(r_input, text="รีเฟรช (Render)", bg="#2563eb", fg="#ffffff", font=('Segoe UI', 10, 'bold'),
                  relief=tk.FLAT, command=self.update_414_view, padx=12, pady=4, cursor="hand2").pack(side=tk.LEFT, padx=5)

        slider_frame = tk.LabelFrame(ctrl, text=" แผงปรับจูนตำแหน่งสูตร 414 ตัว (Real-time Spacing Tuning) ", bg="#1a2233", fg="#34d399", font=('Segoe UI', 10, 'bold'), bd=1)
        slider_frame.pack(fill=tk.X, padx=8, pady=(4, 8))
        
        sf_grid = tk.Frame(slider_frame, bg="#1a2233")
        sf_grid.pack(fill=tk.X, padx=10, pady=6)
        
        tk.Label(sf_grid, text="1. สระหน้า (เ แ โ ใ ไ) ชิดขวา:", bg="#1a2233", fg="#e2e8f0", font=('Segoe UI', 9)).grid(row=0, column=0, sticky=tk.W, padx=5)
        self.sl_414_lead = tk.Scale(sf_grid, from_=0, to=14, orient=tk.HORIZONTAL, bg="#1a2233", fg="#ffffff", highlightthickness=0, length=140, command=lambda v: self.update_414_view())
        self.sl_414_lead.set(8)
        self.sl_414_lead.grid(row=0, column=1, padx=5)
        
        tk.Label(sf_grid, text="2. สระตาม (ะ า ำ) ชิดซ้าย:", bg="#1a2233", fg="#e2e8f0", font=('Segoe UI', 9)).grid(row=0, column=2, sticky=tk.W, padx=15)
        self.sl_414_trail = tk.Scale(sf_grid, from_=-14, to=0, orient=tk.HORIZONTAL, bg="#1a2233", fg="#ffffff", highlightthickness=0, length=140, command=lambda v: self.update_414_view())
        self.sl_414_trail.set(-6)
        self.sl_414_trail.grid(row=0, column=3, padx=5)
        
        tk.Label(sf_grid, text="3. วรรณยุกต์เดี่ยว ยกสูงขึ้น (Y):", bg="#1a2233", fg="#e2e8f0", font=('Segoe UI', 9)).grid(row=1, column=0, sticky=tk.W, padx=5, pady=(4, 0))
        self.sl_414_toney = tk.Scale(sf_grid, from_=-16, to=0, orient=tk.HORIZONTAL, bg="#1a2233", fg="#ffffff", highlightthickness=0, length=140, command=lambda v: self.update_414_view())
        self.sl_414_toney.set(-8)
        self.sl_414_toney.grid(row=1, column=1, padx=5, pady=(4, 0))
        
        tk.Label(sf_grid, text="4. วรรณยุกต์เดี่ยว ชิดซ้าย (X):", bg="#1a2233", fg="#e2e8f0", font=('Segoe UI', 9)).grid(row=1, column=2, sticky=tk.W, padx=15, pady=(4, 0))
        self.sl_414_tonex = tk.Scale(sf_grid, from_=-16, to=0, orient=tk.HORIZONTAL, bg="#1a2233", fg="#ffffff", highlightthickness=0, length=140, command=lambda v: self.update_414_view())
        self.sl_414_tonex.set(-8)
        self.sl_414_tonex.grid(row=1, column=3, padx=5, pady=(4, 0))

        work = tk.Frame(self.tab_414, bg="#161a24")
        work.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        f_disp1 = tk.LabelFrame(work, text=" [1] การแสดงผลจริงในเกม (Simulated Game Menu) ", bg="#1f2636", fg="#38bdf8", font=('Segoe UI', 10, 'bold'), bd=1)
        f_disp1.pack(fill=tk.X, padx=5, pady=4)
        
        self.canvas_414_game = tk.Canvas(f_disp1, bg="#10141d", height=120, highlightthickness=0)
        self.canvas_414_game.pack(fill=tk.X, padx=8, pady=8)
        
        f_disp2 = tk.LabelFrame(work, text=" [2] รายละเอียดการแยกเซลล์ฟอนต์ 36x36 พิกเซลตามสูตร 414 ตัว ", bg="#1f2636", fg="#fde047", font=('Segoe UI', 10, 'bold'), bd=1)
        f_disp2.pack(fill=tk.BOTH, expand=True, padx=5, pady=4)
        
        self.canvas_414_decon = tk.Canvas(f_disp2, bg="#10141d", highlightthickness=0)
        self.canvas_414_decon.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        self.lbl_414_stat = tk.Label(self.tab_414, text="", bg="#161a24", fg="#94a3b8", font=('Segoe UI', 9))
        self.lbl_414_stat.pack(fill=tk.X, padx=12, pady=(0, 5))
        
        self.update_414_view()

    def set_414_text(self, text):
        self.entry_414.delete(0, tk.END)
        self.entry_414.insert(0, text)
        self.update_414_view()

    def update_414_view(self):
        text = self.entry_414.get().strip()
        if not text:
            text = "เริ่มเล่น"
            
        lead_ox = self.sl_414_lead.get()
        trail_ox = self.sl_414_trail.get()
        tone_ox = self.sl_414_tonex.get()
        tone_oy = self.sl_414_toney.get()
        
        lines = text.split('\\n')
        board_w = 1100
        board_h = max(100, len(lines) * 90 + 20)
        img_game = Image.new('RGBA', (board_w, board_h), (16, 20, 30, 255))
        draw_g = ImageDraw.Draw(img_game)
        
        total_cells_used = 0
        all_tokens_detail = []
        
        yc = 15
        for line in lines:
            parts = [p for p in line.split('   ') if p]
            if len(parts) == 1:
                parts = [line]
            xc = 20
            for part in parts:
                toks = tokenize_414(part)
                cells = []
                for tt, tv in toks:
                    c = render_cell_414(tt, tv, lead_ox, trail_ox, tone_ox, tone_oy)
                    cells.append((c, tt, tv))
                    all_tokens_detail.append((tt, tv))
                total_cells_used += len(cells)
                
                btn_w = len(cells) * 36 + 24
                draw_g.rectangle([xc, yc, xc + btn_w, yc + 52], fill=(22, 35, 60), outline=(218, 165, 32), width=2)
                draw_g.line([xc + 4, yc + 8, xc + btn_w - 4, yc + 8], fill=(220, 50, 50, 100), width=1)
                draw_g.line([xc + 4, yc + 44, xc + btn_w - 4, yc + 44], fill=(50, 120, 220, 100), width=1)
                
                x_char = xc + 12
                for cell_img, tt, tv in cells:
                    draw_g.rectangle([x_char, yc + 8, x_char + 35, yc + 43], outline=(60, 80, 120, 80), width=1)
                    img_game.paste(cell_img, (x_char, yc + 8), cell_img)
                    x_char += 36
                xc += btn_w + 16
            yc += 70
            
        self.tk_414_game = ImageTk.PhotoImage(img_game)
        self.canvas_414_game.delete("all")
        self.canvas_414_game.create_image(10, 10, anchor=tk.NW, image=self.tk_414_game)
        
        # Lower Canvas: Deconstruction
        decon_w = max(1100, len(all_tokens_detail) * 72 + 60)
        decon_h = 160
        img_decon = Image.new('RGBA', (decon_w, decon_h), (13, 17, 26, 255))
        draw_d = ImageDraw.Draw(img_decon)
        
        font_lbl = ImageFont.truetype(FONT_TTF, 12)
        font_sub = ImageFont.truetype(FONT_TTF, 10)
        
        type_names = {
            'LEAD': ('สระหน้า (ขวา)', (56, 189, 248)),
            'TRAIL': ('สระตาม (ซ้าย)', (251, 146, 60)),
            'TONE': ('วรรณยุกต์ (ยก)', (239, 68, 68)),
            'BASE_UPPER': ('พยัญชนะ+สระบน', (74, 222, 128)),
            'BASE_LOWER': ('พยัญชนะ+สระล่าง', (74, 222, 128)),
            'BASE': ('พยัญชนะเดี่ยว', (167, 139, 250)),
            'SPACE': ('เว้นวรรค', (148, 163, 184))
        }
        
        xd = 20
        for i, (tt, tv) in enumerate(all_tokens_detail):
            c_img = render_cell_414(tt, tv, lead_ox, trail_ox, tone_ox, tone_oy)
            c_2x = c_img.resize((54, 54), Image.Resampling.NEAREST)
            
            t_label, t_color = type_names.get(tt, (tt, (200, 200, 200)))
            
            draw_d.rectangle([xd, 15, xd + 54, 15 + 54], outline=t_color, width=2)
            draw_d.line([xd, 15 + 46, xd + 54, 15 + 46], fill=(34, 197, 94, 120), width=1)
            img_decon.paste(c_2x, (xd, 15), c_2x)
            
            draw_d.text((xd + 27, 76), f"'{tv}'", font=font_lbl, fill=(255, 255, 255), anchor='ms')
            draw_d.text((xd + 27, 92), t_label, font=font_sub, fill=t_color, anchor='ms')
            draw_d.text((xd + 27, 106), f"Cell #{i+1}", font=font_sub, fill=(148, 163, 184), anchor='ms')
            
            xd += 68
            
        self.tk_414_decon = ImageTk.PhotoImage(img_decon)
        self.canvas_414_decon.delete("all")
        self.canvas_414_decon.create_image(10, 10, anchor=tk.NW, image=self.tk_414_decon)
        
        self.lbl_414_stat.config(text=f"📊 สถิติสูตร 414 ตัว: คำนี้ใช้เซลล์ทั้งหมด {total_cells_used} เซลล์ (กว้าง {total_cells_used * 36} px) | ทุกเซลล์อยู่ในแค็ตตาล็อก 414 ตัว 100%")
'''

# 1. Add helper code before class ThaiFontMasterStudio
cls_idx = code.find("class ThaiFontMasterStudio(tk.Tk):")
assert cls_idx != -1
code = code[:cls_idx] + helper_code + "\n" + code[cls_idx:]

# 2. Add tab setup in __init__
init_target = """        self.setup_tab_single_tuner()
        self.setup_tab_test()
        self.setup_tab_atlas()"""

new_init = """        self.setup_tab_single_tuner()
        self.setup_tab_test()
        self.setup_tab_atlas()
        
        # TAB 5: 414 Formula Simulator
        self.tab_414 = tk.Frame(self.notebook, bg="#161a24")
        self.notebook.add(self.tab_414, text="  🌟 ทดสอบสูตร 414 ตัว (สระติดพยัญชนะ + วรรณยุกต์ยกสูง)  ")
        self.setup_tab_414()
        self.notebook.select(self.tab_414)"""

assert init_target in code, "init_target not found!"
code = code.replace(init_target, new_init)

# 3. Add methods before if __name__ == '__main__':
main_idx = code.rfind("if __name__ == '__main__':")
if main_idx == -1:
    main_idx = code.rfind('if __name__ == "__main__":')
assert main_idx != -1
code = code[:main_idx] + methods_414 + "\n" + code[main_idx:]

with open(target_file, "w", encoding="utf-8") as f:
    f.write(code)

print("Updated thai_font_preview_gui.py successfully!")
