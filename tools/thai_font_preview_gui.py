"""
thai_font_preview_gui.py
โปรแกรมปรับแต่งและประกอบฟอนต์ไทย PUA แบบแยกเลเยอร์อิสระ (PUA Multi-Layer Cluster Composer)
สำหรับ Dragon Quest Heroes I & II (Nintendo Switch)

คุณสมบัติหลัก:
1. แท็บ 1 [🧩 ปรับแต่ง PUA รวมคลัสเตอร์ (Multi-Layer Composer)]:
   - เลือกคลัสเตอร์ เช่น "เริ่", "ร้", "ล่" หรือพิมพ์คำผสมใดๆ ได้อิสระ
   - สามารถเลือกปรับแยกชิ้นส่วนได้ตามใจชอบ 100%:
     * ปรับ สระหน้า 'เ' (เลื่อน ซ้าย/ขวา/บน/ล่าง, ขยายความกว้าง/ความสูง)
     * ปรับ พยัญชนะ 'ร' (ขยับเข้าใกล้ 'เ', ปรับความอ้วน)
     * ปรับ สระบน 'ิ' (ยกสูงขึ้น/กดต่ำลง, เลื่อนซ้าย/ขวา)
     * ปรับ วรรณยุกต์ '่' (ยกสูง, ขยับหลบขวา, ขยายขนาด)
     * ปรับ รวมทั้งก้อน (ขยับตำแหน่งกึ่งกลางในช่อง 36x36)
   - พรีวิวซูมขนาดใหญ่ 8x มีกรอบสีทองไฮไลต์ชิ้นส่วนที่กำลังปรับแบบสดๆ
   - พรีวิวประโยคจริงในเกม (เริ่มเล่น สร้างเซฟ ลบเซฟ) อัปเดต Real-time
   - ปุ่ม [💾 บันทึกค่าคอนฟิก PUA] เซฟลงไฟล์ thai_glyph_tuning.json
   - ปุ่ม [🚀 ติดตั้งเข้า Mod เกมจริง] ฉีดเข้า RomFS (Ryujinx, Yuzu, Atmosphere) ทันที
2. แท็บ 2 [🎛️ ปรับแต่งตัวอักษรเดี่ยว (Single Glyph Tuner)]:
   - ปรับตำแหน่งและขนาดตัวอักษรเดี่ยว ก-ฮ, สระ, วรรณยุกต์
3. แท็บ 3 [📝 ทดสอบคำและประโยค (Word Tester)]
4. แท็บ 4 [📋 ตารางอักขระครบทุกตัว (Character Atlas)]
"""

import os
import sys
import json
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import numpy as np
from PIL import Image, ImageFont, ImageDraw, ImageTk

BASE_DIR = r"D:\Game\dragon quest heroes i & ii"
SWITCH_DIR = os.path.join(BASE_DIR, "switch")
TOOLS_DIR = os.path.join(SWITCH_DIR, "tools")
FONT_TTF = os.path.join(SWITCH_DIR, "fonts", "Pridi-Bold.ttf")
CONFIG_JSON = os.path.join(TOOLS_DIR, "thai_glyph_tuning.json")
DEPLOY_SCRIPT = os.path.join(TOOLS_DIR, "deploy_perfect_thai_menus_romfs.py")

f32 = ImageFont.truetype(FONT_TTF, 32)
f_mark = ImageFont.truetype(FONT_TTF, 28)

UPPER_MARKS = set('\u0e31\u0e34\u0e35\u0e36\u0e37\u0e4d')
LOWER_MARKS = set('\u0e38\u0e39\u0e3a')
TONE_MARKS  = set('\u0e48\u0e49\u0e4a\u0e4b\u0e4c\u0e47')

ALL_THAI_CHARS = [
    'ก', 'ข', 'ฃ', 'ค', 'ฅ', 'ฆ', 'ง', 'จ', 'ฉ', 'ช', 'ซ', 'ฌ', 'ญ', 'ฎ', 'ฏ',
    'ฐ', 'ฑ', 'ฒ', 'ณ', 'ด', 'ต', 'ถ', 'ท', 'ธ', 'น', 'บ', 'ป', 'ผ', 'ฝ', 'พ',
    'ฟ', 'ภ', 'ม', 'ย', 'ร', 'ล', 'ว', 'ศ', 'ษ', 'ส', 'ห', 'ฬ', 'อ', 'ฮ',
    'ะ', 'า', 'ำ', 'เ', 'แ', 'โ', 'ใ', 'ไ', 'ฤ', 'ฦ', 'ๅ',
    'ิ', 'ี', 'ึ', 'ื', 'ุ', 'ู', 'ั', '็',
    '่', '้', '๊', '๋', '์', 'ๆ', 'ฯ'
]

QUICK_CHARS = ['ก', 'เ', 'ร', 'ิ', '่', 'ม', 'ล', 'น', 'ส', '้', 'า', 'ง', 'ซ', 'ฟ', 'บ', 'ด', 'ต', 'ป', 'ะ', 'ู']

def get_glyph_crop(ch):
    font = f_mark if (ch in UPPER_MARKS or ch in LOWER_MARKS or ch in TONE_MARKS) else f32
    t = Image.new('RGBA', (80, 80), (0, 0, 0, 0))
    if ch in UPPER_MARKS or ch in TONE_MARKS:
        ImageDraw.Draw(t).text((40, 44), ch, font=font, fill=(255, 255, 255, 255), anchor='ms')
    elif ch in LOWER_MARKS:
        ImageDraw.Draw(t).text((40, 76), ch, font=font, fill=(255, 255, 255, 255), anchor='ms')
    else:
        ImageDraw.Draw(t).text((40, 60), ch, font=font, fill=(255, 255, 255, 255), anchor='ms')
        
    coords = np.argwhere(np.array(t)[:, :, 3] > 20)
    if len(coords) == 0:
        return Image.new('RGBA', (5, 5), (0, 0, 0, 0))
    return t.crop((coords[:, 1].min(), coords[:, 0].min(), coords[:, 1].max() + 1, coords[:, 0].max() + 1))

def get_natural_glyph_metrics(ch):
    cr = get_glyph_crop(ch)
    if ch in ['ป', 'ฝ', 'ฟ', 'ฬ']:
        return cr.width, 25
    elif ch in ['ส', 'ฮ', 'ศ']:
        return cr.width, 20
    elif ch in ['ญ', 'ฎ', 'ฏ']:
        return cr.width, 25
    elif ch == 'ฐ':
        return cr.width, 29
    elif ch in 'โใไ':
        return 14, 26
    elif ch in 'าะ':
        return 14, 19
    elif ch == 'เ':
        return 10, 19
    elif ch == 'แ':
        return 18, 19
    elif ch == 'ำ':
        return 21, 27
    elif ch == 'ๅ':
        return 14, 25
    elif ch in UPPER_MARKS:
        return 15, 6
    elif ch in LOWER_MARKS or ch in TONE_MARKS:
        return cr.width, cr.height
    else:
        # Standard consonants ก-ฮ (Uniform 19px body height)
        return cr.width, 19

