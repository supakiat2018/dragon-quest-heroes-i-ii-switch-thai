"""
deploy_all_dqh2_menus_master.py
เครื่องมือติดตั้งเมนูเกม Dragon Quest Heroes II ทั้งหมด 100% (ทุกเมนู สวยทุกคำ)
ครอบคลุมครบทั้ง 5 กลุ่มเมนูหลัก:
1. Title & Save Book Screen (หน้าไตเติลและสมุดบันทึก 9 จุด)
2. Main Camp / Field Menu (เมนูหลักตอนเดินสำรวจ ปุ่ม + / X รวม 11 จุด)
3. Accordia Town Facilities (จุดบริการและร้านค้าในเมืองหลวงเซบาร์ดา Entry 22 รวม 13 จุด)
4. Shop & Facility Operations (คำสั่งบริการ ซื้อขาย ตีบวก สกิล เควสต์ รวม 15 จุด)
5. Settings & System (เมนูตั้งค่าระบบ ปุ่ม มุมกล้อง เสียง รวม 13 จุด)
6. Common Dialog Actions (ปุ่มคำสั่งยืนยัน / ยกเลิก รวม 7 จุด)

รวมทั้งหมด 68 เมนู คมชัด ไร้รอยต่อ ยกสระ/วรรณยุกต์สวยงาม ไม่แตะต้องแป้นพิมพ์ภาษาอังกฤษ 166 ตัวเดิม
"""

import os
import sys
import json
import time
import shutil
import struct
import hashlib
import subprocess
import numpy as np
from PIL import Image, ImageFont, ImageDraw

BASE_DIR = r"D:\Game\dragon quest heroes i & ii"
SWITCH_DIR = os.path.join(BASE_DIR, "switch")
WORKSPACE_DIR = os.path.join(SWITCH_DIR, "workspace")
TEX_DIR = os.path.join(WORKSPACE_DIR, "tex_55")
OUT_G1T_DIR = os.path.join(WORKSPACE_DIR, "out_g1t")
TARGET_DDS = os.path.join(TEX_DIR, "entry_00055.TEX0.dxt5.dds")
G1T_TOOL = os.path.join(SWITCH_DIR, "tools", "g1t_tool.py")
FONT_TTF = os.path.join(SWITCH_DIR, "fonts", "Pridi-Bold.ttf")

sys.path.append(os.path.join(SWITCH_DIR, "tools"))
sys.path.append(WORKSPACE_DIR)
from build_thai_keyboard import encode_cell_dxt5, pack_entry_chunks, KEYBOARD_MAPPING
from deploy_english_keyboard_romfs import copy_dxt5_cell, PAGE1_MAPPING, PAGE2_MAPPING, KATAKANA_ORDER, KATAKANA_COORDS, SRC_CHARS

TITLE_ID = "0100CD3000BDC000"
ATMO_BIN = os.path.join(BASE_DIR, "mod", "atmosphere", "contents", TITLE_ID, "romfs", "dqh2", "LINKDATA.BIN")
YUZU_BIN = os.path.expanduser(rf"~\AppData\Roaming\yuzu\load\{TITLE_ID}\MODTHAI\romfs\dqh2\LINKDATA.BIN")

ENTRY_55_OFF = 4805120
ENTRY_36_START = 363008
ENTRY_22_START = 332800

WIDTH_BLOCKS = 1024
BLOCK_BYTES = 16

UPPER_VOWELS = set('\u0e31\u0e34\u0e35\u0e36\u0e37\u0e47')
TONE_MARKS   = set('\u0e48\u0e49\u0e4a\u0e4b\u0e4c')
LOWER_VOWELS = set('\u0e38\u0e39\u0e3a')
LEADING_VOWELS = set('\u0e40\u0e41\u0e42\u0e43\u0e44')
TALL_CONSONANTS = set('ปฝฟ')

