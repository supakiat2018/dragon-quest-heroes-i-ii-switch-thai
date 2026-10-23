"""
DQH2_Thai_Font_Studio.py
โปรแกรมสตูดิโอปรับแต่งฟอนต์ภาษาไทยสำหรับ Dragon Quest Heroes II (Nintendo Switch)
เวอร์ชันอัปเกรด:
1. เพิ่มสไลเดอร์ "ยืดความสูงอิสระ (Height Scale Y %)" 70% - 180% ดึงตัวอักษรให้สูงเท่าตัว A หรือคันจิเดิมได้ 100%
2. เพิ่มสไลเดอร์ "ยืดความกว้างอิสระ (Width Scale X %)" 70% - 160%
3. ปรับเลื่อนแกน Y (ขึ้น-ลง) และแกน X (ซ้าย-ขวา) ให้ลงล็อก Baseline และตรงกลางเป๊ะ
4. ปรับความหนาด้านละเท่าๆ กัน (Symmetric Dilation)
5. ซ้อนเงาฟอนต์เดิมจางๆ (Ghost Overlay) ซูมใหญ่ 10x
6. ปุ่ม [💾 บันทึกการตั้งค่า (Save Config)] เพื่อเซฟส่งต่อให้ AI นำไปสร้างฟอนต์จริง
"""

import os
import sys
import json
import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image, ImageFont, ImageDraw, ImageTk

# Paths
BASE_D = r"D:\Game\dragon quest heroes i & ii"
STUDIO_DIR = os.path.join(BASE_D, "DQH2_Original_Font")
CLEAN_DDS = os.path.join(BASE_D, "switch", "workspace", "tex_clean_55", "clean_entry_00055.TEX0.dxt5.dds")
DEFAULT_FONT = os.path.join(BASE_D, "switch", "fonts", "Pridi-Bold.ttf")
CONFIG_JSON = os.path.join(STUDIO_DIR, "dqh2_thai_font_config.json")

os.makedirs(STUDIO_DIR, exist_ok=True)

# Character classification
UPPER_MARKS = set('ิีึืั็ํ')
LOWER_MARKS = set('ฺุู')
TONE_MARKS  = set('่้๊๋์')

# Reference characters from Entry 55
REF_COORDS = {
    'A (Original English)': (1, 44),
    'B (Original English)': (1, 45),
    'W (Original Wide)': (1, 66),
    '0 (Original Number)': (1, 34),
    '1 (Original Number)': (1, 35),
    'あ (Original Hiragana)': (6, 75),
    'ア (Original Katakana)': (7, 45),
    'ド (Original Katakana)': (7, 85),
    'ปิดเงา (No Ghost)': None
}