def load_or_create_config():
    if os.path.exists(CONFIG_JSON):
        try:
            with open(CONFIG_JSON, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
                if 'clusters' not in cfg:
                    cfg['clusters'] = {}
                return cfg
        except Exception:
            pass
            
    cfg = {
        'version': '2.0',
        'global': {'baseline': 32},
        'glyphs': {},
        'clusters': {}
    }
    for ch in ALL_THAI_CHARS:
        w, h = get_natural_glyph_metrics(ch)
        cfg['glyphs'][ch] = {
            'offset_x': 0, 'offset_y': 0,
            'width': w, 'height': h,
            'natural_w': w, 'natural_h': h
        }
    return cfg

def save_config(cfg):
    with open(CONFIG_JSON, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)

# Render single glyph with user tuning
def render_tuned_single_glyph(ch, config, baseline=32):
    cell = Image.new('RGBA', (36, 36), (0, 0, 0, 0))
    if not ch or ch == ' ':
        return cell
        
    g_info = config.get('glyphs', {}).get(ch, {})
    if ch in UPPER_MARKS:
        default_ox, default_oy, default_w, default_h = 0, -3, 15, 6
    elif ch in 'เแโใไ':
        default_w = 18 if ch == 'แ' else (14 if ch in 'โใไ' else 10)
        default_h = 26 if ch in 'โใไ' else 19
        default_ox, default_oy = 18, 1
    elif ch in 'าะ':
        default_ox, default_oy, default_w, default_h = -7, 0, 14, 19
    elif ch == 'ำ':
        default_ox, default_oy, default_w, default_h = -2, 0, 21, 27
    elif ch == 'ๅ':
        default_ox, default_oy, default_w, default_h = -2, 0, 14, 25
    else:
        nat_w, nat_h = get_natural_glyph_metrics(ch)
        default_ox, default_oy, default_w, default_h = 0, 0, nat_w, nat_h
        
    off_x = g_info.get('offset_x', default_ox)
    off_y = g_info.get('offset_y', default_oy)
    target_w = g_info.get('width', default_w)
    target_h = g_info.get('height', default_h)
    
    cr = get_glyph_crop(ch)
    if target_w == cr.width and target_h == cr.height:
        glyph_img = cr
    else:
        tw = max(4, min(36, target_w))
        th = max(4, min(36, target_h))
        glyph_img = cr.resize((tw, th), Image.Resampling.LANCZOS)
        
    gw, gh = glyph_img.size
    cx = (36 - gw) // 2 + off_x
    if ch in LOWER_MARKS:
        cy = baseline + 2 + off_y
    elif ch in UPPER_MARKS or ch in TONE_MARKS:
        cy = baseline - 19 - gh + off_y
    else:
        cy = baseline - gh + off_y
        
    cx = max(0, min(36 - gw, cx))
    cy = max(0, min(36 - gh, cy))
    cell.paste(glyph_img, (cx, cy), glyph_img)
    return cell

# Compose multi-layer PUA cluster (e.g. 'เริ่', 'ร้', 'ล่') with 1:1 direct cell placement (NO auto-shrinking!)
def compose_pua_cluster_image(cluster_text, config, highlight_part=None, baseline=32):
    cell = Image.new('RGBA', (36, 36), (0, 0, 0, 0))
    if not cluster_text:
        return cell, {}
        
    c_info = config.get('clusters', {}).get(cluster_text, {})
    layers = c_info.get('layers', {})
    whole_ox = c_info.get('whole_ox', 0)
    whole_oy = c_info.get('whole_oy', 0)
    
    # Identify parts
    lead_ch = cluster_text[0] if cluster_text[0] in 'เแโใไ' and len(cluster_text) > 1 else ''
    rest = cluster_text[1:] if lead_ch else cluster_text
    base_ch = rest[0] if rest else ''
    up_ch = ''.join([c for c in rest[1:] if c in UPPER_MARKS])[:1] if len(rest) > 1 else ''
    tone_ch = ''.join([c for c in rest[1:] if c in TONE_MARKS])[:1] if len(rest) > 1 else ''
    low_ch = ''.join([c for c in rest[1:] if c in LOWER_MARKS])[:1] if len(rest) > 1 else ''
    
    layer_bounds = {}
    
    # 1. Lead (e.g. เ)
    if lead_ch:
        l_cfg = layers.get(lead_ch, {})
        ox = l_cfg.get('offset_x', -2) + whole_ox
        oy = l_cfg.get('offset_y', 0) + whole_oy
        cr_l = get_glyph_crop(lead_ch)
        nat_w, nat_h = cr_l.width, cr_l.height
        default_w = 18 if lead_ch == 'แ' else (14 if lead_ch in 'โใไ' else 10)
        default_h = 26 if lead_ch in 'โใไ' else 19
        w = max(4, l_cfg.get('width', default_w))
        h = max(4, l_cfg.get('height', default_h))
        sc_l = cr_l if (w == nat_w and h == nat_h) else cr_l.resize((w, h), Image.Resampling.LANCZOS)
        
        pos_x_l = 3 + ox
        pos_y_l = baseline - h + oy
        cell.paste(sc_l, (pos_x_l, pos_y_l), sc_l)
        layer_bounds[lead_ch] = (pos_x_l, pos_y_l, w, h)
        x_base_start = pos_x_l + w + 1
    else:
        x_base_start = (36 - 18) // 2 + whole_ox
        
    # 2. Base (e.g. ร)
    if base_ch:
        b_cfg = layers.get(base_ch, {})
        ox = b_cfg.get('offset_x', 0)
        oy = b_cfg.get('offset_y', 0) + whole_oy
        cr_b = get_glyph_crop(base_ch)
        nat_w, nat_h = get_natural_glyph_metrics(base_ch)
        w_b = max(4, b_cfg.get('width', nat_w))
        h_b = max(4, b_cfg.get('height', nat_h))
        sc_b = cr_b if (w_b == cr_b.width and h_b == cr_b.height) else cr_b.resize((w_b, h_b), Image.Resampling.LANCZOS)
        
        if lead_ch:
            pos_x_b = x_base_start + ox
        else:
            pos_x_b = max(0, min(36 - w_b, (36 - w_b) // 2 + whole_ox + ox))
        pos_y_b = max(0, min(36 - h_b, baseline - h_b + oy))
        cell.paste(sc_b, (pos_x_b, pos_y_b), sc_b)
        layer_bounds[base_ch] = (pos_x_b, pos_y_b, w_b, h_b)
    else:
        pos_x_b, pos_y_b, w_b, h_b = 10, baseline - 19, 18, 19
        
    # 3. Upper mark (e.g. ิ)
    y_top = pos_y_b
    if up_ch:
        u_cfg = layers.get(up_ch, {})
        ox = u_cfg.get('offset_x', 0)
        oy = u_cfg.get('offset_y', -3)
        cr_u = get_glyph_crop(up_ch)
        nat_w, nat_h = cr_u.width, cr_u.height
        w_u = max(4, u_cfg.get('width', 15))
        h_u = max(4, u_cfg.get('height', 6))
        sc_u = cr_u if (w_u == nat_w and h_u == nat_h) else cr_u.resize((w_u, h_u), Image.Resampling.LANCZOS)
        
        pos_x_u = pos_x_b + (w_b - w_u) // 2 + ox
        pos_y_u = pos_y_b - h_u + 2 + oy
        cell.paste(sc_u, (pos_x_u, pos_y_u), sc_u)
        layer_bounds[up_ch] = (pos_x_u, pos_y_u, w_u, h_u)
        y_top = pos_y_u
        
    # 4. Tone mark (e.g. ่)
    if tone_ch:
        t_cfg = layers.get(tone_ch, {})
        ox = t_cfg.get('offset_x', 0)
        oy = t_cfg.get('offset_y', 0)
        cr_t = get_glyph_crop(tone_ch)
        nat_w, nat_h = cr_t.width, cr_t.height
        w_t = max(4, t_cfg.get('width', nat_w))
        h_t = max(4, t_cfg.get('height', nat_h))
        sc_t = cr_t if (w_t == nat_w and h_t == nat_h) else cr_t.resize((w_t, h_t), Image.Resampling.LANCZOS)
        
        pos_x_t = pos_x_b + w_b - w_t - 1 + ox
        pos_y_t = y_top - h_t - 1 + oy
        cell.paste(sc_t, (pos_x_t, pos_y_t), sc_t)
        layer_bounds[tone_ch] = (pos_x_t, pos_y_t, w_t, h_t)
        
    # 5. Lower mark (e.g. ุ)
    if low_ch:
        l_cfg = layers.get(low_ch, {})
        ox = l_cfg.get('offset_x', 0)
        oy = l_cfg.get('offset_y', 0)
        cr_l = get_glyph_crop(low_ch)
        nat_w, nat_h = cr_l.width, cr_l.height
        w_l = max(4, l_cfg.get('width', nat_w))
        h_l = max(4, l_cfg.get('height', nat_h))
        sc_l = cr_l if (w_l == nat_w and h_l == nat_h) else cr_l.resize((w_l, h_l), Image.Resampling.LANCZOS)
        
        pos_x_l = pos_x_b + (w_b - w_l) // 2 + ox
        pos_y_l = baseline + 2 + oy
        cell.paste(sc_l, (pos_x_l, pos_y_l), sc_l)
        layer_bounds[low_ch] = (pos_x_l, pos_y_l, w_l, h_l)
        
    return cell, layer_bounds

class ThaiFontMasterStudio(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Dragon Quest Heroes II - สตูดิโอปรับแต่งฟอนต์ไทย PUA แบบแยกเลเยอร์อิสระ")
        self.geometry("1120x640")
        self.minsize(960, 500)
        self.configure(bg="#161a24")
        
        self.config_data = load_or_create_config()
        self.ensure_default_clusters()
        
        self.current_cluster = "ริ่"
        self.current_layer_part = "whole"
        self.custom_preview_text = "" # 'whole', or char like 'เ', 'ร', 'ิ', '่'
        
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure("TNotebook", background="#161a24", borderwidth=0)
        style.configure("TNotebook.Tab", background="#222b3d", foreground="#cbd5e1", padding=[16, 7], font=('Segoe UI', 11, 'bold'))
        style.map("TNotebook.Tab", background=[("selected", "#2563eb")], foreground=[("selected", "#ffffff")])
        
        # TOP BAR: Font Selector
        top_bar = tk.Frame(self, bg="#1e2433")
        top_bar.pack(fill=tk.X, padx=10, pady=(8, 4))
        
        tk.Label(top_bar, text="🔤 ฟอนต์ที่ใช้งานอยู่:", bg="#1e2433", fg="#94a3b8", font=('Segoe UI', 9, 'bold')).pack(side=tk.LEFT, padx=(10, 5), pady=6)
        self.lbl_current_font = tk.Label(top_bar, text=os.path.basename(FONT_TTF), bg="#1e2433", fg="#38bdf8", font=('Segoe UI', 10, 'bold'))
        self.lbl_current_font.pack(side=tk.LEFT, padx=5, pady=6)
        
        tk.Button(top_bar, text="📂 เลือกฟอนต์อื่นในเครื่อง (.ttf / .otf)", bg="#2563eb", fg="#ffffff", font=('Segoe UI', 9, 'bold'),
                  relief=tk.FLAT, cursor="hand2", command=self.browse_custom_font, padx=12, pady=3).pack(side=tk.RIGHT, padx=10, pady=5)
        
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # TAB 1: PUA Cluster Composer (Hero feature requested by user!)
        self.tab_pua = tk.Frame(self.notebook, bg="#161a24")
        self.notebook.add(self.tab_pua, text="  🧩 ปรับแต่ง PUA รวมคลัสเตอร์ (Multi-Layer Composer)  ")
        
        # TAB 2: Single Glyph Tuner
        self.tab_tuner = tk.Frame(self.notebook, bg="#161a24")
        self.notebook.add(self.tab_tuner, text="  🎛️ ปรับแต่งตัวอักษรเดี่ยว (Single Glyph Tuner)  ")
        
        # TAB 3: Word Tester
        self.tab_test = tk.Frame(self.notebook, bg="#161a24")
        self.notebook.add(self.tab_test, text="  📝 ทดสอบคำและประโยค (Word Tester)  ")
        
        # TAB 4: Character Atlas
        self.tab_atlas = tk.Frame(self.notebook, bg="#161a24")
        self.notebook.add(self.tab_atlas, text="  📋 ตารางอักขระครบทุกตัว (Character Atlas)  ")
        
        self.setup_tab_pua()
        self.setup_tab_single_tuner()
        self.setup_tab_test()
        self.setup_tab_atlas()
        
    def ensure_default_clusters(self):
        if 'clusters' not in self.config_data:
            self.config_data['clusters'] = {}
        for c in ["ริ่", "ร้", "ล่", "ชื่", "ตั้", "กิ่", "กิ้"]:
            if c not in self.config_data['clusters']:
                self.config_data['clusters'][c] = {
                    'whole_ox': 0, 'whole_oy': 0,
                    'layers': {}
                }
                for ch in c:
                    nw, nh = get_natural_glyph_metrics(ch)
                    self.config_data['clusters'][c]['layers'][ch] = {
                        'offset_x': 0, 'offset_y': 0,
                        'width': nw, 'height': nh
                    }
        # Permanent lock for leading vowels: เ, แ, โ, ใ, ไ (Offset X = +18, Offset Y = +1)
        if 'glyphs' not in self.config_data:
            self.config_data['glyphs'] = {}
        for lv in 'เแโใไ':
            if lv not in self.config_data['glyphs']:
                self.config_data['glyphs'][lv] = {
                    'offset_x': 18, 'offset_y': 1,
                    'width': 18 if lv == 'แ' else (14 if lv in 'โใไ' else 10),
                    'height': 26 if lv in 'โใไ' else 19
                }
            elif self.config_data['glyphs'][lv].get('offset_x', 0) == 0:
                self.config_data['glyphs'][lv]['offset_x'] = 18
                self.config_data['glyphs'][lv]['offset_y'] = 1
                    
    # ================= TAB 1: PUA CLUSTER COMPOSER =================
    def setup_tab_pua(self):
        top_bar = tk.Frame(self.tab_pua, bg="#1f2636", relief=tk.RAISED, bd=1)
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
                  command=self.on_load_custom_input).pack(side=tk.LEFT)
                  
        work = tk.Frame(self.tab_pua, bg="#161a24")
        work.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Left Panel: Sub-layer selectors, Action Toolbar, and compact Sliders
        left_f = tk.LabelFrame(work, text=" แผงปรับแต่งชิ้นส่วนย่อย (Layer Parts) ", bg="#1f2636", fg="#f0c050", font=('Segoe UI', 10, 'bold'), bd=1)
        left_f.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10), pady=2, ipadx=6, ipady=4)
        
        self.lbl_pua_cluster_title = tk.Label(left_f, text="เป้าหมาย: [ ริ่ ]", bg="#121622", fg="#fde047", font=('Segoe UI', 11, 'bold'), relief=tk.RIDGE, bd=1)
        self.lbl_pua_cluster_title.pack(fill=tk.X, padx=6, pady=(3, 3), ipady=2)
        
        # Sub-layer Buttons
        tk.Label(left_f, text="1. เลือกชิ้นส่วนที่ต้องการขยับ/ปรับขนาด:", bg="#1f2636", fg="#38bdf8", font=('Segoe UI', 9, 'bold')).pack(anchor=tk.W, padx=6, pady=(2, 1))
        self.layer_btn_frame = tk.Frame(left_f, bg="#1f2636")
        self.layer_btn_frame.pack(fill=tk.X, padx=6, pady=1)
        self.layer_buttons = {}
        
        self.lbl_active_layer = tk.Label(left_f, text="กำลังปรับ: [ รวมทั้งก้อน ]", bg="#2a354c", fg="#a7f3d0", font=('Segoe UI', 9, 'bold'), relief=tk.GROOVE)
        self.lbl_active_layer.pack(fill=tk.X, padx=6, pady=(2, 5), ipady=2)
        
        # Action Toolbar (PROMINENT AT TOP: Guaranteed 100% visible, cannot be pushed off-screen!)
        act_box = tk.LabelFrame(left_f, text=" ⚡ คำสั่งหลัก (Action Toolbar) ", bg="#1f2636", fg="#c084fc", font=('Segoe UI', 9, 'bold'), bd=1)
        act_box.pack(fill=tk.X, padx=6, pady=(0, 5), ipadx=4, ipady=3)
        
        row_act1 = tk.Frame(act_box, bg="#1f2636")
        row_act1.pack(fill=tk.X, pady=2)
        self.btn_auto_tight = tk.Button(row_act1, text="⚡ จัดตัวชิดสวยงาม (Auto Tight)", bg="#7c3aed", fg="#ffffff", activebackground="#6d28d9", font=('Segoe UI', 9, 'bold'),
                                        relief=tk.RAISED, bd=2, cursor="hand2", command=self.apply_auto_tight_spacing, pady=5)
        self.btn_auto_tight.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 3))
        self.btn_save = tk.Button(row_act1, text="💾 บันทึกค่า (Save)", bg="#059669", fg="#ffffff", activebackground="#047857", font=('Segoe UI', 9, 'bold'),
                                  relief=tk.RAISED, bd=2, cursor="hand2", command=self.save_pua_config, pady=5)
        self.btn_save.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(3, 0))
                  
        row_act2 = tk.Frame(act_box, bg="#1f2636")
        row_act2.pack(fill=tk.X, pady=2)
        tk.Button(row_act2, text="🔄 คืนค่า (Reset)", bg="#374151", fg="#d1d5db", font=('Segoe UI', 9),
                  relief=tk.FLAT, cursor="hand2", command=self.reset_current_layer, pady=3).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 3))
        tk.Button(row_act2, text="🚀 ติดตั้ง RomFS (Deploy)", bg="#2563eb", fg="#ffffff", font=('Segoe UI', 9, 'bold'),
                  relief=tk.FLAT, cursor="hand2", command=self.deploy_to_mod, pady=3).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(3, 0))
        
        # Sliders Frame (Ultra Compact 2x2 Grid Layout)
        slider_box = tk.LabelFrame(left_f, text=" ตำแหน่งและขนาดของชิ้นส่วน (2x2 Grid) ", bg="#1f2636", fg="#4ade80", font=('Segoe UI', 9, 'bold'), bd=1)
        slider_box.pack(fill=tk.X, padx=6, pady=2, ipadx=4, ipady=3)
        
        f_grid = tk.Frame(slider_box, bg="#1f2636")
        f_grid.pack(fill=tk.X, padx=2, pady=2)
        f_grid.columnconfigure(0, weight=1)
        f_grid.columnconfigure(1, weight=1)
        
        # Row 0, Col 0: Offset X
        c00 = tk.Frame(f_grid, bg="#1f2636")
        c00.grid(row=0, column=0, sticky="ew", padx=3, pady=2)
        tk.Label(c00, text="↔ เลื่อน X (ซ้าย-ขวา):", bg="#1f2636", fg="#cbd5e1", font=('Segoe UI', 8, 'bold')).pack(anchor=tk.W)
        fx_in = tk.Frame(c00, bg="#1f2636")
        fx_in.pack(fill=tk.X)
        self.pua_sl_ox = tk.Scale(fx_in, from_=-18, to=18, orient=tk.HORIZONTAL, bg="#1f2636", fg="#ffffff", highlightthickness=0, length=110, command=self.on_pua_slider_change)
        self.pua_sl_ox.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.lbl_pua_ox = tk.Label(fx_in, text="0 px", bg="#1f2636", fg="#38bdf8", font=('Segoe UI', 8, 'bold'), width=5)
        self.lbl_pua_ox.pack(side=tk.LEFT)
        
        # Row 0, Col 1: Width
        c01 = tk.Frame(f_grid, bg="#1f2636")
        c01.grid(row=0, column=1, sticky="ew", padx=3, pady=2)
        tk.Label(c01, text="↔ ความกว้าง (W):", bg="#1f2636", fg="#cbd5e1", font=('Segoe UI', 8, 'bold')).pack(anchor=tk.W)
        fw_in = tk.Frame(c01, bg="#1f2636")
        fw_in.pack(fill=tk.X)
        self.pua_sl_w = tk.Scale(fw_in, from_=4, to=36, orient=tk.HORIZONTAL, bg="#1f2636", fg="#ffffff", highlightthickness=0, length=110, command=self.on_pua_slider_change)
        self.pua_sl_w.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.lbl_pua_w = tk.Label(fw_in, text="18 px", bg="#1f2636", fg="#4ade80", font=('Segoe UI', 8, 'bold'), width=5)
        self.lbl_pua_w.pack(side=tk.LEFT)
        
        # Row 1, Col 0: Offset Y
        c10 = tk.Frame(f_grid, bg="#1f2636")
        c10.grid(row=1, column=0, sticky="ew", padx=3, pady=2)
        tk.Label(c10, text="↕ เลื่อน Y (ขึ้น-ลง):", bg="#1f2636", fg="#cbd5e1", font=('Segoe UI', 8, 'bold')).pack(anchor=tk.W)
        fy_in = tk.Frame(c10, bg="#1f2636")
        fy_in.pack(fill=tk.X)
        self.pua_sl_oy = tk.Scale(fy_in, from_=-18, to=18, orient=tk.HORIZONTAL, bg="#1f2636", fg="#ffffff", highlightthickness=0, length=110, command=self.on_pua_slider_change)
        self.pua_sl_oy.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.lbl_pua_oy = tk.Label(fy_in, text="0 px", bg="#1f2636", fg="#38bdf8", font=('Segoe UI', 8, 'bold'), width=5)
        self.lbl_pua_oy.pack(side=tk.LEFT)
        
        # Row 1, Col 1: Height
        c11 = tk.Frame(f_grid, bg="#1f2636")
        c11.grid(row=1, column=1, sticky="ew", padx=3, pady=2)
        tk.Label(c11, text="↕ ความสูง (H):", bg="#1f2636", fg="#cbd5e1", font=('Segoe UI', 8, 'bold')).pack(anchor=tk.W)
        fh_in = tk.Frame(c11, bg="#1f2636")
        fh_in.pack(fill=tk.X)
        self.pua_sl_h = tk.Scale(fh_in, from_=4, to=36, orient=tk.HORIZONTAL, bg="#1f2636", fg="#ffffff", highlightthickness=0, length=110, command=self.on_pua_slider_change)
        self.pua_sl_h.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.lbl_pua_h = tk.Label(fh_in, text="18 px", bg="#1f2636", fg="#4ade80", font=('Segoe UI', 8, 'bold'), width=5)
        self.lbl_pua_h.pack(side=tk.LEFT)
                  
        # Right Previews
        right_f = tk.Frame(work, bg="#161a24")
        right_f.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        zoom_frame = tk.LabelFrame(right_f, text=" พรีวิวคลัสเตอร์ PUA ซูมขยายใหญ่ 8x (แสดงผลสดตามสไลเดอร์) ", bg="#1f2636", fg="#f0c050", font=('Segoe UI', 11, 'bold'), bd=1)
        zoom_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 6))
        
        self.canvas_pua_zoom = tk.Canvas(zoom_frame, bg="#0d1117", highlightthickness=0, width=288, height=288)
        self.canvas_pua_zoom.pack(side=tk.LEFT, padx=15, pady=10)
        
        pua_info_f = tk.Frame(zoom_frame, bg="#1f2636")
        pua_info_f.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.lbl_pua_detail = tk.Label(pua_info_f, text="", bg="#1f2636", fg="#e2e8f0", font=('Segoe UI', 11), justify=tk.LEFT)
        self.lbl_pua_detail.pack(anchor=tk.NW, pady=5)
        
        tk.Label(pua_info_f, text="⭐ ไฮไลต์สีทอง = ขอบเขตของชิ้นส่วนที่กำลังปรับเลื่อนอยู่\n- คุณสามารถคลิกเลือกปรับทีละตัว เช่น ปรับแค่ 'เ' หรือแค่ 'ิ' หรือแค่ '่' ได้อย่างอิสระ 100%!\n- เส้นขอบฟ้า = กรอบ 36×36 px ในเอนจิ้นเกมจริง",
                 bg="#1e2433", fg="#94a3b8", font=('Segoe UI', 9), justify=tk.LEFT, relief=tk.GROOVE, padx=10, pady=8).pack(anchor=tk.SW, fill=tk.X, pady=10)
                 
        sentence_frame = tk.LabelFrame(right_f, text=" พรีวิวในปุ่มเมนูเกมจริง (Real-Time In-Game Buttons) ", bg="#1f2636", fg="#f0c050", font=('Segoe UI', 11, 'bold'), bd=1)
        sentence_frame.pack(fill=tk.X, pady=(6, 0))
        
        self.canvas_pua_sentence = tk.Canvas(sentence_frame, bg="#121622", highlightthickness=0, height=80)
        self.canvas_pua_sentence.pack(fill=tk.X, padx=10, pady=10)
        
        self.select_pua_cluster("ริ่")
        
    def on_load_custom_input(self):
        txt = self.entry_custom_cluster.get().strip()
        if not txt:
            return
        self.custom_preview_text = txt
        self.select_pua_cluster(txt, sync_entry=False)
        self.update_pua_sentence()

    def select_pua_cluster(self, c_text, sync_entry=True):
        if not c_text:
            return
        if sync_entry:
            self.custom_preview_text = ""
            self.entry_custom_cluster.delete(0, tk.END)
            self.entry_custom_cluster.insert(0, c_text)
            
        LEAD_VOWELS = set('เแโใไ')
        TRAIL_VOWELS = set('ะาำฤฦๅ')
        
        # Tokenize c_text into Thai structural tokens
        tokens = []
        i = 0
        n = len(c_text)
        while i < n:
            ch = c_text[i]
            if ch in LEAD_VOWELS:
                tokens.append(('lead_vowel', ch))
                i += 1
            elif ch in TRAIL_VOWELS:
                tokens.append(('trail_vowel', ch))
                i += 1
            elif ch in UPPER_MARKS or ch in LOWER_MARKS or ch in TONE_MARKS:
                tokens.append(('mark', ch))
                i += 1
            elif ch in (' ', '   '):
                i += 1
            else:
                combo = ch
                j = i + 1
                while j < n and (c_text[j] in UPPER_MARKS or c_text[j] in LOWER_MARKS or c_text[j] in TONE_MARKS):
                    combo += c_text[j]
                    j += 1
                if len(combo) > 1:
                    tokens.append(('cluster', combo))
                else:
                    tokens.append(('consonant', combo))
                i = j

        # Identify active cluster or character
        cluster_tokens = [tok for t_type, tok in tokens if t_type == 'cluster']
        if cluster_tokens:
            self.current_cluster = cluster_tokens[0]
        elif len(c_text) <= 3 and not any(t_type in ('lead_vowel', 'trail_vowel') for t_type, _ in tokens):
            self.current_cluster = c_text
        else:
            self.current_cluster = tokens[0][1] if tokens else "ริ่"

        if len(c_text) > 3 or any(t_type in ('lead_vowel', 'trail_vowel') for t_type, _ in tokens):
            self.lbl_pua_cluster_title.config(text=f"เป้าหมาย: [ {self.current_cluster} ] (จากคำ: '{c_text}')")
        else:
            self.lbl_pua_cluster_title.config(text=f"คลัสเตอร์ PUA: [ {self.current_cluster} ]")
        
        # If current_cluster is a true vertical cluster, ensure default structure in config
        if len(self.current_cluster) > 1:
            if self.current_cluster not in self.config_data.get('clusters', {}):
                self.config_data.setdefault('clusters', {})[self.current_cluster] = {
                    'whole_ox': 0, 'whole_oy': 0,
                    'layers': {}
                }
                for ch in self.current_cluster:
                    nw, nh = get_natural_glyph_metrics(ch)
                    self.config_data['clusters'][self.current_cluster]['layers'][ch] = {
                        'offset_x': 0, 'offset_y': 0,
                        'width': nw, 'height': nh
                    }

        # Rebuild layer buttons dynamically
        for w in self.layer_btn_frame.winfo_children():
            w.destroy()
            
        self.layer_buttons = {}
        
        # If active target is a cluster (length > 1), show 'whole' button
        if len(self.current_cluster) > 1:
            btn_whole = tk.Button(self.layer_btn_frame, text=f"รวมทั้งก้อน [{self.current_cluster}]", font=('Segoe UI', 9, 'bold'), bg="#374151", fg="#ffffff",
                                  relief=tk.FLAT, cursor="hand2", command=lambda: self.select_pua_layer_part('whole'))
            btn_whole.pack(side=tk.LEFT, padx=2, pady=1)
            self.layer_buttons['whole'] = btn_whole

        added_parts = set()
        default_part_to_select = 'whole' if len(self.current_cluster) > 1 else None
        
        for t_type, tok in tokens:
            if tok in added_parts:
                continue
            added_parts.add(tok)
            
            if t_type == 'cluster':
                for ch in tok:
                    if ch in added_parts:
                        continue
                    added_parts.add(ch)
                    desc = f"วรรณยุกต์ '{ch}'" if ch in TONE_MARKS else (f"สระบน '{ch}'" if ch in UPPER_MARKS else f"พยัญชนะ '{ch}'")
                    b = tk.Button(self.layer_btn_frame, text=desc, font=('Segoe UI', 9, 'bold'), bg="#2b354c", fg="#cbd5e1",
                                  relief=tk.FLAT, cursor="hand2", command=lambda p=ch: self.select_pua_layer_part(p))
                    b.pack(side=tk.LEFT, padx=2, pady=1)
                    self.layer_buttons[ch] = b
            else:
                desc = f"สระ '{tok}'" if t_type == 'lead_vowel' else (f"สระตาม '{tok}'" if t_type == 'trail_vowel' else f"พยัญชนะ '{tok}'")
                b = tk.Button(self.layer_btn_frame, text=desc, font=('Segoe UI', 9, 'bold'), bg="#2b354c", fg="#cbd5e1",
                              relief=tk.FLAT, cursor="hand2", command=lambda p=tok: self.select_pua_layer_part(p))
                b.pack(side=tk.LEFT, padx=2, pady=1)
                self.layer_buttons[tok] = b
                if default_part_to_select is None:
                    default_part_to_select = tok

        if default_part_to_select is None:
            default_part_to_select = 'whole'
        self.select_pua_layer_part(default_part_to_select)
        
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
                if 'height' in l_cfg: h = l_cfg['height']
            
        self.pua_sl_ox.set(ox)
        self.pua_sl_oy.set(oy)
        self.pua_sl_w.set(w)
        self.pua_sl_h.set(h)
        
        self.lbl_pua_ox.config(text=f"{ox:+d} px")
        self.lbl_pua_oy.config(text=f"{oy:+d} px")
        self.lbl_pua_w.config(text=f"{w} px")
        self.lbl_pua_h.config(text=f"{h} px")
        
        self.update_pua_displays()
        
    def on_pua_slider_change(self, *args):
        ox = self.pua_sl_ox.get()
        oy = self.pua_sl_oy.get()
        w = self.pua_sl_w.get()
        h = self.pua_sl_h.get()
        
        self.lbl_pua_ox.config(text=f"{ox:+d} px")
        self.lbl_pua_oy.config(text=f"{oy:+d} px")
        self.lbl_pua_w.config(text=f"{w} px")
        self.lbl_pua_h.config(text=f"{h} px")
        
        part = self.current_layer_part
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
        self.update_pua_sentence()
        
    def update_pua_displays(self):
        part = self.current_layer_part
        if part != 'whole':
            c_img = render_tuned_single_glyph(part, self.config_data)
            bounds = {part: (0, 0, c_img.width, c_img.height)}
        elif self.current_cluster in self.config_data.get('clusters', {}) or len(self.current_cluster) <= 4:
            c_img, bounds = compose_pua_cluster_image(self.current_cluster, self.config_data, self.current_layer_part)
        else:
            c_img = render_tuned_single_glyph(self.current_cluster[0], self.config_data)
            bounds = {}
        
        scale = 8
        c_large = c_img.resize((36 * scale, 36 * scale), Image.Resampling.NEAREST)
        draw = ImageDraw.Draw(c_large)
        
        # Bounding grid
        draw.rectangle([0, 0, 36 * scale - 1, 36 * scale - 1], outline=(56, 189, 248), width=2)
        draw.line([0, 6 * scale, 36 * scale, 6 * scale], fill=(239, 68, 68, 140), width=1)
        draw.line([0, 32 * scale, 36 * scale, 32 * scale], fill=(34, 197, 94, 140), width=1)
        
        # Highlight active layer with gold outline!
        part = self.current_layer_part
        if part in bounds:
            bx, by, bw, bh = bounds[part]
            draw.rectangle([bx * scale, by * scale, (bx + bw) * scale, (by + bh) * scale], outline=(234, 179, 8), width=2)
            
        self.tk_pua_zoom = ImageTk.PhotoImage(c_large)
        self.canvas_pua_zoom.delete("all")
        self.canvas_pua_zoom.create_image(16, 16, anchor=tk.NW, image=self.tk_pua_zoom)
        
        part_desc = "รวมทั้งก้อน" if part == 'whole' else f"'{part}'"
        detail = (
            f"คลัสเตอร์ PUA:  '{self.current_cluster}'\n"
            f"ชิ้นส่วนที่เลือก:  {part_desc}\n"
            f"เลื่อน ซ้าย-ขวา (Offset X):  {self.pua_sl_ox.get():+d} px\n"
            f"เลื่อน ขึ้น-ลง (Offset Y):  {self.pua_sl_oy.get():+d} px\n"
            f"ความกว้าง (Width):  {self.pua_sl_w.get()} px\n"
            f"ความสูง (Height):  {self.pua_sl_h.get()} px\n"
        )
        self.lbl_pua_detail.config(text=detail)
        
        self.update_pua_sentence()
        
    def update_pua_sentence(self):
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
        
        custom_txt = getattr(self, 'custom_preview_text', '').strip()
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
            ]
        
        can_w = 950
        can_h = 80
        img = Image.new('RGBA', (can_w, can_h), (18, 22, 34, 255))
        draw = ImageDraw.Draw(img)
        
        xc = 20
        yc = 16
        for name, cells in menus_cells:
            btn_w = len(cells) * 36 + 20
            draw.rectangle([xc, yc, xc + btn_w, yc + 46], fill=(22, 35, 60), outline=(218, 165, 32), width=2)
            draw.line([xc + 4, yc + 8, xc + btn_w - 4, yc + 8], fill=(220, 50, 50, 100), width=1)
            draw.line([xc + 4, yc + 39, xc + btn_w - 4, yc + 39], fill=(50, 120, 220, 100), width=1)
            
            x_char = xc + 10
            for cell in cells:
                draw.rectangle([x_char, yc + 5, x_char + 35, yc + 40], outline=(60, 80, 120, 80), width=1)
                img.paste(cell, (x_char, yc + 5), cell)
                x_char += 36
                
            xc += btn_w + 15
            
        self.tk_pua_sentence = ImageTk.PhotoImage(img)
        self.canvas_pua_sentence.delete("all")
        self.canvas_pua_sentence.create_image(10, 5, anchor=tk.NW, image=self.tk_pua_sentence)
        
    def apply_auto_tight_spacing(self):
        # Optimal optical alignment & natural proportional widths (Uniform 19px body baseline)
        # Option A (30px Tight + Extra-Elevated Marks matching actual_option_a_elevated.png)
        tight_presets = {
            'ส': {'offset_x': 0, 'offset_y': 0, 'width': 30, 'height': 19},
            'ง': {'offset_x': 0, 'offset_y': 0, 'width': 30, 'height': 19},
            'ซ': {'offset_x': 0, 'offset_y': 0, 'width': 30, 'height': 19},
            'ฟ': {'offset_x': 0, 'offset_y': 0, 'width': 30, 'height': 25},
            'ล': {'offset_x': 0, 'offset_y': 0, 'width': 30, 'height': 19},
            'บ': {'offset_x': 0, 'offset_y': 0, 'width': 30, 'height': 19},
            'ม': {'offset_x': 0, 'offset_y': 0, 'width': 30, 'height': 19},
            'น': {'offset_x': 0, 'offset_y': 0, 'width': 30, 'height': 19},
            'ต': {'offset_x': 0, 'offset_y': 0, 'width': 30, 'height': 19},
            'อ': {'offset_x': 0, 'offset_y': 0, 'width': 30, 'height': 19},
            'ช': {'offset_x': 0, 'offset_y': 0, 'width': 30, 'height': 19},
            'ค': {'offset_x': 0, 'offset_y': 0, 'width': 31, 'height': 19},
            'ห': {'offset_x': 0, 'offset_y': 0, 'width': 31, 'height': 19},
            'ก': {'offset_x': 0, 'offset_y': 0, 'width': 31, 'height': 19},
            'ว': {'offset_x': 0, 'offset_y': 0, 'width': 28, 'height': 19},
            'ร': {'offset_x': 0, 'offset_y': 0, 'width': 28, 'height': 19},
            'เ': {'offset_x': 18, 'offset_y': 1, 'width': 12, 'height': 19},
            'แ': {'offset_x': 18, 'offset_y': 1, 'width': 20, 'height': 19},
            'โ': {'offset_x': 18, 'offset_y': 1, 'width': 16, 'height': 26},
            'ใ': {'offset_x': 18, 'offset_y': 1, 'width': 16, 'height': 26},
            'ไ': {'offset_x': 18, 'offset_y': 1, 'width': 16, 'height': 26},
            'า': {'offset_x': -7, 'offset_y': 0, 'width': 22, 'height': 19},
            'ะ': {'offset_x': -7, 'offset_y': 0, 'width': 22, 'height': 19},
            'ร้': {'whole_ox': 0, 'whole_oy': 0, 'layers': {'ร': {'offset_x': 0, 'offset_y': 0, 'width': 28, 'height': 19}, '้': {'offset_x': 4, 'offset_y': -5, 'width': 11, 'height': 11}}},
            'ล่': {'whole_ox': 0, 'whole_oy': 0, 'layers': {'ล': {'offset_x': 0, 'offset_y': 0, 'width': 30, 'height': 19}, '่': {'offset_x': 4, 'offset_y': -4, 'width': 10, 'height': 10}}},
            'ริ่': {'whole_ox': 0, 'whole_oy': 0, 'layers': {'ร': {'offset_x': 0, 'offset_y': 0, 'width': 28, 'height': 19}, 'ิ': {'offset_x': 0, 'offset_y': -6, 'width': 18, 'height': 7}, '่': {'offset_x': 4, 'offset_y': -11, 'width': 9, 'height': 9}}},
            'ชื่': {'whole_ox': 0, 'whole_oy': 0, 'layers': {'ช': {'offset_x': 0, 'offset_y': 0, 'width': 30, 'height': 19}, 'ื': {'offset_x': 0, 'offset_y': -6, 'width': 20, 'height': 7}, '่': {'offset_x': 5, 'offset_y': -11, 'width': 9, 'height': 9}}},
            'ตั้': {'whole_ox': 0, 'whole_oy': 0, 'layers': {'ต': {'offset_x': 0, 'offset_y': 0, 'width': 30, 'height': 19}, 'ั': {'offset_x': 0, 'offset_y': -5, 'width': 18, 'height': 7}, '้': {'offset_x': 5, 'offset_y': -11, 'width': 10, 'height': 10}}},
            'กิ่': {'whole_ox': 0, 'whole_oy': 0, 'layers': {'ก': {'offset_x': 0, 'offset_y': 0, 'width': 31, 'height': 19}, 'ิ': {'offset_x': 0, 'offset_y': -6, 'width': 18, 'height': 7}, '่': {'offset_x': 5, 'offset_y': -11, 'width': 9, 'height': 9}}},
            'กิ้': {'whole_ox': 0, 'whole_oy': 0, 'layers': {'ก': {'offset_x': 0, 'offset_y': 0, 'width': 31, 'height': 19}, 'ิ': {'offset_x': 0, 'offset_y': -6, 'width': 18, 'height': 7}, '้': {'offset_x': 5, 'offset_y': -11, 'width': 10, 'height': 10}}},
        }
        for k, v in tight_presets.items():
            if 'whole_ox' in v or 'layers' in v:
                self.config_data.setdefault('clusters', {})[k] = v
            else:
                self.config_data.setdefault('glyphs', {})[k] = v
        save_config(self.config_data)
        self.select_pua_cluster(self.current_cluster)
        self.update_pua_displays()
        self.update_pua_sentence()
        messagebox.showinfo("จัดตัวชิดเรียบร้อย", "นำเข้าการตั้งค่า 'ตัวชิดสวยงาม' เรียบร้อยแล้ว!\nช่องว่างระหว่างตัวอักษรลดลงเหลือเพียง 2-4px แนบชิดสนิท สวยงามระดับฟอนต์ภาษาอังกฤษ")
        
    def save_pua_config(self):
        # Clean up any single-character or full word keys mistakenly saved under clusters
        if 'clusters' in self.config_data:
            to_del = [k for k in list(self.config_data['clusters'].keys()) if len(k) <= 1 or any(c in 'เแโใไ' for c in k)]
            for k in to_del:
                del self.config_data['clusters'][k]
        save_config(self.config_data)
        messagebox.showinfo("บันทึกสำเร็จ", f"บันทึกค่าการปรับแต่งคลัสเตอร์ PUA '{self.current_cluster}' เรียบร้อยแล้ว!\n\nไฟล์: {CONFIG_JSON}\n\nคุณสามารถกดปุ่ม 'ติดตั้งเข้า Mod เกมจริง' เพื่อนำไปใช้ในเกมได้ทันทีครับ!")
        
    def reset_current_layer(self):
        part = self.current_layer_part
        c_info = self.config_data['clusters'][self.current_cluster]
        if part == 'whole':
            c_info['whole_ox'] = 0
            c_info['whole_oy'] = 0
        else:
            nw, nh = get_natural_glyph_metrics(part)
            c_info['layers'][part] = {
                'offset_x': 0, 'offset_y': 0,
                'width': nw, 'height': nh
            }
        self.select_pua_layer_part(part)
        save_config(self.config_data)
        
    def deploy_to_mod(self):
        save_config(self.config_data)
        try:
            cmd = f'python "{DEPLOY_SCRIPT}"'
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if res.returncode == 0:
                messagebox.showinfo("ติดตั้งสำเร็จ", "ฉีดค่าฟอนต์ PUA ที่ปรับแต่งใหม่เข้า RomFS ทั้งหมดเรียบร้อยแล้ว!\n- Ryujinx Mod\n- Yuzu Mod\n- Atmosphere Mod\n\nสามารถเปิดเกมดูผลลัพธ์ในเกมได้ทันทีครับ!")
            else:
                messagebox.showerror("เกิดข้อผิดพลาด", f"ไม่สามารถติดตั้งได้:\n{res.stderr}")
        except Exception as e:
            messagebox.showerror("เกิดข้อผิดพลาด", str(e))

    def deploy_exefs_patch(self):
        try:
            exefs_script = os.path.join(TOOLS_DIR, "deploy_proportional_exefs_patch.py")
            cmd = f'python "{exefs_script}"'
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if res.returncode == 0:
                messagebox.showinfo("ติดตั้ง ExeFS สำเร็จ", "สร้างและติดตั้ง ExeFS Proportional Kerning Patch เรียบร้อย 100%!\n\n- ตัวอักษรจะขยับเข้ามาชิดกันอัตโนมัติตามเอนจิ้นเกม (เหมือนบน PC)\n- ติดตั้งลง Atmosphere, Yuzu, Ryujinx ครบถ้วน\n- ภาษาญี่ปุ่นและคีย์บอร์ดอังกฤษไม่ได้รับผลกระทบใดๆ")
            else:
                messagebox.showerror("เกิดข้อผิดพลาด", f"ไม่สามารถติดตั้ง ExeFS ได้:\n{res.stderr}")
        except Exception as e:
            messagebox.showerror("เกิดข้อผิดพลาด", str(e))

    def browse_custom_font(self):
        file_path = filedialog.askopenfilename(
            title="เลือกไฟล์ฟอนต์ภาษาไทย (.ttf หรือ .otf)",
            filetypes=[("TrueType/OpenType Fonts", "*.ttf *.otf"), ("All Files", "*.*")],
            initialdir=r"C:\Windows\Fonts"
        )
        if file_path and os.path.exists(file_path):
            global FONT_TTF, f32, f_mark
            FONT_TTF = file_path
            f32 = ImageFont.truetype(FONT_TTF, 32)
            f_mark = ImageFont.truetype(FONT_TTF, 28)
            self.lbl_current_font.config(text=os.path.basename(file_path))
            self.select_pua_cluster(self.current_cluster)
            self.update_pua_displays()
            self.update_pua_sentence()
            messagebox.showinfo("เปลี่ยนฟอนต์สำเร็จ", f"โหลดฟอนต์ใหม่เรียบร้อยแล้ว:\n{os.path.basename(file_path)}\n\nระบบคำนวณขนาดและเรนเดอร์พรีวิวใหม่ให้ทันที!")

    # ================= TAB 2: SINGLE GLYPH TUNER =================
    def setup_tab_single_tuner(self):
        top_bar = tk.Frame(self.tab_tuner, bg="#1f2636", relief=tk.RAISED, bd=1)
        top_bar.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        tk.Label(top_bar, text="เลือกตัวอักษรเดี่ยว:", bg="#1f2636", fg="#93c5fd", font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT, padx=8, pady=6)
        for qch in QUICK_CHARS:
            b = tk.Button(top_bar, text=qch, font=('Segoe UI', 10, 'bold'), width=2, bg="#2c364d", fg="#ffffff",
                          relief=tk.FLAT, cursor="hand2", command=lambda c=qch: self.select_single_char(c))
            b.pack(side=tk.LEFT, padx=2, pady=4)
            
        self.combo_single = ttk.Combobox(top_bar, values=ALL_THAI_CHARS, width=4, font=('Segoe UI', 11), state="readonly")
        self.combo_single.set('ก')
        self.combo_single.pack(side=tk.LEFT, padx=6)
        self.combo_single.bind("<<ComboboxSelected>>", lambda e: self.select_single_char(self.combo_single.get()))
        
        work = tk.Frame(self.tab_tuner, bg="#161a24")
        work.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        left_ctrl = tk.LabelFrame(work, text=" แผงปรับตำแหน่ง/ขนาดตัวเดี่ยว ", bg="#1f2636", fg="#f0c050", font=('Segoe UI', 11, 'bold'), bd=1)
        left_ctrl.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10), pady=5, ipadx=10, ipady=5)
        
        self.lbl_selected_single = tk.Label(left_ctrl, text="ตัวอักษร:  [ ก ]", bg="#121622", fg="#fde047", font=('Segoe UI', 14, 'bold'), relief=tk.RIDGE, bd=2)
        self.lbl_selected_single.pack(fill=tk.X, padx=10, pady=10, ipady=4)
        
        # Offsets
        p_grp = tk.LabelFrame(left_ctrl, text=" ขยับตำแหน่ง ", bg="#1f2636", fg="#38bdf8", font=('Segoe UI', 10, 'bold'), bd=1)
        p_grp.pack(fill=tk.X, padx=10, pady=6)
        
        tk.Label(p_grp, text="↔ ขยับ ซ้าย - ขวา (Offset X):", bg="#1f2636", fg="#cbd5e1", font=('Segoe UI', 9)).pack(anchor=tk.W, padx=10, pady=(6, 0))
        fx = tk.Frame(p_grp, bg="#1f2636")
        fx.pack(fill=tk.X, padx=10, pady=2)
        self.sl_s_ox = tk.Scale(fx, from_=-18, to=18, orient=tk.HORIZONTAL, bg="#1f2636", fg="#ffffff", highlightthickness=0, length=180, command=self.on_single_param_change)
        self.sl_s_ox.pack(side=tk.LEFT)
        self.lbl_s_ox = tk.Label(fx, text="0 px", bg="#1f2636", fg="#38bdf8", font=('Segoe UI', 9, 'bold'), width=5)
        self.lbl_s_ox.pack(side=tk.LEFT, padx=5)
        
        tk.Label(p_grp, text="↕ ขยับ ขึ้น - ลง (Offset Y):", bg="#1f2636", fg="#cbd5e1", font=('Segoe UI', 9)).pack(anchor=tk.W, padx=10, pady=(4, 0))
        fy = tk.Frame(p_grp, bg="#1f2636")
        fy.pack(fill=tk.X, padx=10, pady=2)
        self.sl_s_oy = tk.Scale(fy, from_=-18, to=18, orient=tk.HORIZONTAL, bg="#1f2636", fg="#ffffff", highlightthickness=0, length=180, command=self.on_single_param_change)
        self.sl_s_oy.pack(side=tk.LEFT)
        self.lbl_s_oy = tk.Label(fy, text="0 px", bg="#1f2636", fg="#38bdf8", font=('Segoe UI', 9, 'bold'), width=5)
        self.lbl_s_oy.pack(side=tk.LEFT, padx=5)
        
        # Size
        s_grp = tk.LabelFrame(left_ctrl, text=" ขนาดและความอ้วน ", bg="#1f2636", fg="#4ade80", font=('Segoe UI', 10, 'bold'), bd=1)
        s_grp.pack(fill=tk.X, padx=10, pady=6)
        
        tk.Label(s_grp, text="↔ ความกว้าง / ความอ้วน (Width):", bg="#1f2636", fg="#cbd5e1", font=('Segoe UI', 9)).pack(anchor=tk.W, padx=10, pady=(6, 0))
        fw = tk.Frame(s_grp, bg="#1f2636")
        fw.pack(fill=tk.X, padx=10, pady=2)
        self.sl_s_w = tk.Scale(fw, from_=4, to=36, orient=tk.HORIZONTAL, bg="#1f2636", fg="#ffffff", highlightthickness=0, length=180, command=self.on_single_param_change)
        self.sl_s_w.pack(side=tk.LEFT)
        self.lbl_s_w = tk.Label(fw, text="18 px", bg="#1f2636", fg="#4ade80", font=('Segoe UI', 9, 'bold'), width=5)
        self.lbl_s_w.pack(side=tk.LEFT, padx=5)
        
        tk.Label(s_grp, text="↕ ความสูง (Height):", bg="#1f2636", fg="#cbd5e1", font=('Segoe UI', 9)).pack(anchor=tk.W, padx=10, pady=(4, 0))
        fh = tk.Frame(s_grp, bg="#1f2636")
        fh.pack(fill=tk.X, padx=10, pady=2)
        self.sl_s_h = tk.Scale(fh, from_=4, to=36, orient=tk.HORIZONTAL, bg="#1f2636", fg="#ffffff", highlightthickness=0, length=180, command=self.on_single_param_change)
        self.sl_s_h.pack(side=tk.LEFT)
        self.lbl_s_h = tk.Label(fh, text="18 px", bg="#1f2636", fg="#4ade80", font=('Segoe UI', 9, 'bold'), width=5)
        self.lbl_s_h.pack(side=tk.LEFT, padx=5)
        
        act = tk.Frame(left_ctrl, bg="#1f2636")
        act.pack(fill=tk.X, padx=10, pady=(15, 5))
        tk.Button(act, text="💾 บันทึกตัวนี้ (Save)", bg="#10b981", fg="#ffffff", font=('Segoe UI', 10, 'bold'), relief=tk.FLAT,
                  command=lambda: save_config(self.config_data) or messagebox.showinfo("บันทึก", "บันทึกเรียบร้อย"), pady=5).pack(fill=tk.X, pady=3)
        tk.Button(act, text="🌿 คืนค่าธรรมชาติของฟอนต์", bg="#374151", fg="#d1d5db", font=('Segoe UI', 9), relief=tk.FLAT,
                  command=self.reset_single_char_natural).pack(fill=tk.X, pady=2)
                  
        right_s = tk.Frame(work, bg="#161a24")
        right_s.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        zoom_s = tk.LabelFrame(right_s, text=" ซูม 8x ตัวอักษรเดี่ยว ", bg="#1f2636", fg="#f0c050", font=('Segoe UI', 11, 'bold'), bd=1)
        zoom_s.pack(fill=tk.BOTH, expand=True)
        self.canvas_single_zoom = tk.Canvas(zoom_s, bg="#0d1117", highlightthickness=0, width=288, height=288)
        self.canvas_single_zoom.pack(side=tk.LEFT, padx=15, pady=10)
        
        self.cur_single_char = 'ก'
        self.load_single_char_sliders('ก')
        
    def select_single_char(self, ch):
        self.cur_single_char = ch
        self.combo_single.set(ch)
        self.lbl_selected_single.config(text=f"ตัวอักษร:  [ {ch} ]")
        self.load_single_char_sliders(ch)
        
    def load_single_char_sliders(self, ch):
        g = self.config_data.get('glyphs', {}).get(ch, {})
        ox = g.get('offset_x', 0)
        oy = g.get('offset_y', 0)
        nw, nh = get_natural_glyph_metrics(ch)
        w = g.get('width', nw)
        h = g.get('height', nh)
        
        self.sl_s_ox.set(ox)
        self.sl_s_oy.set(oy)
        self.sl_s_w.set(w)
        self.sl_s_h.set(h)
        
        self.lbl_s_ox.config(text=f"{ox:+d} px")
        self.lbl_s_oy.config(text=f"{oy:+d} px")
        self.lbl_s_w.config(text=f"{w} px")
        self.lbl_s_h.config(text=f"{h} px")
        
        self.update_single_display()
        
    def on_single_param_change(self, *args):
        ox = self.sl_s_ox.get()
        oy = self.sl_s_oy.get()
        w = self.sl_s_w.get()
        h = self.sl_s_h.get()
        
        self.lbl_s_ox.config(text=f"{ox:+d} px")
        self.lbl_s_oy.config(text=f"{oy:+d} px")
        self.lbl_s_w.config(text=f"{w} px")
        self.lbl_s_h.config(text=f"{h} px")
        
        ch = self.cur_single_char
        nw, nh = get_natural_glyph_metrics(ch)
        self.config_data['glyphs'][ch] = {
            'offset_x': ox, 'offset_y': oy,
            'width': w, 'height': h,
            'natural_w': nw, 'natural_h': nh
        }
        self.update_single_display()
        
    def update_single_display(self):
        c_img = render_tuned_single_glyph(self.cur_single_char, self.config_data)
        scale = 8
        c_large = c_img.resize((36 * scale, 36 * scale), Image.Resampling.NEAREST)
        draw = ImageDraw.Draw(c_large)
        draw.rectangle([0, 0, 36 * scale - 1, 36 * scale - 1], outline=(56, 189, 248), width=2)
        draw.line([0, 6 * scale, 36 * scale, 6 * scale], fill=(239, 68, 68, 140), width=1)
        draw.line([0, 32 * scale, 36 * scale, 32 * scale], fill=(34, 197, 94, 140), width=1)
        
        self.tk_s_zoom = ImageTk.PhotoImage(c_large)
        self.canvas_single_zoom.delete("all")
        self.canvas_single_zoom.create_image(16, 16, anchor=tk.NW, image=self.tk_s_zoom)
        
    def reset_single_char_natural(self):
        ch = self.cur_single_char
        nw, nh = get_natural_glyph_metrics(ch)
        self.config_data['glyphs'][ch] = {
            'offset_x': 0, 'offset_y': 0,
            'width': nw, 'height': nh,
            'natural_w': nw, 'natural_h': nh
        }
        self.load_single_char_sliders(ch)
        save_config(self.config_data)

    # ================= TAB 3: WORD TESTER =================
    def setup_tab_test(self):
        ctrl = tk.Frame(self.tab_test, bg="#1f2636", relief=tk.RAISED, bd=1)
        ctrl.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        r1 = tk.Frame(ctrl, bg="#1f2636")
        r1.pack(fill=tk.X, padx=10, pady=8)
        
        tk.Label(r1, text="พิมพ์คำทดสอบ:", bg="#1f2636", fg="#f0c050", font=('Segoe UI', 11, 'bold')).pack(side=tk.LEFT, padx=5)
        self.entry_test = tk.Entry(r1, font=('Segoe UI', 13), width=40, bg="#10141d", fg="#ffffff", insertbackground="#ffffff")
        self.entry_test.insert(0, "เริ่มเล่นสร้างเซฟลบเซฟ")
        self.entry_test.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.entry_test.bind("<KeyRelease>", lambda e: self.update_word_test())
        
        tk.Button(r1, text="พรีวิว (Render)", bg="#2563eb", fg="#ffffff", font=('Segoe UI', 10, 'bold'), relief=tk.FLAT,
                  command=self.update_word_test, padx=12, pady=4, cursor="hand2").pack(side=tk.LEFT, padx=5)
                  
        disp = tk.Frame(self.tab_test, bg="#10141d", relief=tk.SUNKEN, bd=2)
        disp.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.canvas_test = tk.Canvas(disp, bg="#10141d", highlightthickness=0)
        self.canvas_test.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.update_word_test()
        
    def update_word_test(self):
        text = self.entry_test.get().strip()
        if not text: text = "เริ่มเล่น   สร้างเซฟ   ลบเซฟ"
        lines = text.split('\n')
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
        self.canvas_test.create_image(10, 10, anchor=tk.NW, image=self.tk_test_img)

    # ================= TAB 4: CHARACTER ATLAS =================
    def setup_tab_atlas(self):
        f = tk.Frame(self.tab_atlas, bg="#161a24")
        f.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(f, text="ตารางอักขระครบทุกตัว (คลิกที่ตัวใดเพื่อนำไปปรับแต่งในแท็บ 2):", bg="#161a24", fg="#f0c050", font=('Segoe UI', 11, 'bold')).pack(anchor=tk.W, pady=(0, 8))
        
        canvas_f = tk.Frame(f, bg="#10141d", relief=tk.SUNKEN, bd=2)
        canvas_f.pack(fill=tk.BOTH, expand=True)
        
        c = tk.Canvas(canvas_f, bg="#10141d", highlightthickness=0)
        vbar = tk.Scrollbar(canvas_f, orient=tk.VERTICAL, command=c.yview)
        c.configure(yscrollcommand=vbar.set)
        vbar.pack(side=tk.RIGHT, fill=tk.Y)
        c.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        inner = tk.Frame(c, bg="#10141d")
        c.create_window((0, 0), window=inner, anchor=tk.NW)
        
        groups = [
            ("1. คลัสเตอร์ PUA ซ้อนชั้น (สูตร 949 ตัว):", ["ริ่", "ร้", "ล่", "ชื่", "ตั้", "กิ่", "กิ้"]),
            ("2. พยัญชนะไทย 44 ตัว (ก - ฮ):", list("กขฃคฅฆงจฉชซฌญฎฏฐฑฒณดตถทธนบปผฝพฟภมยรลวศษสหฬอฮ")),
            ("3. สระแนวบรรทัด:", list("ะาำเแโใไฤฦๅ")),
            ("4. สระบน และ สระล่าง (เดี่ยว):", ["ิ", "ี", "ึ", "ื", "ุ", "ู", "ั", "็"]),
            ("5. วรรณยุกต์ และ เครื่องหมาย (เดี่ยว):", ["่", "้", "๊", "๋", "์", "ๆ", "ฯ"])
        ]
        
        self.atlas_icons = {}
        row_y = 0
        for g_title, chars in groups:
            tk.Label(inner, text=g_title, bg="#10141d", fg="#60a5fa", font=('Segoe UI', 10, 'bold')).grid(row=row_y, column=0, columnspan=16, sticky=tk.W, padx=10, pady=(12, 4))
            row_y += 1
            col_x = 0
            for item in chars:
                if len(item) > 1:
                    cell_img, _ = compose_pua_cluster_image(item, self.config_data)
                else:
                    cell_img = render_tuned_single_glyph(item, self.config_data)
                    
                photo = ImageTk.PhotoImage(cell_img)
                self.atlas_icons[item] = photo
                
                b = tk.Button(inner, image=photo, bg="#1e2638", activebackground="#2563eb", relief=tk.FLAT, bd=1,
                              command=lambda it=item: self.jump_to_edit(it), cursor="hand2")
                b.grid(row=row_y, column=col_x, padx=2, pady=2)
                col_x += 1
                if col_x >= 15:
                    col_x = 0
                    row_y += 1
            row_y += 1
            
        inner.update_idletasks()
        c.configure(scrollregion=c.bbox("all"))
        
    def jump_to_edit(self, item):
        if len(item) > 1:
            self.notebook.select(self.tab_pua)
            self.select_pua_cluster(item)
        else:
            self.notebook.select(self.tab_tuner)
            self.select_single_char(item)

if __name__ == "__main__":
    app = ThaiFontMasterStudio()
    app.mainloop()