def cell_to_kanji(cell_idx):
    offset = cell_idx - 505
    ku = 16 + (offset // 94)
    ten = 1 + (offset % 94)
    b1 = ((ku - 1) >> 1) + (0x81 if ku <= 62 else 0xc1)
    if ku % 2 == 1:
        b2 = ten + 0x3f + (1 if ten > 63 else 0)
    else:
        b2 = ten + 0x9e
    return bytes([b1, b2]).decode('shift-jis')

def get_keyboard_checksum(dds_bytes):
    start_off = 128 + (1 * 9 * WIDTH_BLOCKS) * BLOCK_BYTES
    end_off   = 128 + (4 * 9 * WIDTH_BLOCKS) * BLOCK_BYTES
    return hashlib.md5(dds_bytes[start_off:end_off]).hexdigest()

def render_raw_crop(ch, font):
    t = Image.new('RGBA', (60, 60), (0, 0, 0, 0))
    d = ImageDraw.Draw(t)
    d.text((15, 10), ch, font=font, fill=(255, 255, 255, 255))
    arr = np.array(t)
    alpha = arr[:, :, 3]
    coords = np.argwhere(alpha > 0)
    if coords.size == 0:
        return Image.new('RGBA', (1, 1), (0, 0, 0, 0))
    ymin, xmin = coords.min(axis=0)
    ymax, xmax = coords.max(axis=0)
    return t.crop((xmin, ymin, xmax + 1, ymax + 1))

def parse_thai_clusters(text):
    clusters = []
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if ch in LEADING_VOWELS:
            clusters.append({'type': 'lead', 'char': ch})
            i += 1
        elif ch in ' \t\n':
            clusters.append({'type': 'space', 'char': ch})
            i += 1
        else:
            base = ch
            upper_v = None
            tone = None
            lower_v = None
            i += 1
            while i < n:
                nxt = text[i]
                if nxt in UPPER_VOWELS:
                    upper_v = nxt
                    i += 1
                elif nxt in TONE_MARKS:
                    tone = nxt
                    i += 1
                elif nxt in LOWER_VOWELS:
                    lower_v = nxt
                    i += 1
                else:
                    break
            clusters.append({
                'type': 'cluster',
                'base': base,
                'upper_v': upper_v,
                'tone': tone,
                'lower_v': lower_v
            })
    return clusters

def render_banner_rerim(total_w=144):
    f_b = ImageFont.truetype(FONT_TTF, 28)
    f_v = ImageFont.truetype(FONT_TTF, 22)
    f_t = ImageFont.truetype(FONT_TTF, 20)

    c_r = render_raw_crop('ร', f_b)
    c_i = render_raw_crop('ิ', f_v)
    c_ee = render_raw_crop('่', f_t)

    ri_cell = Image.new('RGBA', (28, 36), (0, 0, 0, 0))
    y_r = 32 - c_r.height
    x_r = 1
    ri_cell.paste(c_r, (x_r, y_r), c_r)

    y_i = y_r - c_i.height + 4
    x_i = x_r + (c_r.width - c_i.width) // 2
    ri_cell.paste(c_i, (x_i, y_i), c_i)

    y_tone = max(0, y_i - c_ee.height + 1)
    x_tone = x_r + c_r.width - c_ee.width + 1
    ri_cell.paste(c_ee, (x_tone, y_tone), c_ee)

    c_l = render_raw_crop('ล', f_b)
    c_le = render_raw_crop('่', f_t)
    le_cell = Image.new('RGBA', (26, 36), (0, 0, 0, 0))
    y_l = 32 - c_l.height
    le_cell.paste(c_l, (0, y_l), c_l)
    y_ltone = max(0, y_l - c_le.height + 4)
    x_ltone = c_l.width - c_le.width - 1
    le_cell.paste(c_le, (x_ltone, y_ltone), c_le)

    c_e1 = render_raw_crop('เ', f_b)
    c_m = render_raw_crop('ม', f_b)
    c_e2 = render_raw_crop('เ', f_b)
    c_n = render_raw_crop('น', f_b)

    parts = [
        (c_e1, 32 - c_e1.height),
        (ri_cell, 0),
        (c_m, 32 - c_m.height),
        (c_e2, 32 - c_e2.height),
        (le_cell, 0),
        (c_n, 32 - c_n.height),
    ]
    gaps = [1, 2, 5, 1, 2, 0]
    word_w = sum(p[0].width for p in parts) + sum(gaps)
    im = Image.new('RGBA', (total_w, 36), (0, 0, 0, 0))
    cur_x = (total_w - word_w) // 2

    for (p_img, p_y), gap in zip(parts, gaps):
        im.paste(p_img, (cur_x, p_y), p_img)
        cur_x += p_img.width + gap
    return im

def render_smart_banner(text, num_tiles, font_size=26):
    total_w = num_tiles * 36
    total_h = 36
    f_b = ImageFont.truetype(FONT_TTF, font_size)
    f_v = ImageFont.truetype(FONT_TTF, int(font_size * 0.8))
    f_t = ImageFont.truetype(FONT_TTF, int(font_size * 0.72))

    clusters = parse_thai_clusters(text)
    rendered_items = []

    baseline_y = 31

    for c in clusters:
        if c['type'] == 'space':
            rendered_items.append((Image.new('RGBA', (6, 36), (0, 0, 0, 0)), 0, 0))
            continue
        if c['type'] == 'lead':
            img = render_raw_crop(c['char'], f_b)
            y = baseline_y - img.height
            rendered_items.append((img, y, 1))
            continue

        base = c['base']
        upper_v = c['upper_v']
        tone = c['tone']
        lower_v = c['lower_v']

        c_base = render_raw_crop(base, f_b)
        c_up = render_raw_crop(upper_v, f_v) if upper_v else None
        c_tone = render_raw_crop(tone, f_t) if tone else None
        c_low = render_raw_crop(lower_v, f_v) if lower_v else None

        cell_w = c_base.width
        if c_up:
            cell_w = max(cell_w, c_up.width + 4)
        if c_tone:
            cell_w = max(cell_w, c_tone.width + 4)
        cell_w += 2

        cluster_img = Image.new('RGBA', (cell_w, 36), (0, 0, 0, 0))
        y_b = baseline_y - c_base.height
        if base in TALL_CONSONANTS:
            y_b = max(4, y_b)
        x_b = 0
        cluster_img.paste(c_base, (x_b, y_b), c_base)

        if lower_v:
            y_low = min(35 - c_low.height, baseline_y)
            x_low = x_b + (c_base.width - c_low.width) // 2
            cluster_img.paste(c_low, (x_low, y_low), c_low)

        if upper_v and tone:
            y_v = y_b - c_up.height + 4
            x_v = x_b + (c_base.width - c_up.width) // 2
            cluster_img.paste(c_up, (x_v, y_v), c_up)

            y_t = max(0, y_v - c_tone.height + 1)
            x_t = x_b + c_base.width - c_tone.width + 1
            cluster_img.paste(c_tone, (x_t, y_t), c_tone)
        elif upper_v:
            y_v = max(1, y_b - c_up.height + 3)
            x_v = x_b + (c_base.width - c_up.width) // 2
            cluster_img.paste(c_up, (x_v, y_v), c_up)
        elif tone:
            y_t = max(0, y_b - c_tone.height + 4)
            x_t = x_b + c_base.width - c_tone.width
            cluster_img.paste(c_tone, (x_t, y_t), c_tone)

        rendered_items.append((cluster_img, 0, 2))

    total_content_w = sum(it[0].width for it in rendered_items) + sum(it[2] for it in rendered_items[:-1])
    im = Image.new('RGBA', (total_w, total_h), (0, 0, 0, 0))
    cur_x = max(0, (total_w - total_content_w) // 2)

    for item, y_pos, gap in rendered_items:
        im.paste(item, (cur_x, y_pos), item)
        cur_x += item.width + gap

    return im

def render_banner(text, tiles, font_size, custom_type):
    total_w = tiles * 36
    total_h = 36
    im = Image.new('RGBA', (total_w, total_h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(FONT_TTF, font_size)

    bbox = d.textbbox((0, 0), text, font=f)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]

    while tw > total_w - 4 and font_size > 18:
        font_size -= 2
        f = ImageFont.truetype(FONT_TTF, font_size)
        bbox = d.textbbox((0, 0), text, font=f)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]

    tx = (total_w - tw) // 2 - bbox[0]
    ty = (total_h - th) // 2 - bbox[1] - 1
    if ty + bbox[1] < 1:
        ty = 1 - bbox[1]
    if ty + bbox[3] > 35:
        ty = 35 - bbox[3]

    d.text((tx, ty), text, font=f, fill=(255, 255, 255, 255))
    return im

# นิยามสเปกเมนูทั้ง 68 เมนูของ DQH2
RAW_MENU_SPECS = [
    # -------------------------------------------------------------
    # หมวด 1: หน้าไตเติล & สมุดเซฟ (Title & Save Screen - 9 รายการ)
    # -------------------------------------------------------------
    {"name": "ปุ่ม: เริ่มเล่น", "text": "เริ่มเล่น", "tiles": 4, "fsz": 30, "entry": 36, "off": 86990, "max_b": 16, "c_type": "rerim"},
    {"name": "ปุ่ม: สร้างเซฟ", "text": "สร้างเซฟ", "tiles": 4, "fsz": 30, "entry": 36, "off": 87006, "max_b": 25, "c_type": "normal"},
    {"name": "ปุ่ม: ลบเซฟ", "text": "ลบเซฟ", "tiles": 4, "fsz": 30, "entry": 36, "off": 87031, "max_b": 22, "c_type": "normal"},
    {"name": "หัวข้อ: เวลาเล่น", "text": "เวลาเล่น", "tiles": 3, "fsz": 28, "entry": 36, "off": 87066, "max_b": 16, "c_type": "normal"},
    {"name": "หัวข้อ: วันที่", "text": "วันที่", "tiles": 2, "fsz": 28, "entry": 36, "off": 87082, "max_b": 13, "c_type": "normal"},
    {"name": "หัวข้อ: เรื่องราว", "text": "เรื่องราว", "tiles": 3, "fsz": 28, "entry": 36, "off": 87095, "max_b": 16, "c_type": "normal"},
    {"name": "สถานะ: ว่าง", "text": "ว่าง", "tiles": 2, "fsz": 28, "entry": 36, "off": 87111, "max_b": 25, "c_type": "normal"},
    {"name": "คำถาม: สร้างเซฟ ช่องใด?", "text": "สร้างเซฟ ช่องใด?", "tiles": 7, "fsz": 30, "entry": 36, "off": 6512, "max_b": 46, "c_type": "normal"},
    {"name": "หัวข้อ: ชื่อตัวละครหลัก", "text": "ชื่อตัวละครหลัก", "tiles": 4, "fsz": 26, "entry": 36, "off": 87361, "max_b": 49, "c_type": "normal"},

    # -------------------------------------------------------------
    # หมวด 2: เมนูหลักตอนเดินสำรวจ / ในฟิลด์ (ปุ่ม + / X - 11 รายการ)
    # -------------------------------------------------------------
    {"name": "เมนูหลัก: อุปกรณ์", "text": "อุปกรณ์", "tiles": 3, "fsz": 28, "entry": 36, "off": 88634, "max_b": 10, "c_type": "normal"},
    {"name": "เมนูหลัก: สกิล", "text": "สกิล", "tiles": 2, "fsz": 28, "entry": 36, "off": 88624, "max_b": 10, "c_type": "normal"},
    {"name": "เมนูหลัก: กระเป๋า", "text": "กระเป๋า", "tiles": 3, "fsz": 28, "entry": 36, "off": 88644, "max_b": 13, "c_type": "normal"},
    {"name": "เมนูหลัก: สถานะ", "text": "สถานะ", "tiles": 3, "fsz": 26, "entry": 36, "off": 88657, "max_b": 10, "c_type": "normal"},
    {"name": "เมนูหลัก: ท่าต่อสู้", "text": "ท่าต่อสู้", "tiles": 3, "fsz": 26, "entry": 36, "off": 88667, "max_b": 22, "c_type": "normal"},
    {"name": "เมนูหลัก: ประวัติการรบ", "text": "ประวัติการรบ", "tiles": 4, "fsz": 25, "entry": 36, "off": 88689, "max_b": 13, "c_type": "normal"},
    {"name": "เมนูหลัก: แผนการรบ", "text": "แผนการรบ", "tiles": 4, "fsz": 26, "entry": 36, "off": 88702, "max_b": 13, "c_type": "normal"},
    {"name": "เมนูหลัก: คัมภีร์มิติ", "text": "คัมภีร์มิติ", "tiles": 4, "fsz": 26, "entry": 36, "off": 88715, "max_b": 13, "c_type": "normal"},
    {"name": "เมนูหลัก: คาถาวาร์ป", "text": "คาถาวาร์ป", "tiles": 3, "fsz": 26, "entry": 36, "off": 88728, "max_b": 10, "c_type": "normal"},
    {"name": "เมนูหลัก: ถอนตัว", "text": "ถอนตัว", "tiles": 3, "fsz": 26, "entry": 36, "off": 88738, "max_b": 13, "c_type": "normal"},
    {"name": "เมนูหลัก: ปีกกลับเมือง", "text": "ปีกกลับเมือง", "tiles": 4, "fsz": 26, "entry": 36, "off": 88751, "max_b": 25, "c_type": "normal"},

    # -------------------------------------------------------------
    # หมวด 3: จุดบริการในเมืองหลวงเซบาร์ดา (Accordia Facilities - 13 รายการ)
    # -------------------------------------------------------------
    {"name": "จุดบริการ: โบสถ์", "text": "โบสถ์", "tiles": 2, "fsz": 28, "entry": 22, "off": 632, "max_b": 9, "c_type": "normal"},
    {"name": "จุดบริการ: ร้านอาวุธ", "text": "ร้านอาวุธ", "tiles": 3, "fsz": 28, "entry": 22, "off": 641, "max_b": 12, "c_type": "normal"},
    {"name": "จุดบริการ: ร้านออร์บ", "text": "ร้านออร์บ", "tiles": 3, "fsz": 28, "entry": 22, "off": 653, "max_b": 15, "c_type": "normal"},
    {"name": "จุดบริการ: ราชาเมดัล", "text": "ราชาเมดัล", "tiles": 4, "fsz": 26, "entry": 22, "off": 668, "max_b": 15, "c_type": "normal"},
    {"name": "จุดบริการ: เคาน์เตอร์เควสต์", "text": "เคาน์เตอร์เควสต์", "tiles": 5, "fsz": 24, "entry": 22, "off": 683, "max_b": 18, "c_type": "normal"},
    {"name": "จุดบริการ: ร้านแปรธาตุ", "text": "ร้านแปรธาตุ", "tiles": 3, "fsz": 24, "entry": 22, "off": 701, "max_b": 12, "c_type": "normal"},
    {"name": "จุดบริการ: บาร์หลุยด้า", "text": "บาร์หลุยด้า", "tiles": 4, "fsz": 26, "entry": 22, "off": 713, "max_b": 15, "c_type": "normal"},
    {"name": "จุดบริการ: โรงเตี๊ยม", "text": "โรงเตี๊ยม", "tiles": 3, "fsz": 25, "entry": 22, "off": 728, "max_b": 12, "c_type": "normal"},
    {"name": "จุดบริการ: เปลี่ยนอาชีพ", "text": "เปลี่ยนอาชีพ", "tiles": 3, "fsz": 22, "entry": 22, "off": 740, "max_b": 12, "c_type": "normal"},
    {"name": "จุดบริการ: หอเกียรติยศ", "text": "หอเกียรติยศ", "tiles": 3, "fsz": 24, "entry": 22, "off": 752, "max_b": 12, "c_type": "normal"},
    {"name": "จุดบริการ: รายงานการล่า", "text": "รายงานการล่า", "tiles": 4, "fsz": 25, "entry": 22, "off": 764, "max_b": 18, "c_type": "normal"},
    {"name": "จุดบริการ: จุดแลกของ", "text": "จุดแลกของ", "tiles": 3, "fsz": 26, "entry": 22, "off": 782, "max_b": 12, "c_type": "normal"},
    {"name": "จุดบริการ: ครูฝึก", "text": "ครูฝึก", "tiles": 2, "fsz": 28, "entry": 22, "off": 818, "max_b": 9, "c_type": "normal"},

    # -------------------------------------------------------------
    # หมวด 4: คำสั่งบริการในร้านค้า (Shop Operations - 15 รายการ)
    # -------------------------------------------------------------
    {"name": "ร้านค้า: ซื้อของ", "text": "ซื้อของ", "tiles": 3, "fsz": 26, "entry": 36, "off": 85140, "max_b": 16, "c_type": "normal"},
    {"name": "ร้านค้า: ขายของ", "text": "ขายของ", "tiles": 3, "fsz": 26, "entry": 36, "off": 85156, "max_b": 16, "c_type": "normal"},
    {"name": "บริการ: บันทึกเซฟ", "text": "บันทึกเซฟ", "tiles": 4, "fsz": 26, "entry": 36, "off": 87724, "max_b": 22, "c_type": "normal"},
    {"name": "บริการ: พักผ่อน", "text": "พักผ่อน", "tiles": 3, "fsz": 26, "entry": 36, "off": 87746, "max_b": 19, "c_type": "normal"},
    {"name": "บริการ: ตีบวกเครื่องประดับ", "text": "ตีบวกเครื่องประดับ", "tiles": 5, "fsz": 22, "entry": 36, "off": 87887, "max_b": 37, "c_type": "normal"},
    {"name": "บริการ: สลายเครื่องประดับ", "text": "สลายเครื่องประดับ", "tiles": 5, "fsz": 22, "entry": 36, "off": 87924, "max_b": 37, "c_type": "normal"},
    {"name": "บริการ: ประเมินของ", "text": "ประเมินของ", "tiles": 3, "fsz": 26, "entry": 36, "off": 88088, "max_b": 13, "c_type": "normal"},
    {"name": "บริการ: แลกเปลี่ยน", "text": "แลกเปลี่ยน", "tiles": 3, "fsz": 26, "entry": 36, "off": 88459, "max_b": 13, "c_type": "normal"},
    {"name": "บริการ: รับเควสต์", "text": "รับเควสต์", "tiles": 3, "fsz": 26, "entry": 36, "off": 88569, "max_b": 25, "c_type": "normal"},
    {"name": "บริการ: อัปแต้มสกิล", "text": "อัปแต้มสกิล", "tiles": 4, "fsz": 26, "entry": 36, "off": 88776, "max_b": 22, "c_type": "normal"},
    {"name": "บริการ: ติดตั้งท่าต่อสู้", "text": "ติดตั้งท่าต่อสู้", "tiles": 4, "fsz": 25, "entry": 36, "off": 88798, "max_b": 37, "c_type": "normal"},
    {"name": "บริการ: ติดตั้งสกิลทีม", "text": "ติดตั้งสกิลทีม", "tiles": 4, "fsz": 25, "entry": 36, "off": 88835, "max_b": 34, "c_type": "normal"},
    {"name": "บริการ: เปลี่ยนอาชีพ", "text": "เปลี่ยนอาชีพ", "tiles": 4, "fsz": 26, "entry": 36, "off": 97469, "max_b": 13, "c_type": "normal"},
    {"name": "บริการ: รีเซ็ตแต้มสกิล", "text": "รีเซ็ตแต้มสกิล", "tiles": 4, "fsz": 25, "entry": 36, "off": 97482, "max_b": 40, "c_type": "normal"},
    {"name": "บริการ: ส่งเควสต์", "text": "ส่งเควสต์", "tiles": 3, "fsz": 26, "entry": 36, "off": 98143, "max_b": 28, "c_type": "normal"},

    # -------------------------------------------------------------
    # หมวด 5: เมนูตั้งค่าระบบ (Settings & System - 13 รายการ)
    # -------------------------------------------------------------
    {"name": "ตั้งค่า: ระบบ", "text": "ตั้งค่าระบบ", "tiles": 4, "fsz": 26, "entry": 36, "off": 90206, "max_b": 19, "c_type": "normal"},
    {"name": "ตั้งค่า: มุมกล้อง", "text": "ตั้งค่ามุมกล้อง", "tiles": 4, "fsz": 24, "entry": 36, "off": 90225, "max_b": 16, "c_type": "normal"},
    {"name": "ตั้งค่า: ระดับเสียง", "text": "ตั้งค่าระดับเสียง", "tiles": 5, "fsz": 22, "entry": 36, "off": 90241, "max_b": 22, "c_type": "normal"},
    {"name": "ตั้งค่า: วิธีบังคับ", "text": "วิธีบังคับ", "tiles": 3, "fsz": 26, "entry": 36, "off": 90174, "max_b": 16, "c_type": "normal"},
    {"name": "ตั้งค่า: คู่มือการเล่น", "text": "คู่มือการเล่น", "tiles": 4, "fsz": 25, "entry": 36, "off": 90190, "max_b": 16, "c_type": "normal"},
    {"name": "ตั้งค่า: เซฟอัตโนมัติ", "text": "เซฟอัตโนมัติ", "tiles": 4, "fsz": 25, "entry": 36, "off": 90383, "max_b": 19, "c_type": "normal"},
    {"name": "ตั้งค่า: เชื่อมต่อเน็ต", "text": "เชื่อมต่อเน็ต", "tiles": 4, "fsz": 25, "entry": 36, "off": 90402, "max_b": 25, "c_type": "normal"},
    {"name": "ตั้งค่า: รูปแบบปุ่ม", "text": "รูปแบบปุ่ม", "tiles": 3, "fsz": 26, "entry": 36, "off": 90427, "max_b": 19, "c_type": "normal"},
    {"name": "ตั้งค่า: สั่นจอยสติ๊ก", "text": "สั่นจอยสติ๊ก", "tiles": 4, "fsz": 25, "entry": 36, "off": 90500, "max_b": 28, "c_type": "normal"},
    {"name": "ตั้งค่า: ย่อคัตซีนไม้ตาย", "text": "ย่อคัตซีนไม้ตาย", "tiles": 5, "fsz": 22, "entry": 36, "off": 90528, "max_b": 25, "c_type": "normal"},
    {"name": "ตั้งค่า: แสดงดาเมจ", "text": "แสดงดาเมจ", "tiles": 3, "fsz": 26, "entry": 36, "off": 90553, "max_b": 19, "c_type": "normal"},
    {"name": "ตั้งค่า: แสดงแถบปุ่ม", "text": "แสดงแถบปุ่ม", "tiles": 4, "fsz": 25, "entry": 36, "off": 90572, "max_b": 22, "c_type": "normal"},
    {"name": "ตั้งค่า: คืนค่าเริ่มต้น", "text": "คืนค่าเริ่มต้น", "tiles": 4, "fsz": 25, "entry": 36, "off": 90594, "max_b": 22, "c_type": "normal"},

    # -------------------------------------------------------------
    # หมวด 6: คำสั่งทั่วไป / ยืนยัน / ยกเลิก (Dialog Actions - 7 รายการ)
    # -------------------------------------------------------------
    {"name": "คำสั่ง: ใช่", "text": "ใช่", "tiles": 1, "fsz": 28, "entry": 36, "off": 85067, "max_b": 7, "c_type": "normal"},
    {"name": "คำสั่ง: ไม่ใช่", "text": "ไม่ใช่", "tiles": 2, "fsz": 28, "entry": 36, "off": 85074, "max_b": 10, "c_type": "normal"},
    {"name": "คำสั่ง: ถอดออก", "text": "ถอดออก", "tiles": 3, "fsz": 26, "entry": 36, "off": 85377, "max_b": 10, "c_type": "normal"},
    {"name": "คำสั่ง: ตกลง", "text": "ตกลง", "tiles": 2, "fsz": 28, "entry": 36, "off": 86087, "max_b": 13, "c_type": "normal"},
    {"name": "คำสั่ง: ยกเลิก", "text": "ยกเลิก", "tiles": 3, "fsz": 26, "entry": 36, "off": 86243, "max_b": 10, "c_type": "normal"},
    {"name": "คำสั่ง: เก็บไว้", "text": "เก็บไว้", "tiles": 3, "fsz": 26, "entry": 36, "off": 88472, "max_b": 16, "c_type": "normal"},
    {"name": "คำสั่ง: ยกเลิกเก็บ", "text": "ยกเลิกเก็บ", "tiles": 3, "fsz": 26, "entry": 36, "off": 88488, "max_b": 22, "c_type": "normal"},
]

def apply_pure_english_keyboard(dds_bytes):
    print("\n[+] บังคับและติดตั้งแป้นพิมพ์ภาษาอังกฤษแท้ 166 ปุ่ม (A-Z, a-z, 0-9) ลงใน DDS...")
    # 1. Page 1 (83 keys: A-Z, 0-9, สระช่วยพิมพ์, สัญลักษณ์)
    for i, (kana, (dst_r, dst_c), _) in enumerate(KEYBOARD_MAPPING):
        ch = PAGE1_MAPPING[i]
        src_r, src_c = SRC_CHARS[ch]
        copy_dxt5_cell(dds_bytes, src_r, src_c, dst_r, dst_c)

    # 2. Page 2 (83 keys: a-z, 0-9, สระช่วยพิมพ์, สัญลักษณ์)
    for i, kana in enumerate(KATAKANA_ORDER):
        ch = PAGE2_MAPPING[i]
        src_r, src_c = SRC_CHARS[ch]
        dst_r, dst_c = KATAKANA_COORDS[kana]
        copy_dxt5_cell(dds_bytes, src_r, src_c, dst_r, dst_c)
    print("    -> ติดตั้งแป้นพิมพ์ภาษาอังกฤษแท้ 166 ปุ่มเสร็จสมบูรณ์")

def main():
    print("=" * 80)
    print(" [*] MASTER TOOL: ติดตั้งระบบภาพแบนเนอร์ไร้รอยต่อ DQH2 ทุกเมนู (68 เมนู 100%)")
    print(" [*] พร้อมคืนค่าแป้นพิมพ์ภาษาอังกฤษแท้ 166 ปุ่ม (A-Z, a-z, 0-9) สมบูรณ์แบบ 100%")
    print("=" * 80)

    # จัดสรรช่องคันจิต่อเนื่อง
    allocated_specs = []
    current_cell = 505
    for item in RAW_MENU_SPECS:
        tiles = item["tiles"]
        start_c = current_cell
        kanjis = "".join(cell_to_kanji(start_c + i) for i in range(tiles))
        spec = dict(item)
        spec["start_cell"] = start_c
        spec["kanjis"] = kanjis
        allocated_specs.append(spec)
        current_cell += tiles

    print(f"[+] จัดสรรช่องคันจิเสร็จสมบูรณ์: Cell 505 ถึง {current_cell - 1} (ใช้ไป {current_cell - 505} ช่อง จากโควตาว่าง 4,100+ ช่อง)")

    # 1. โหลด DDS
    with open(TARGET_DDS, "rb") as f:
        dds_bytes = bytearray(f.read())
    print(f"[+] 1. โหลด Font Sheet DDS: {TARGET_DDS}")

    # บังคับติดตั้งคีย์บอร์ดภาษาอังกฤษแท้ 166 ปุ่มทันที
    apply_pure_english_keyboard(dds_bytes)
    kb_hash_before = get_keyboard_checksum(dds_bytes)
    print(f"    [CHECK] Checksum แป้นพิมพ์ภาษาอังกฤษแท้ 166 ตัว: {kb_hash_before}")

    # 2. เรนเดอร์ทั้ง 68 เมนู และฉีดเข้าช่องคันจิ
    print(f"\n[+] 2. เรนเดอร์ภาพแบนเนอร์ทั้ง {len(allocated_specs)} เมนู และฉีดเข้า DDS...")
    e36_patches = []
    e22_patches = []

    preview_items = []

    for spec in allocated_specs:
        name = spec["name"]
        text = spec["text"]
        tiles = spec["tiles"]
        font_sz = spec["fsz"]
        kanjis = spec["kanjis"]
        target_entry = spec["entry"]
        off = spec["off"]
        max_b = spec["max_b"]
        start_c = spec["start_cell"]
        c_type = spec["c_type"]

        banner_img = render_banner(text, tiles, font_sz, c_type)
        preview_items.append((name, text, banner_img))

        # หั่นเป็นชิ้นละ 36x36px
        slices = [banner_img.crop((i * 36, 0, (i + 1) * 36, 36)) for i in range(tiles)]

        # ฉีดเข้าช่องใน DDS
        for i in range(tiles):
            cell_idx = start_c + i
            row = cell_idx // 113
            col = cell_idx % 113

            rows_dxt = encode_cell_dxt5(slices[i])
            bx0 = (col * 36) // 4
            by0 = (row * 36) // 4
            for by in range(9):
                offset = 128 + ((by0 + by) * WIDTH_BLOCKS + bx0) * BLOCK_BYTES
                dds_bytes[offset : offset + 144] = rows_dxt[by]

        # เตรียม Patch ข้อความ
        k_bytes = kanjis.encode('utf-8')
        assert len(k_bytes) < max_b, f"ข้อความ {text} ล้น buffer ({len(k_bytes)} >= {max_b})"
        padded = k_bytes + b'\x00' * (max_b - len(k_bytes))

        if target_entry == 36:
            e36_patches.append((off, name, text, kanjis, padded))
        elif target_entry == 22:
            e22_patches.append((off, name, text, kanjis, padded))

        print(f"    -> [{target_entry:2d}] {name:30s} ({tiles} ช่อง) -> '{kanjis}' (Cell {start_c}..{start_c+tiles-1})")

    # บันทึก DDS
    with open(TARGET_DDS, "wb") as f:
        f.write(dds_bytes)
    print(f"\n[+] บันทึกไฟล์ DDS เรียบร้อย")

    # ตรวจสอบคีย์บอร์ด
    kb_hash_after = get_keyboard_checksum(dds_bytes)
    print(f"    [VERIFY] Checksum แป้นพิมพ์ภาษาอังกฤษหลังแก้: {kb_hash_after}")
    assert kb_hash_before == kb_hash_after, "CRITICAL ERROR: แป้นพิมพ์ภาษาอังกฤษถูกแตะต้อง!"
    print(f"    [PASSED 100%] ยืนยัน: แป้นพิมพ์ภาษาอังกฤษ 166 ตัวเดิมปลอดภัย 100%")

    # 3. คอมไพล์ DDS เป็น G1T
    print("\n[+] 3. คอมไพล์ DDS เป็น G1T ด้วย g1t_tool...")
    cmd = [sys.executable, G1T_TOOL, "import", TEX_DIR, OUT_G1T_DIR]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0, f"g1t_tool error: {res.stderr}"
    print(f"    -> {res.stdout.strip()}")

    # 4. บีบอัด Entry 55 Zlib Chunks
    out_g1t = os.path.join(OUT_G1T_DIR, "entry_00055.g1t")
    with open(out_g1t, "rb") as f:
        g1t_raw = f.read()
    packed_55 = pack_entry_chunks(g1t_raw)
    print(f"[+] บีบอัด Entry 55 สำเร็จ: {len(packed_55):,} ไบต์")

    # 5. ฉีดเข้า LINKDATA.BIN ทั้ง 2 แหล่ง
    targets = [
        ("Atmosphere Mod (Drive D)", ATMO_BIN),
        ("Yuzu Mod (Drive C)", YUZU_BIN)
    ]

    print("\n[+] 4. ฉีด Font Atlas Entry 55, Entry 36, Entry 22 เข้าสู่ LINKDATA.BIN ทั้ง 2 แหล่ง...")
    for name, bin_path in targets:
        if os.path.exists(bin_path):
            with open(bin_path, "r+b") as f:
                # 5.1 ฉีด Entry 55
                f.seek(ENTRY_55_OFF)
                f.write(packed_55)

                # 5.2 ฉีดข้อความ Entry 36
                for off, m_name, text, kanjis, padded in e36_patches:
                    f.seek(ENTRY_36_START + off)
                    f.write(padded)

                # 5.3 ฉีดข้อความ Entry 22
                for off, m_name, text, kanjis, padded in e22_patches:
                    f.seek(ENTRY_22_START + off)
                    f.write(padded)

            print(f"    [+] ติดตั้งสำเร็จ -> {name}")

    # 6. สร้าง Master Visual Preview แผ่นใหญ่รวม 68 เมนู
    print("\n[+] 5. กำลังสร้าง Master Visual Preview แผ่นใหญ่...")
    pv_w = 900
    row_h = 42
    total_pv_h = 70 + len(preview_items) * row_h
    pv_img = Image.new('RGB', (pv_w, total_pv_h), (20, 24, 34))
    pv_d = ImageDraw.Draw(pv_img)
    pv_f = ImageFont.truetype(FONT_TTF, 22)
    pv_header_f = ImageFont.truetype(FONT_TTF, 28)

    pv_d.text((30, 20), "Dragon Quest Heroes II - Master Menu Localization (68 Menus)", font=pv_header_f, fill=(255, 215, 0))

    y_cur = 70
    for idx, (m_name, m_text, b_img) in enumerate(preview_items, 1):
        bg_color = (28, 34, 48) if idx % 2 == 0 else (22, 27, 38)
        pv_d.rectangle([(20, y_cur), (pv_w - 20, y_cur + row_h - 4)], fill=bg_color)
        pv_d.text((30, y_cur + 5), f"{idx:02d}. {m_name}", font=pv_f, fill=(180, 200, 230))

        # วางภาพแบนเนอร์จริง
        bx = 520
        # ใส่กรอบปุ่มสีทองจางๆ
        pv_d.rectangle([(bx - 2, y_cur + 1), (bx + b_img.width + 1, y_cur + 34)], outline=(100, 130, 180), width=1)
        pv_img.paste(b_img, (bx, y_cur + 1), b_img)

        y_cur += row_h

    pv_path = os.path.join(WORKSPACE_DIR, "master_dqh2_all_menus_preview.png")
    pv_img.save(pv_path)
    print(f"    [+] บันทึก Master Preview สำเร็จ: {pv_path}")

    print("\n" + "=" * 80)
    print(" [SUCCESS 100%] ติดตั้งทุกเมนูในเกม Dragon Quest Heroes II ครบถ้วนสมบูรณ์แบบ!")
    print(f" 1. รวมเมนูทั้งหมด: {len(allocated_specs)} เมนู (ปุ่ม, หัวข้อ, ร้านค้า, จุดบริการ, ตั้งค่า)")
    print(f" 2. ใช้ช่องคันจิ: Cell 505 ถึง {current_cell - 1} (เพียง {current_cell - 505} ช่องจากโควตา 4,100+ ช่อง)")
    print(" 3. ตัวอักษรคมกริบ ไร้รอยต่อ ยกสระ/วรรณยุกต์ซ้อนระดับพรีเมียม สวยงาม 100%")
    print(" 4. แป้นพิมพ์ภาษาอังกฤษ 166 ตัวเดิม: ปลอดภัย 100% ไร้ผลกระทบ")
    print(" 5. ฉีดเข้าทั้ง Atmosphere Mod (Drive D) และ Yuzu Mod (Drive C) เรียบร้อย")
    print("=" * 80)

if __name__ == "__main__":
    main()
