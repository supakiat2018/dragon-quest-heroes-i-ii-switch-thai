import os

gui_path = r"D:\Game\dragon quest heroes i & ii\switch\tools\thai_font_preview_gui.py"
with open(gui_path, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Update entry box in setup_tab_pua
old_entry_block = '''        tk.Label(top_bar, text=" หรือพิมพ์ผสมเอง:", bg="#1f2636", fg="#94a3b8", font=('Segoe UI', 10)).pack(side=tk.LEFT, padx=(10, 2))
        self.entry_custom_cluster = tk.Entry(top_bar, width=6, font=('Segoe UI', 11, 'bold'), bg="#10141d", fg="#ffffff", insertbackground="#ffffff")
        self.entry_custom_cluster.insert(0, "ริ่")
        self.entry_custom_cluster.pack(side=tk.LEFT, padx=2)
        tk.Button(top_bar, text="โหลด", bg="#3b82f6", fg="#ffffff", font=('Segoe UI', 9, 'bold'), relief=tk.FLAT,
                  command=lambda: self.select_pua_cluster(self.entry_custom_cluster.get().strip())).pack(side=tk.LEFT, padx=4)'''

new_entry_block = '''        tk.Label(top_bar, text=" หรือพิมพ์ข้อความ/ผสมเอง:", bg="#1f2636", fg="#94a3b8", font=('Segoe UI', 10)).pack(side=tk.LEFT, padx=(10, 2))
        self.entry_custom_cluster = tk.Entry(top_bar, width=32, font=('Segoe UI', 11, 'bold'), bg="#10141d", fg="#ffffff", insertbackground="#ffffff")
        self.entry_custom_cluster.insert(0, "เริ่มเล่นสร้างเซฟลบเซฟ")
        self.entry_custom_cluster.pack(side=tk.LEFT, padx=4)
        self.entry_custom_cluster.bind("<Return>", lambda e: self.on_load_custom_input())
        tk.Button(top_bar, text="โหลด (Load)", bg="#3b82f6", fg="#ffffff", font=('Segoe UI', 9, 'bold'), relief=tk.FLAT, cursor="hand2",
                  command=self.on_load_custom_input).pack(side=tk.LEFT, padx=4)'''

assert old_entry_block in code, "old_entry_block not found!"
code = code.replace(old_entry_block, new_entry_block)

# 2. Fix startup cluster call from เริ่ to ริ่
code = code.replace('self.select_pua_cluster("เริ่")', 'self.select_pua_cluster("ริ่")')

# 3. Update select_pua_cluster and add on_load_custom_input
old_select_fn = '''    def select_pua_cluster(self, c_text):
        if not c_text:
            return
        self.current_cluster = c_text
        self.entry_custom_cluster.delete(0, tk.END)
        self.entry_custom_cluster.insert(0, c_text)
        self.lbl_pua_cluster_title.config(text=f"คลัสเตอร์: [ {c_text} ]")'''

new_select_fn = '''    def on_load_custom_input(self):
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

assert old_select_fn in code, "old_select_fn not found!"
code = code.replace(old_select_fn, new_select_fn)

# 4. In setup_tab_test (Tab 3):
code = code.replace(
    'self.entry_test.insert(0, "เริ่มเล่น   สร้างเซฟ   ลบเซฟ")',
    'self.entry_test.insert(0, "เริ่มเล่นสร้างเซฟลบเซฟ")'
)

with open(gui_path, "w", encoding="utf-8") as f:
    f.write(code)

print("Patch applied successfully to thai_font_preview_gui.py!")