class DQH2FontStudio(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Dragon Quest Heroes II - Thai Font Studio (V2 Proportional & Height Scaler)")
        self.geometry("1340x880")
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        # State Variables
        self.current_font_path = DEFAULT_FONT if os.path.exists(DEFAULT_FONT) else r"C:\Windows\Fonts\leelawdb.ttf"
        self.current_char = "ก"
        self.preview_word = "เริ่มเล่นสร้างเซฟ"
        
        # Sliders state
        self.font_size = 28
        self.scale_y = 1.25 # Height Scale (125% default so it matches tall original 'A'!)
        self.scale_x = 1.00 # Width Scale (100%)
        self.offset_y = 0   # Nudge Y (-10 to +10)
        self.offset_x = 0   # Nudge X (-10 to +10)
        self.base_y = 28
        self.base_thickness = 1 # Dilation pixels
        self.mark_thickness = 0
        self.ghost_opacity = 0.50
        self.ref_key = 'A (Original English)'
        self.show_grid = True
        self.show_baseline = True

        # Load Atlas for ghost
        self.atlas = None
        if os.path.exists(CLEAN_DDS):
            try:
                self.atlas = Image.open(CLEAN_DDS)
            except:
                pass

        self.load_saved_config()
        self.build_ui()
        self.update_preview()

    def load_saved_config(self):
        if os.path.exists(CONFIG_JSON):
            try:
                with open(CONFIG_JSON, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                if "font_path" in cfg and os.path.exists(cfg["font_path"]):
                    self.current_font_path = cfg["font_path"]
                self.font_size = cfg.get("font_size", self.font_size)
                self.scale_y = cfg.get("scale_y", self.scale_y)
                self.scale_x = cfg.get("scale_x", self.scale_x)
                self.offset_y = cfg.get("offset_y", self.offset_y)
                self.offset_x = cfg.get("offset_x", self.offset_x)
                self.base_y = cfg.get("base_y", self.base_y)
                self.base_thickness = cfg.get("base_thickness", self.base_thickness)
                self.mark_thickness = cfg.get("mark_thickness", self.mark_thickness)
                self.ghost_opacity = cfg.get("ghost_opacity", self.ghost_opacity)
            except:
                pass

    def build_ui(self):
        # Grid layout (Left 460px width for spacious controls, Right expands)
        self.grid_columnconfigure(0, weight=0, minsize=460)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ==============================================================
        # LEFT PANEL: Controls & Settings (Wider so text doesn't cut!)
        # ==============================================================
        left_frame = ctk.CTkScrollableFrame(self, label_text="🎛️ เครื่องมือปรับแต่งฟอนต์ (Font Tuning Controls)", width=450)
        left_frame.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")

        # 1. Section: Font Selector
        sec1 = ctk.CTkFrame(left_frame)
        sec1.pack(fill="x", pady=8, padx=5)

        ctk.CTkLabel(sec1, text="1. เลือกฟอนต์ภาษาไทยภายนอก (.ttf/.otf)", font=("Arial", 14, "bold"), text_color="#FFD700").pack(anchor="w", padx=10, pady=(10, 2))
        self.lbl_font_name = ctk.CTkLabel(sec1, text=f"ฟอนต์ปัจจุบัน: {os.path.basename(self.current_font_path)}", font=("Arial", 12), text_color="#A0AEC0")
        self.lbl_font_name.pack(anchor="w", padx=10, pady=2)

        btn_browse = ctk.CTkButton(sec1, text="📂 เลือกไฟล์ฟอนต์จากเครื่อง...", command=self.browse_font, fg_color="#2B6CB0", hover_color="#2C5282")
        btn_browse.pack(fill="x", padx=10, pady=(5, 10))

        # 2. Section: Height & Width Stretch Scaling (แก้เรื่องปรับความสูงไม่ได้!)
        sec_scale = ctk.CTkFrame(left_frame)
        sec_scale.pack(fill="x", pady=8, padx=5)

        ctk.CTkLabel(sec_scale, text="2. ปรับสเกลความสูงและกว้าง (Stretch Size)", font=("Arial", 14, "bold"), text_color="#63B3ED").pack(anchor="w", padx=10, pady=(10, 5))

        # Height Scale Y (70% - 180%)
        self.lbl_scale_y = ctk.CTkLabel(sec_scale, text=f"ยืดความสูงตัวอักษร (Height Scale Y): {int(self.scale_y * 100)}%", font=("Arial", 12, "bold"), text_color="#F6E05E")
        self.lbl_scale_y.pack(anchor="w", padx=10, pady=(5, 0))
        self.slider_scale_y = ctk.CTkSlider(sec_scale, from_=0.70, to=1.80, number_of_steps=55, command=self.on_scale_y_change)
        self.slider_scale_y.set(self.scale_y)
        self.slider_scale_y.pack(fill="x", padx=10, pady=5)

        # Width Scale X (70% - 160%)
        self.lbl_scale_x = ctk.CTkLabel(sec_scale, text=f"ยืดความกว้างตัวอักษร (Width Scale X): {int(self.scale_x * 100)}%")
        self.lbl_scale_x.pack(anchor="w", padx=10, pady=(5, 0))
        self.slider_scale_x = ctk.CTkSlider(sec_scale, from_=0.70, to=1.60, number_of_steps=45, command=self.on_scale_x_change)
        self.slider_scale_x.set(self.scale_x)
        self.slider_scale_x.pack(fill="x", padx=10, pady=5)

        # Nudge Position (Offset Y and Offset X)
        pos_frame = ctk.CTkFrame(sec_scale, fg_color="transparent")
        pos_frame.pack(fill="x", padx=5, pady=5)
        pos_frame.columnconfigure(0, weight=1)
        pos_frame.columnconfigure(1, weight=1)

        # Offset Y
        self.lbl_offset_y = ctk.CTkLabel(pos_frame, text=f"เลื่อนขึ้น-ลง (Nudge Y): {self.offset_y} px")
        self.lbl_offset_y.grid(row=0, column=0, padx=5, sticky="w")
        self.slider_offset_y = ctk.CTkSlider(pos_frame, from_=-10, to=10, number_of_steps=20, command=self.on_offset_y_change)
        self.slider_offset_y.set(self.offset_y)
        self.slider_offset_y.grid(row=1, column=0, padx=5, pady=2, sticky="ew")

        # Offset X
        self.lbl_offset_x = ctk.CTkLabel(pos_frame, text=f"เลื่อนซ้าย-ขวา (Nudge X): {self.offset_x} px")
        self.lbl_offset_x.grid(row=0, column=1, padx=5, sticky="w")
        self.slider_offset_x = ctk.CTkSlider(pos_frame, from_=-10, to=10, number_of_steps=20, command=self.on_offset_x_change)
        self.slider_offset_x.set(self.offset_x)
        self.slider_offset_x.grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        # Font Size & Baseline
        self.lbl_font_size = ctk.CTkLabel(sec_scale, text=f"ขนาดฟอนต์ต้นฉบับ (Base Size): {self.font_size} pt")
        self.lbl_font_size.pack(anchor="w", padx=10, pady=(8, 0))
        self.slider_font_size = ctk.CTkSlider(sec_scale, from_=20, to=36, number_of_steps=16, command=self.on_font_size_change)
        self.slider_font_size.set(self.font_size)
        self.slider_font_size.pack(fill="x", padx=10, pady=5)

        self.lbl_base_y = ctk.CTkLabel(sec_scale, text=f"ตำแหน่งเส้นบรรทัด (Baseline Y): {self.base_y} px")
        self.lbl_base_y.pack(anchor="w", padx=10, pady=(5, 0))
        self.slider_base_y = ctk.CTkSlider(sec_scale, from_=20, to=34, number_of_steps=14, command=self.on_base_y_change)
        self.slider_base_y.set(self.base_y)
        self.slider_base_y.pack(fill="x", padx=10, pady=(5, 10))

        # 3. Section: Thickness & Symmetric Dilation
        sec2 = ctk.CTkFrame(left_frame)
        sec2.pack(fill="x", pady=8, padx=5)

        ctk.CTkLabel(sec2, text="3. ปรับความหนาเท่ากันทุกด้าน (Symmetric Dilation)", font=("Arial", 14, "bold"), text_color="#FFD700").pack(anchor="w", padx=10, pady=(10, 5))

        # Base Consonant Thickness
        self.lbl_base_thick = ctk.CTkLabel(sec2, text=f"ความหนาพยัญชนะฐาน (Consonant): +{self.base_thickness} px")
        self.lbl_base_thick.pack(anchor="w", padx=10, pady=(5, 0))
        self.slider_base_thick = ctk.CTkSlider(sec2, from_=0, to=5, number_of_steps=5, command=self.on_base_thick_change)
        self.slider_base_thick.set(self.base_thickness)
        self.slider_base_thick.pack(fill="x", padx=10, pady=5)

        # Mark Thickness (Vowels & Tones)
        self.lbl_mark_thick = ctk.CTkLabel(sec2, text=f"ความหนาสระและวรรณยุกต์ (Vowels/Tones): +{self.mark_thickness} px")
        self.lbl_mark_thick.pack(anchor="w", padx=10, pady=(5, 0))
        self.slider_mark_thick = ctk.CTkSlider(sec2, from_=0, to=4, number_of_steps=4, command=self.on_mark_thick_change)
        self.slider_mark_thick.set(self.mark_thickness)
        self.slider_mark_thick.pack(fill="x", padx=10, pady=(5, 10))

        # 4. Section: Ghost Overlay
        sec3 = ctk.CTkFrame(left_frame)
        sec3.pack(fill="x", pady=8, padx=5)

        ctk.CTkLabel(sec3, text="4. เงาฟอนต์เดิมจากในเกม (Ghost Overlay)", font=("Arial", 14, "bold"), text_color="#FFD700").pack(anchor="w", padx=10, pady=(10, 5))

        ctk.CTkLabel(sec3, text="เลือกตัวอักษรเงาต้นฉบับ Entry 55 สำหรับทาบขนาด:").pack(anchor="w", padx=10, pady=(5, 0))
        self.combo_ref = ctk.CTkComboBox(sec3, values=list(REF_COORDS.keys()), command=self.on_ref_change)
        self.combo_ref.set(self.ref_key)
        self.combo_ref.pack(fill="x", padx=10, pady=5)

        self.lbl_opacity = ctk.CTkLabel(sec3, text=f"ความจางของเงาฟอนต์เดิม: {int(self.ghost_opacity * 100)}%")
        self.lbl_opacity.pack(anchor="w", padx=10, pady=(5, 0))
        self.slider_opacity = ctk.CTkSlider(sec3, from_=0.0, to=1.0, number_of_steps=20, command=self.on_opacity_change)
        self.slider_opacity.set(self.ghost_opacity)
        self.slider_opacity.pack(fill="x", padx=10, pady=5)

        check_frame = ctk.CTkFrame(sec3, fg_color="transparent")
        check_frame.pack(fill="x", padx=10, pady=(5, 10))
        self.chk_grid = ctk.CTkCheckBox(check_frame, text="ตาราง 36x36 Pixel", command=self.on_toggle_grid)
        self.chk_grid.select()
        self.chk_grid.pack(side="left", padx=5)
        self.chk_base = ctk.CTkCheckBox(check_frame, text="เส้นแดง Baseline", command=self.on_toggle_baseline)
        self.chk_base.select()
        self.chk_base.pack(side="left", padx=15)

        # 5. Section: Save Button (ปุ่มเซฟค่าเพื่อให้มึงสร้าง)
        sec4 = ctk.CTkFrame(left_frame, fg_color="#1A202C")
        sec4.pack(fill="x", pady=15, padx=5)

        self.btn_save = ctk.CTkButton(
            sec4,
            text="💾 บันทึกการตั้งค่า (Save Settings for AI)",
            font=("Arial", 16, "bold"),
            fg_color="#38A169",
            hover_color="#2F855A",
            height=48,
            command=self.save_config_for_ai
        )
        self.btn_save.pack(fill="x", padx=10, pady=10)

        # ==============================================================
        # RIGHT PANEL: Real-time Canvas & Word Testing
        # ==============================================================
        right_frame = ctk.CTkFrame(self)
        right_frame.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")
        right_frame.grid_columnconfigure(0, weight=1)

        # Big Canvas Zoom (10x zoom = 360x360 px)
        top_bar = ctk.CTkFrame(right_frame, fg_color="transparent")
        top_bar.pack(fill="x", padx=15, pady=(15, 5))
        ctk.CTkLabel(top_bar, text="🔍 จอพรีวิวซูม 10 เท่า (10X Cell Preview 36x36 px)", font=("Arial", 16, "bold"), text_color="#63B3ED").pack(side="left")

        self.canvas_label = tk.Label(right_frame, bg="#111317", bd=2, relief="groove")
        self.canvas_label.pack(pady=10)

        # Quick Char Selector
        quick_frame = ctk.CTkFrame(right_frame)
        quick_frame.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(quick_frame, text="เลือกตัวอักษรทดสอบด่วน:", font=("Arial", 13, "bold")).pack(anchor="w", padx=10, pady=(5, 2))

        btn_row = ctk.CTkFrame(quick_frame, fg_color="transparent")
        btn_row.pack(fill="x", padx=5, pady=(2, 8))
        test_samples = ["ก", "ข", "ง", "จ", "ด", "ต", "น", "บ", "ป", "ม", "ย", "ร", "ล", "ว", "ส", "อ", "เ", "แ", "ิ", "ี", "่", "้", "ุ", "ู", "ผู้", "ที่", "นี้", "ได้", "ไม่"]
        for s in test_samples:
            b = ctk.CTkButton(btn_row, text=s, width=32, height=30, font=("Arial", 13), fg_color="#2D3748", hover_color="#4A5568", command=lambda ch=s: self.select_char(ch))
            b.pack(side="left", padx=2)

        # In-Game Sentence Tester
        test_sec = ctk.CTkFrame(right_frame)
        test_sec.pack(fill="both", expand=True, padx=15, pady=10)

        ctk.CTkLabel(test_sec, text="📝 จำลองประโยคบนหน้าจอเกม (In-Game Dialogue Preview):", font=("Arial", 14, "bold"), text_color="#68D391").pack(anchor="w", padx=10, pady=(10, 5))

        self.entry_test = ctk.CTkEntry(test_sec, placeholder_text="พิมพ์ข้อความทดสอบที่นี่...")
        self.entry_test.insert(0, self.preview_word)
        self.entry_test.pack(fill="x", padx=10, pady=5)
        self.entry_test.bind("<KeyRelease>", self.on_word_change)

        self.lbl_word_preview = tk.Label(test_sec, bg="#1A202C", bd=1, relief="solid")
        self.lbl_word_preview.pack(fill="both", expand=True, padx=10, pady=10)

    # -------------------------------------------------------------
    # Event Handlers
    # -------------------------------------------------------------
    def browse_font(self):
        f = filedialog.askopenfilename(filetypes=[("Font Files", "*.ttf;*.otf")])
        if f:
            self.current_font_path = f
            self.lbl_font_name.configure(text=f"ฟอนต์ปัจจุบัน: {os.path.basename(f)}")
            self.update_preview()

    def on_scale_y_change(self, val):
        self.scale_y = float(val)
        self.lbl_scale_y.configure(text=f"ยืดความสูงตัวอักษร (Height Scale Y): {int(self.scale_y * 100)}%")
        self.update_preview()

    def on_scale_x_change(self, val):
        self.scale_x = float(val)
        self.lbl_scale_x.configure(text=f"ยืดความกว้างตัวอักษร (Width Scale X): {int(self.scale_x * 100)}%")
        self.update_preview()

    def on_offset_y_change(self, val):
        self.offset_y = int(val)
        self.lbl_offset_y.configure(text=f"เลื่อนขึ้น-ลง (Nudge Y): {self.offset_y} px")
        self.update_preview()

    def on_offset_x_change(self, val):
        self.offset_x = int(val)
        self.lbl_offset_x.configure(text=f"เลื่อนซ้าย-ขวา (Nudge X): {self.offset_x} px")
        self.update_preview()

    def on_base_thick_change(self, val):
        self.base_thickness = int(val)
        self.lbl_base_thick.configure(text=f"ความหนาพยัญชนะฐาน (Consonant): +{self.base_thickness} px")
        self.update_preview()

    def on_mark_thick_change(self, val):
        self.mark_thickness = int(val)
        self.lbl_mark_thick.configure(text=f"ความหนาสระและวรรณยุกต์ (Vowels/Tones): +{self.mark_thickness} px")
        self.update_preview()

    def on_font_size_change(self, val):
        self.font_size = int(val)
        self.lbl_font_size.configure(text=f"ขนาดฟอนต์ต้นฉบับ (Base Size): {self.font_size} pt")
        self.update_preview()

    def on_base_y_change(self, val):
        self.base_y = int(val)
        self.lbl_base_y.configure(text=f"ตำแหน่งเส้นบรรทัด (Baseline Y): {self.base_y} px")
        self.update_preview()

    def on_opacity_change(self, val):
        self.ghost_opacity = float(val)
        self.lbl_opacity.configure(text=f"ความจางของเงาฟอนต์เดิม: {int(self.ghost_opacity * 100)}%")
        self.update_preview()

    def on_ref_change(self, choice):
        self.ref_key = choice
        self.update_preview()

    def on_toggle_grid(self):
        self.show_grid = self.chk_grid.get()
        self.update_preview()

    def on_toggle_baseline(self):
        self.show_baseline = self.chk_base.get()
        self.update_preview()

    def select_char(self, ch):
        self.current_char = ch
        self.update_preview()

    def on_word_change(self, event=None):
        self.preview_word = self.entry_test.get()
        self.update_preview()

    # -------------------------------------------------------------
    # Render Engine (Height Scaling + Dilation)
    # -------------------------------------------------------------
    def render_single_cell(self, text):
        try:
            f = ImageFont.truetype(self.current_font_path, self.font_size)
        except:
            f = ImageFont.load_default()

        # 1. วาดลงบน Scratch Canvas ขนาดใหญ่ 120x120
        scratch = Image.new("RGBA", (120, 120), (0, 0, 0, 0))
        d_scratch = ImageDraw.Draw(scratch)
        d_scratch.text((60, 70), text, font=f, fill=(255, 255, 255, 255), anchor="ms")

        alpha_scratch = np.array(scratch)[:, :, 3]
        ys, xs = np.where(alpha_scratch > 10)

        cell = Image.new("RGBA", (36, 36), (0, 0, 0, 0))

        if len(xs) > 0:
            x0, x1 = int(np.min(xs)), int(np.max(xs)) + 1
            y0, y1 = int(np.min(ys)), int(np.max(ys)) + 1
            cropped = scratch.crop((x0, y0, x1, y1))

            # 2. ปรับยืดความสูง (Scale Y) และความกว้าง (Scale X) อิสระ!
            new_w = max(1, int(cropped.width * self.scale_x))
            new_h = max(1, int(cropped.height * self.scale_y))
            resized = cropped.resize((new_w, new_h), Image.Resampling.LANCZOS)

            # วางลงบนช่อง 36x36
            paste_x = 18 + self.offset_x - (new_w // 2)
            paste_y = self.base_y + self.offset_y - new_h
            cell.paste(resized, (paste_x, paste_y), resized)

        # 3. ปรับความหนาเท่ากันทุกทิศทางด้วย Symmetric Dilation
        alpha = np.array(cell)[:, :, 3]
        has_mark = any(c in text for c in UPPER_MARKS | LOWER_MARKS | TONE_MARKS)
        thick = self.mark_thickness if (has_mark and len(text) == 1) else self.base_thickness

        if thick > 0:
            k_size = thick * 2 + 1
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k_size, k_size))
            dilated = cv2.dilate(alpha, kernel, iterations=1)
        else:
            dilated = alpha

        # รวมเป็นภาพ RGBA สีขาว
        out_cell = Image.new("RGBA", (36, 36), (0, 0, 0, 0))
        white_arr = np.zeros((36, 36, 4), dtype=np.uint8)
        white_arr[:, :, 0] = 255
        white_arr[:, :, 1] = 255
        white_arr[:, :, 2] = 255
        white_arr[:, :, 3] = dilated
        out_cell = Image.fromarray(white_arr)

        return out_cell

    def update_preview(self):
        # 1. จอซูม 10 เท่า (360 x 360 px)
        Z = 10
        zoom_w = 36 * Z
        zoom_h = 36 * Z
        view_im = Image.new("RGBA", (zoom_w, zoom_h), (18, 20, 26, 255))

        # A. เงาฟอนต์เดิม (Ghost Overlay)
        if self.atlas and self.ref_key in REF_COORDS and REF_COORDS[self.ref_key] is not None and self.ghost_opacity > 0:
            r, c = REF_COORDS[self.ref_key]
            orig_crop = self.atlas.crop((c * 36, r * 36, c * 36 + 36, r * 36 + 36))
            orig_arr = np.array(orig_crop)
            orig_arr[:, :, 0] = 70  # Cyan
            orig_arr[:, :, 1] = 200
            orig_arr[:, :, 2] = 255
            orig_arr[:, :, 3] = (orig_arr[:, :, 3] * self.ghost_opacity).astype(np.uint8)
            ghost_im = Image.fromarray(orig_arr).resize((zoom_w, zoom_h), Image.NEAREST)
            view_im.paste(ghost_im, (0, 0), ghost_im)

        # B. ตัวอักษรไทยที่ยืดความสูง + ปรับความหนาแล้ว
        thai_cell = self.render_single_cell(self.current_char)
        thai_zoom = thai_cell.resize((zoom_w, zoom_h), Image.NEAREST)
        view_im.paste(thai_zoom, (0, 0), thai_zoom)

        # C. เส้น Baseline และ Grid
        draw = ImageDraw.Draw(view_im)
        if self.show_baseline:
            line_y = (self.base_y + self.offset_y) * Z
            draw.line([(0, line_y), (zoom_w, line_y)], fill=(255, 60, 60, 220), width=2)

        if self.show_grid:
            draw.rectangle([(0, 0), (zoom_w - 1, zoom_h - 1)], outline=(70, 80, 100, 255), width=2)
            draw.line([(18 * Z, 0), (18 * Z, zoom_h)], fill=(45, 55, 75, 150), width=1)

        tk_img = ImageTk.PhotoImage(view_im)
        self.canvas_label.configure(image=tk_img)
        self.canvas_label.image = tk_img

        # 2. จำลองประโยคในเกม
        word = self.preview_word if self.preview_word else " "
        word_len = len(word)
        word_im = Image.new("RGBA", (max(word_len * 36, 200), 72), (24, 28, 36, 255))

        for idx, ch in enumerate(word):
            c_img = self.render_single_cell(ch)
            word_im.paste(c_img, (idx * 36, 18), c_img)

        word_display = word_im.resize((word_im.width * 2, word_im.height * 2), Image.NEAREST)
        tk_word_img = ImageTk.PhotoImage(word_display)
        self.lbl_word_preview.configure(image=tk_word_img)
        self.lbl_word_preview.image = tk_word_img

    # -------------------------------------------------------------
    # Save Config for AI Agent
    # -------------------------------------------------------------
    def save_config_for_ai(self):
        config_data = {
            "font_path": self.current_font_path,
            "font_size": self.font_size,
            "scale_y": round(self.scale_y, 3),
            "scale_x": round(self.scale_x, 3),
            "offset_y": self.offset_y,
            "offset_x": self.offset_x,
            "base_y": self.base_y,
            "base_thickness": self.base_thickness,
            "mark_thickness": self.mark_thickness,
            "ghost_opacity": round(self.ghost_opacity, 2),
            "ref_character": self.ref_key,
            "cell_width": 36,
            "cell_height": 36,
            "status": "READY_FOR_AI_BUILD"
        }

        with open(CONFIG_JSON, "w", encoding="utf-8") as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)

        msg = (
            f"✅ บันทึกค่าคอนฟิกสำเร็จเรียบร้อยแล้ว!\n\n"
            f"ไฟล์: {os.path.basename(CONFIG_JSON)}\n"
            f"- ยืดความสูง (Height Scale Y): {int(self.scale_y * 100)}%\n"
            f"- ยืดความกว้าง (Width Scale X): {int(self.scale_x * 100)}%\n"
            f"- เลื่อนตำแหน่ง (Y/X): {self.offset_y} px / {self.offset_x} px\n"
            f"- ความหนาพยัญชนะ: +{self.base_thickness} px\n"
            f"- ความหนาสระ/วรรณยุกต์: +{self.mark_thickness} px\n\n"
            f"พร้อมส่งต่อให้ AI นำค่าเหล่านี้ไปสร้างฟอนต์ Entry 55 และฉีดเข้าตัวเกมได้ทันทีครับ!"
        )
        messagebox.showinfo("บันทึกสำเร็จ", msg)

if __name__ == "__main__":
    app = DQH2FontStudio()
    app.mainloop()
