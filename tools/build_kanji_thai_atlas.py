"""
build_kanji_thai_atlas.py
คอมไพล์ฟอนต์ภาษาไทยฉบับสมบูรณ์แบบสำหรับ Nintendo Switch
- เรนเดอร์ 83 พยัญชนะเดี่ยวและสระแนวบรรทัดลงในช่อง Kana (Optical Alignment: สระหนาชิดขวา สระหลังชิดซ้าย พยัญชนะกึ่งกลาง)
- เรนเดอร์ 2,208 พยางค์ PUA คลัสเตอร์ ลงในช่องคันจิแท้ (เริ่ม Ku 24 Ten 01)
- มาตรฐาน Option A แท้:
  * 3 ระดับ (พยัญชนะ + สระบน + วรรณยุกต์): สระบน Y=6, วรรณยุกต์ Y=0
  * 2 ระดับ (พยัญชนะ + สระบน/วรรณยุกต์): ยกสูง Y=2..4
  * ความกว้างคลัสเตอร์ 28-29px แนบชิดสวยงามแบบฟอนต์อังกฤษ ไร้รอยแหว่ง
- แพ็ก Entry 55 และฉีดเข้า LINKDATA.BIN ทั้ง Atmosphere และ Yuzu
"""

import os
import sys
import json
import time
import shutil
import struct
import subprocess
import numpy as np
from PIL import Image, ImageFont, ImageDraw

SWITCH_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(SWITCH_DIR)

WORKSPACE_DIR = os.path.join(SWITCH_DIR, "workspace")
TEX_DIR = os.path.join(WORKSPACE_DIR, "tex_55")
OUT_G1T_DIR = os.path.join(WORKSPACE_DIR, "out_g1t")
FONT_TTF = os.path.join(SWITCH_DIR, "fonts", "Pridi-Bold.ttf")
G1T_TOOL = os.path.join(SWITCH_DIR, "tools", "g1t_tool.py")

CLEAN_DDS = os.path.join(WORKSPACE_DIR, "tex_clean_55", "clean_entry_00055.TEX0.dxt5.dds")
TARGET_DDS = os.path.join(TEX_DIR, "entry_00055.TEX0.dxt5.dds")
META_PATH = os.path.join(WORKSPACE_DIR, "kanji_cluster_slots.json")

TITLE_ID = "0100CD3000BDC000"
MOD_DIR = os.path.join(BASE_DIR, "mod", "atmosphere", "contents", TITLE_ID, "romfs", "dqh2")
MOD_BIN = os.path.join(MOD_DIR, "LINKDATA.BIN")
YUZU_DIR = os.path.expanduser(r"~\AppData\Roaming\yuzu\load\0100CD3000BDC000\MODTHAI\romfs\dqh2")
YUZU_BIN = os.path.join(YUZU_DIR, "LINKDATA.BIN")

sys.path.append(os.path.join(SWITCH_DIR, "tools"))
from build_thai_keyboard import KEYBOARD_MAPPING, encode_cell_dxt5, pack_entry_chunks

ENTRY_55_OFF = 4805120
ENTRY_55_ZSZ = 1106944
WIDTH_BLOCKS = 4096 // 4  # 1024
BLOCK_BYTES = 16

f_base = ImageFont.truetype(FONT_TTF, 30)
f_vowel = ImageFont.truetype(FONT_TTF, 24)
f_tone = ImageFont.truetype(FONT_TTF, 22)
f_mark = ImageFont.truetype(FONT_TTF, 26)
f_single = ImageFont.truetype(FONT_TTF, 27)

TONE_MARKS = set(['่', '้', '๊', '๋', '์'])
UPPER_MARKS = set(['ิ', 'ี', 'ึ', 'ื', 'ั', '็', 'ํ'])
LOWER_MARKS = set(['ุ', 'ู', 'ฺ'])

