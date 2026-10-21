import os

gui_path = r"D:\Game\dragon quest heroes i & ii\switch\tools\thai_font_preview_gui.py"
with open(gui_path, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Update window geometry to 1240x860
code = code.replace('self.geometry("1140x840")', 'self.geometry("1240x860")')

# 2. Update top_bar in setup_tab_pua with 2 rows and full-width expand entry
old_top_bar = '''        top_bar = tk.Frame(self.tab_pua, bg="#1f2636", relief=tk.RAISED, bd=1)
        top_bar.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        tk.Label(top_bar, text="เลือกคลัสเตอร์ PUA ที่ต้องการปรับ:", bg="#1f2636", fg="#f0c050", font=('Segoe UI', 11, 'bold')).pack(side=tk.LEFT, padx=10, pady=8)
        
        for c_name in ["ริ่", "ร้", "ล่", "ชื่", "ตั้", "กิ่", "กิ้"]:
            b = tk.Button(top_bar, text=f" [ {c_name} ] ", font=('Segoe UI', 11, 'bold'), bg="#2b354c", fg="#ffffff",
                          relief=tk.FLAT, cursor="hand2", command=lambda cn=c_name: self.select_pua_cluster(cn))
            b.pack(side=tk.LEFT, padx=3, pady=6)
            
        tk.Label(top_bar, text=" หรือพิมพ์ข้อความ/ผสมเอง:", bg="#1f2636", fg="#94a3b8", font=('Segoe UI', 10)).pack(side=tk.LEFT, padx=(10, 2))
        self.entry_custom_cluster = tk.Entry(top_bar, width=32, font=('Segoe UI', 11, 'bold'), bg="#10141d", fg="#ffffff", insertbackground="#ffffff")
        self.entry_custom_cluster.insert(0, "เริ่มเล่นสร้างเซฟลบเซฟ")
        self.entry_custom_cluster.pack(side=tk.LEFT, padx=4)
        self.entry_custom_cluster.bind("<Return>", lambda e: self.on_load_custom_input())
        tk.Button(top_bar, text="โหลด (Load)", bg="#3b82f6", fg="#ffffff", font=('Segoe UI', 9, 'bold'), relief=tk.FLAT, cursor="hand2",
                  command=self.on_load_custom_input).pack(side=tk.LEFT, padx=4)'''

new_top_bar = '''        top_bar = tk.Frame(self.tab_pua, bg="#1f2636", relief=tk.RAISED, bd=1)
        top_bar.pack(fill=tk.X, padx=10, pady=(6, 4))
        
        # Row 1: Presets
        r1 = tk.Frame(top_bar, bg="#1f2636")
        r1.pack(fill=tk.X, padx=8, pady=(4, 2))
        tk.Label(r1, text="เลือกคลัสเตอร์ PUA ที่ต้องการปรับ:", bg="#1f2636", fg="#f0c050", font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT, padx=(0, 6))
        for c_name in ["ริ่", "ร้", "ล่", "ชื่", "ตั้", "กิ่", "กิ้"]:
            b = tk.Button(r1, text=f" [ {c_name} ] ", font=('Segoe UI', 10, 'bold'), bg="#2b354c", fg="#ffffff",
                          relief=tk.FLAT, cursor="hand2", command=lambda cn=c_name: self.select_pua_cluster(cn))
            b.pack(side=tk.LEFT, padx=3)
            
        # Row 2: Custom Text Entry (Long & Spacious with guaranteed visible Load button)
        r2 = tk.Frame(top_bar, bg="#1f2636")
        r2.pack(fill=tk.X, padx=8, pady=(2, 6))
        tk.Label(r2, text="หรือพิมพ์ข้อความ / ผสมคำเอง:", bg="#1f2636", fg="#38bdf8", font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT, padx=(0, 6))
        self.entry_custom_cluster = tk.Entry(r2, font=('Segoe UI', 11, 'bold'), bg="#10141d", fg="#ffffff", insertbackground="#ffffff")
        self.entry_custom_cluster.insert(0, "เริ่มเล่นสร้างเซฟลบเซฟ")
        self.entry_custom_cluster.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        self.entry_custom_cluster.bind("<Return>", lambda e: self.on_load_custom_input())
        tk.Button(r2, text="  🔍 โหลด (Load)  ", bg="#2563eb", fg="#ffffff", font=('Segoe UI', 10, 'bold'), relief=tk.FLAT, cursor="hand2",
                  command=self.on_load_custom_input).pack(side=tk.LEFT)'''

assert old_top_bar in code, "old_top_bar not found!"
code = code.replace(old_top_bar, new_top_bar)

# 3. Compact action buttons in left panel to prevent overflow
old_act_box = '''        # Action Buttons
        act_box = tk.Frame(left_f, bg="#1f2636")
        act_box.pack(fill=tk.X, padx=10, pady=(15, 5))
        
        tk.Button(act_box, text="⚡ จัดตัวชิดสวยงาม (Auto Tight Spacing)", bg="#8b5cf6", fg="#ffffff", font=('Segoe UI', 10, 'bold'),
                  relief=tk.FLAT, cursor="hand2", command=self.apply_auto_tight_spacing, pady=6).pack(fill=tk.X, pady=3)
        tk.Button(act_box, text="💾 บันทึกค่า PUA คลัสเตอร์นี้ (Save)", bg="#10b981", fg="#ffffff", font=('Segoe UI', 10, 'bold'),
                  relief=tk.FLAT, cursor="hand2", command=self.save_pua_config, pady=6).pack(fill=tk.X, pady=3)
        tk.Button(act_box, text="🔄 คืนค่าชิ้นส่วนนี้ (Reset Layer)", bg="#374151", fg="#d1d5db", font=('Segoe UI', 9),
                  relief=tk.FLAT, cursor="hand2", command=self.reset_current_layer).pack(fill=tk.X, pady=2)
        tk.Button(act_box, text="🚀 ติดตั้ง RomFS ฟอนต์เกม (Deploy)", bg="#2563eb", fg="#ffffff", font=('Segoe UI', 10, 'bold'),
                  relief=tk.FLAT, cursor="hand2", command=self.deploy_to_mod, pady=4).pack(fill=tk.X, pady=2)
        tk.Button(act_box, text="⚡ ติดตั้ง ExeFS Patch ตัวชิด (Proportional)", bg="#7c3aed", fg="#ffffff", font=('Segoe UI', 10, 'bold'),
                  relief=tk.FLAT, cursor="hand2", command=self.deploy_exefs_patch, pady=4).pack(fill=tk.X, pady=2)'''

new_act_box = '''        # Action Buttons (2 compact rows to prevent any vertical overflow)
        act_box = tk.Frame(left_f, bg="#1f2636")
        act_box.pack(fill=tk.X, padx=8, pady=(8, 4))
        
        row_act1 = tk.Frame(act_box, bg="#1f2636")
        row_act1.pack(fill=tk.X, pady=2)
        tk.Button(row_act1, text="⚡ จัดตัวชิดสวยงาม (Auto Tight)", bg="#8b5cf6", fg="#ffffff", font=('Segoe UI', 9, 'bold'),
                  relief=tk.FLAT, cursor="hand2", command=self.apply_auto_tight_spacing, pady=5).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 3))
        tk.Button(row_act1, text="💾 บันทึกค่า (Save)", bg="#10b981", fg="#ffffff", font=('Segoe UI', 9, 'bold'),
                  relief=tk.FLAT, cursor="hand2", command=self.save_pua_config, pady=5).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(3, 0))
                  
        row_act2 = tk.Frame(act_box, bg="#1f2636")
        row_act2.pack(fill=tk.X, pady=2)
        tk.Button(row_act2, text="🔄 คืนค่า (Reset)", bg="#374151", fg="#d1d5db", font=('Segoe UI', 9),
                  relief=tk.FLAT, cursor="hand2", command=self.reset_current_layer, pady=4).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 3))
        tk.Button(row_act2, text="🚀 ติดตั้ง RomFS (Deploy)", bg="#2563eb", fg="#ffffff", font=('Segoe UI', 9, 'bold'),
                  relief=tk.FLAT, cursor="hand2", command=self.deploy_to_mod, pady=4).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(3, 0))'''

assert old_act_box in code, "old_act_box not found!"
code = code.replace(old_act_box, new_act_box)

# 4. Widen canvas_pua_sentence so buttons never cut off on the right
code = code.replace('can_w = 800', 'can_w = 950')

with open(gui_path, "w", encoding="utf-8") as f:
    f.write(code)

print("Applied UI overflow fix successfully!")