def get_glyph_crop(ch, font):
    t = Image.new('RGBA', (80, 80), (0, 0, 0, 0))
    ImageDraw.Draw(t).text((40, 50), ch, font=font, fill=(255, 255, 255, 255), anchor='ms')
    arr = np.array(t)[:, :, 3]
    coords = np.argwhere(arr > 20)
    if len(coords) == 0:
        return None
    return t.crop((coords[:, 1].min(), coords[:, 0].min(), coords[:, 1].max() + 1, coords[:, 0].max() + 1))

def render_smart_cluster_opt_a(text, target_w=29):
    if len(text) == 1:
        crop_b = get_glyph_crop(text, f_single)
        if not crop_b:
            return Image.new('RGBA', (36, 36), (0, 0, 0, 0))
        w = int(round(crop_b.width * 1.15))
        h = crop_b.height
        scaled = crop_b.resize((w, h), Image.Resampling.LANCZOS)
        cell = Image.new('RGBA', (36, 36), (0, 0, 0, 0))
        if text in ['เ', 'แ', 'โ', 'ใ', 'ไ']:
            cx = 36 - w - 2
        elif text in ['ะ', 'า', 'ำ']:
            cx = 2
        else:
            cx = (36 - w) // 2
        cy = 31 - h
        cell.paste(scaled, (cx, cy), scaled)
        return cell

    base = text[0]
    upper = None
    lower = None
    tone = None
    for c in text[1:]:
        if c in UPPER_MARKS:
            upper = c
        elif c in LOWER_MARKS:
            lower = c
        elif c in TONE_MARKS:
            tone = c

    can = Image.new('RGBA', (80, 80), (0, 0, 0, 0))
    crop_b = get_glyph_crop(base, f_base)
    if not crop_b:
        return Image.new('RGBA', (36, 36), (0, 0, 0, 0))

    x_b = 40 - crop_b.width // 2
    y_b = 33 - crop_b.height
    can.paste(crop_b, (x_b, y_b), crop_b)

    if upper and tone:
        crop_v = get_glyph_crop(upper, f_vowel)
        crop_t = get_glyph_crop(tone, f_tone)
        if crop_v:
            can.paste(crop_v, (x_b + (crop_b.width - crop_v.width) // 2, 6), crop_v)
        if crop_t:
            can.paste(crop_t, (x_b + crop_b.width - crop_t.width - 2, 0), crop_t)
    elif upper:
        crop_v = get_glyph_crop(upper, f_mark)
        if crop_v:
            can.paste(crop_v, (x_b + (crop_b.width - crop_v.width) // 2, 4), crop_v)
    elif tone:
        crop_t = get_glyph_crop(tone, f_mark)
        if crop_t:
            can.paste(crop_t, (x_b + crop_b.width - crop_t.width - 2, 2), crop_t)

    if lower:
        crop_l = get_glyph_crop(lower, f_vowel)
        if crop_l:
            can.paste(crop_l, (x_b + (crop_b.width - crop_l.width) // 2, 24), crop_l)

    coords = np.argwhere(np.array(can)[:, :, 3] > 20)
    cropped = can.crop((coords[:, 1].min(), coords[:, 0].min(), coords[:, 1].max() + 1, coords[:, 0].max() + 1))
    scaled = cropped.resize((target_w, cropped.height), Image.Resampling.LANCZOS)
    cell = Image.new('RGBA', (36, 36), (0, 0, 0, 0))
    cx = (36 - target_w) // 2
    cy = coords[:, 0].min()
    cell.paste(scaled, (cx, cy), scaled)
    return cell

def main():
    start_time = time.time()
    print("=" * 70)
    print(" [1/4] เตรียมแผ่นภาพต้นฉบับสะอาดจาก tex_clean_55...")
    print("=" * 70)
    shutil.copy2(CLEAN_DDS, TARGET_DDS)
    with open(TARGET_DDS, "rb") as f:
        dds_bytes = bytearray(f.read())
    print(f"[+] โหลด DDS สำเร็จ: {len(dds_bytes):,} bytes")

    # 2. วาด 83 พยัญชนะเดี่ยวลงช่องคานะ
    print("\n" + "=" * 70)
    print(" [2/4] วาด 83 พยัญชนะเดี่ยวและสระแนวบรรทัดลงในช่อง Kana...")
    print("=" * 70)
    for kana, (row, col), thai_ch in KEYBOARD_MAPPING:
        cell_img = render_smart_cluster_opt_a(thai_ch)
        rows_dxt = encode_cell_dxt5(cell_img)
        bx0 = (col * 36) // 4
        by0 = (row * 36) // 4
        for by in range(9):
            offset = 128 + ((by0 + by) * WIDTH_BLOCKS + bx0) * BLOCK_BYTES
            dds_bytes[offset : offset + 144] = rows_dxt[by]
    print("[+] วาดพยัญชนะเดี่ยวและสระแนวบรรทัด 83 ตัวเรียบร้อย!")

    # 3. วาด 2,208 พยางค์คลัสเตอร์ลงช่องคันจิแท้ (Option A แท้)
    print("\n" + "=" * 70)
    print(" [3/4] วาด 2,208 พยางค์คลัสเตอร์ลงในช่องคันจิแท้ (Option A แท้)...")
    print("=" * 70)
    with open(META_PATH, "r", encoding="utf-8") as f:
        cluster_slots = json.load(f)
    print(f"[+] โหลดสล็อตคลัสเตอร์สำเร็จ: {len(cluster_slots):,} รายการ")

    t_render = time.time()
    for item in cluster_slots:
        thai_str = item['thai']
        row = item['row']
        col = item['col']
        
        cell_img = render_smart_cluster_opt_a(thai_str)
        rows_dxt = encode_cell_dxt5(cell_img)
        
        bx0 = (col * 36) // 4
        by0 = (row * 36) // 4
        for by in range(9):
            offset = 128 + ((by0 + by) * WIDTH_BLOCKS + bx0) * BLOCK_BYTES
            dds_bytes[offset : offset + 144] = rows_dxt[by]

    el_render = time.time() - t_render
    print(f"[+] เรนเดอร์และบีบอัด DXT5 ครบ 2,208 คลัสเตอร์สำเร็จใน {el_render:.1f} วินาที!")

    # บันทึก DDS
    with open(TARGET_DDS, "wb") as f:
        f.write(dds_bytes)
    print(f"[+] บันทึกไฟล์ DDS อัปเดต: {TARGET_DDS}")

    # 4. แปลงกลับเป็น G1T และฉีดเข้าเกม
    print("\n" + "=" * 70)
    print(" [4/4] แปลง DDS เป็น G1T และฉีดเข้าสู่ LINKDATA.BIN...")
    print("=" * 70)
    os.makedirs(OUT_G1T_DIR, exist_ok=True)
    cmd = [sys.executable, G1T_TOOL, "import", TEX_DIR, OUT_G1T_DIR]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0, f"g1t_tool import failed: {res.stderr}"
    print(f"    [+] {res.stdout.strip()}")

    out_g1t = os.path.join(OUT_G1T_DIR, "entry_00055.g1t")
    with open(out_g1t, "rb") as f:
        g1t_raw = f.read()

    packed = pack_entry_chunks(g1t_raw)
    pad = b'\x00' * (ENTRY_55_ZSZ - len(packed))
    payload = packed + pad
    assert len(payload) == ENTRY_55_ZSZ

    targets = [
        ("Atmosphere Mod", MOD_BIN),
        ("Yuzu Mod", YUZU_BIN)
    ]

    for name, bin_path in targets:
        if os.path.exists(bin_path):
            with open(bin_path, "r+b") as f:
                f.seek(ENTRY_55_OFF)
                f.write(payload)
            print(f"    [+] ฉีด Entry 55 สำเร็จ -> {name} ({bin_path})")

    total_el = time.time() - start_time
    print("\n" + "=" * 70)
    print(f" [SUCCESS] สร้าง Font Atlas คันจิ Option A แท้ 2,292 ช่องสำเร็จทั้งหมดใน {total_el:.1f} วินาที!")
    print("=" * 70)

if __name__ == "__main__":
    main()
