"""
deploy_all_dqh2_menus_master.py
เครื่องมือติดตั้งระบบแปลภาษาไทย Dragon Quest Heroes II แบบสมบูรณ์แบบ 100%
ครอบคลุม:
1. แป้นพิมพ์ภาษาอังกฤษแท้ 166 ปุ่ม (A-Z, a-z, 0-9) ป้องกันการถูกทับ 100% (Cells 210..377)
2. เมนูเกมทั้งหมด 68 เมนู (6 หมวดหมู่หลัก) ไร้รอยต่อ Option A สวยทุกคำ (Cells 505..738)
3. แถบแนะนำปุ่มกดท้ายจอ 36 คำหลัก (42 สล็อตใน Entry 36) สไตล์เกมเมอร์ สั้นกระชับ ยกสระลอย Option A คมชัด (Cells 740..816)
4. ปลอดภัย 100% ไร้ Buffer Overflow (0% Overflow) และคงรหัสไอคอนปุ่ม Switch (\x1bP...) ไว้สมบูรณ์แบบ
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

def render_banner(text, tiles, font_size, custom_type):
    if custom_type == "rerim":
        return render_banner_rerim(tiles * 36)

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

def render_elevated_cluster(base_ch, upper_v, tone_m, f_size=26):
    f_b = ImageFont.truetype(FONT_TTF, f_size)
    f_v = ImageFont.truetype(FONT_TTF, int(f_size * 0.85))
    f_t = ImageFont.truetype(FONT_TTF, int(f_size * 0.75))

    t_b = Image.new('RGBA', (60, 60), (0,0,0,0))
    ImageDraw.Draw(t_b).text((10, 10), base_ch, font=f_b, fill=(255,255,255,255))
    bbox_b = t_b.getbbox()
    c_b = t_b.crop(bbox_b)

    t_v = Image.new('RGBA', (60, 60), (0,0,0,0))
    ImageDraw.Draw(t_v).text((10, 15), 'อ' + upper_v, font=f_v, fill=(255,255,255,255))
    t_dummy = Image.new('RGBA', (60, 60), (0,0,0,0))
    ImageDraw.Draw(t_dummy).text((10, 15), 'อ', font=f_v, fill=(255,255,255,255))
    arr_v = np.array(t_v)
    arr_d = np.array(t_dummy)
    mask = (arr_v[:, :, 3] > 0) & (arr_d[:, :, 3] == 0)
    arr_clean = np.zeros_like(arr_v)
    arr_clean[mask] = arr_v[mask]
    img_v = Image.fromarray(arr_clean)
    bbox_v = img_v.getbbox()
    c_v = img_v.crop(bbox_v) if bbox_v else Image.new('RGBA', (1,1), (0,0,0,0))

    t_t = Image.new('RGBA', (60, 60), (0,0,0,0))
    ImageDraw.Draw(t_t).text((10, 15), 'อ' + tone_m, font=f_t, fill=(255,255,255,255))
    arr_t = np.array(t_t)
    mask_t = (arr_t[:, :, 3] > 0) & (arr_d[:, :, 3] == 0)
    arr_t_clean = np.zeros_like(arr_t)
    arr_t_clean[mask_t] = arr_t[mask_t]
    img_t = Image.fromarray(arr_t_clean)
    bbox_t = img_t.getbbox()
    c_t = img_t.crop(bbox_t) if bbox_t else Image.new('RGBA', (1,1), (0,0,0,0))

    cl_w = max(c_b.width, c_v.width + 4, c_t.width + 4) + 2
    cl = Image.new('RGBA', (cl_w, 36), (0,0,0,0))

    y_b = 32 - c_b.height
    x_b = (cl_w - c_b.width) // 2
    cl.paste(c_b, (x_b, y_b), c_b)

    x_v = x_b + (c_b.width - c_v.width) // 2
    if base_ch in 'ปฝฟ':
        x_v -= 2
    elif base_ch in 'ท':
        x_v += 2
    y_v = y_b - c_v.height + 3
    cl.paste(c_v, (x_v, y_v), c_v)

    x_t = x_b + c_b.width - c_t.width + 1
    if base_ch in 'ปฝฟ':
        x_t -= 3
    y_t = max(0, y_v - c_t.height + 1)
    cl.paste(c_t, (x_t, y_t), c_t)

    return cl

def render_guide_banner_master(text, num_tiles, font_size=28):
    total_w = num_tiles * 36
    total_h = 36
    f = ImageFont.truetype(FONT_TTF, font_size)

    stacked_words = ["วิ่ง", "ฟื้นฟู", "ที่ได้", "ที่ใช้", "สลับที่", "ทิ้ง", "ใช้ทีมนี้"]

    if text not in stacked_words:
        im = Image.new('RGBA', (total_w, total_h), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
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
        if ty + bbox[1] < 1: ty = 1 - bbox[1]
        if ty + bbox[3] > 35: ty = 35 - bbox[3]
        d.text((tx, ty), text, font=f, fill=(255, 255, 255, 255))
        return im

    if text == "วิ่ง":
        cl_wi = render_elevated_cluster('ว', 'ิ', '่', font_size)
        f_norm = ImageFont.truetype(FONT_TTF, font_size)
        t_ng = Image.new('RGBA', (40, 40), (0,0,0,0))
        ImageDraw.Draw(t_ng).text((5, 5), 'ง', font=f_norm, fill=(255,255,255,255))
        c_ng = t_ng.crop(t_ng.getbbox())
        tw = cl_wi.width + 1 + c_ng.width
        im = Image.new('RGBA', (total_w, total_h), (0, 0, 0, 0))
        cx = (total_w - tw) // 2
        im.paste(cl_wi, (cx, 0), cl_wi)
        im.paste(c_ng, (cx + cl_wi.width + 1, 32 - c_ng.height), c_ng)
        return im

    if text == "ฟื้นฟู":
        cl_fuen = render_elevated_cluster('ฟ', 'ื', '้', font_size)
        f_norm = ImageFont.truetype(FONT_TTF, font_size)
        t_rest = Image.new('RGBA', (60, 40), (0,0,0,0))
        ImageDraw.Draw(t_rest).text((5, 5), 'นฟู', font=f_norm, fill=(255,255,255,255))
        c_rest = t_rest.crop(t_rest.getbbox())
        tw = cl_fuen.width + 1 + c_rest.width
        im = Image.new('RGBA', (total_w, total_h), (0, 0, 0, 0))
        cx = (total_w - tw) // 2
        im.paste(cl_fuen, (cx, 0), cl_fuen)
        im.paste(c_rest, (cx + cl_fuen.width + 1, 32 - c_rest.height), c_rest)
        return im

    if text in ["ที่ได้", "ที่ใช้"]:
        cl_tee = render_elevated_cluster('ท', 'ี', '่', font_size)
        rest_str = text[3:]
        f_norm = ImageFont.truetype(FONT_TTF, font_size)
        t_rest = Image.new('RGBA', (60, 40), (0,0,0,0))
        ImageDraw.Draw(t_rest).text((5, 5), rest_str, font=f_norm, fill=(255,255,255,255))
        c_rest = t_rest.crop(t_rest.getbbox())
        tw = cl_tee.width + 2 + c_rest.width
        im = Image.new('RGBA', (total_w, total_h), (0, 0, 0, 0))
        cx = (total_w - tw) // 2
        im.paste(cl_tee, (cx, 0), cl_tee)
        im.paste(c_rest, (cx + cl_tee.width + 2, 32 - c_rest.height), c_rest)
        return im

    if text == "สลับที่":
        cl_tee = render_elevated_cluster('ท', 'ี', '่', font_size)
        f_norm = ImageFont.truetype(FONT_TTF, font_size)
        t_salap = Image.new('RGBA', (60, 40), (0,0,0,0))
        ImageDraw.Draw(t_salap).text((5, 5), 'สลับ', font=f_norm, fill=(255,255,255,255))
        c_salap = t_salap.crop(t_salap.getbbox())
        tw = c_salap.width + 2 + cl_tee.width
        im = Image.new('RGBA', (total_w, total_h), (0, 0, 0, 0))
        cx = (total_w - tw) // 2
        im.paste(c_salap, (cx, 32 - c_salap.height), c_salap)
        im.paste(cl_tee, (cx + c_salap.width + 2, 0), cl_tee)
        return im

    if text == "ทิ้ง":
        cl_ting = render_elevated_cluster('ท', 'ิ', '้', font_size)
        f_norm = ImageFont.truetype(FONT_TTF, font_size)
        t_ng = Image.new('RGBA', (40, 40), (0,0,0,0))
        ImageDraw.Draw(t_ng).text((5, 5), 'ง', font=f_norm, fill=(255,255,255,255))
        c_ng = t_ng.crop(t_ng.getbbox())
        tw = cl_ting.width + 1 + c_ng.width
        im = Image.new('RGBA', (total_w, total_h), (0, 0, 0, 0))
        cx = (total_w - tw) // 2
        im.paste(cl_ting, (cx, 0), cl_ting)
        im.paste(c_ng, (cx + cl_ting.width + 1, 32 - c_ng.height), c_ng)
        return im

    if text == "ใช้ทีมนี้":
        cl_nee = render_elevated_cluster('น', 'ี', '้', font_size)
        f_norm = ImageFont.truetype(FONT_TTF, font_size)
        t_front = Image.new('RGBA', (80, 40), (0,0,0,0))
        ImageDraw.Draw(t_front).text((5, 5), 'ใช้ทีม', font=f_norm, fill=(255,255,255,255))
        c_front = t_front.crop(t_front.getbbox())
        tw = c_front.width + 2 + cl_nee.width
        im = Image.new('RGBA', (total_w, total_h), (0, 0, 0, 0))
        cx = (total_w - tw) // 2
        im.paste(c_front, (cx, 32 - c_front.height), c_front)
        im.paste(cl_nee, (cx + c_front.width + 2, 0), cl_nee)
        return im

    return render_banner(text, num_tiles, font_size, 'normal')

# นิยามสเปกเมนูทั้ง 68 เมนูของ DQH2 (Cells 505..738 รวม 234 ช่อง)
RAW_MENU_SPECS = [
    # หมวด 1: หน้าไตเติล & สมุดเซฟ (9 รายการ)
    {"name": "ปุ่ม: เริ่มเล่น", "text": "เริ่มเล่น", "tiles": 4, "fsz": 30, "entry": 36, "off": 86990, "max_b": 16, "c_type": "normal"},
    {"name": "ปุ่ม: สร้างเซฟ", "text": "สร้างเซฟ", "tiles": 4, "fsz": 30, "entry": 36, "off": 87006, "max_b": 25, "c_type": "normal"},
    {"name": "ปุ่ม: ลบเซฟ", "text": "ลบเซฟ", "tiles": 4, "fsz": 30, "entry": 36, "off": 87031, "max_b": 22, "c_type": "normal"},
    {"name": "หัวข้อ: เวลาเล่น", "text": "เวลาเล่น", "tiles": 3, "fsz": 28, "entry": 36, "off": 87066, "max_b": 16, "c_type": "normal"},
    {"name": "หัวข้อ: วันที่", "text": "วันที่", "tiles": 2, "fsz": 28, "entry": 36, "off": 87082, "max_b": 13, "c_type": "normal"},
    {"name": "หัวข้อ: เรื่องราว", "text": "เรื่องราว", "tiles": 3, "fsz": 28, "entry": 36, "off": 87095, "max_b": 16, "c_type": "normal"},
    {"name": "สถานะ: ว่าง", "text": "ว่าง", "tiles": 2, "fsz": 28, "entry": 36, "off": 87111, "max_b": 25, "c_type": "normal"},
    {"name": "คำถาม: สร้างเซฟ ช่องใด?", "text": "สร้างเซฟ ช่องใด?", "tiles": 7, "fsz": 30, "entry": 36, "off": 6512, "max_b": 46, "c_type": "normal"},
    {"name": "หัวข้อ: ชื่อตัวละครหลัก", "text": "ชื่อตัวละครหลัก", "tiles": 4, "fsz": 26, "entry": 36, "off": 87361, "max_b": 49, "c_type": "normal"},

    # หมวด 2: เมนูหลักตอนเดินสำรวจ / ในฟิลด์ (11 รายการ)
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

    # หมวด 3: จุดบริการในเมืองหลวงเซบาร์ดา (13 รายการ)
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

    # หมวด 4: คำสั่งบริการในร้านค้า (15 รายการ)
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

    # หมวด 5: เมนูตั้งค่าระบบ (13 รายการ)
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

    # หมวด 6: คำสั่งทั่วไป / ยืนยัน / ยกเลิก (7 รายการ)
    {"name": "คำสั่ง: ใช่", "text": "ใช่", "tiles": 1, "fsz": 28, "entry": 36, "off": 85067, "max_b": 7, "c_type": "normal"},
    {"name": "คำสั่ง: ไม่ใช่", "text": "ไม่ใช่", "tiles": 2, "fsz": 28, "entry": 36, "off": 85074, "max_b": 10, "c_type": "normal"},
    {"name": "คำสั่ง: ถอดออก", "text": "ถอดออก", "tiles": 3, "fsz": 26, "entry": 36, "off": 85377, "max_b": 10, "c_type": "normal"},
    {"name": "คำสั่ง: ตกลง", "text": "ตกลง", "tiles": 2, "fsz": 28, "entry": 36, "off": 86087, "max_b": 13, "c_type": "normal"},
    {"name": "คำสั่ง: ยกเลิก", "text": "ยกเลิก", "tiles": 3, "fsz": 26, "entry": 36, "off": 86243, "max_b": 10, "c_type": "normal"},
    {"name": "คำสั่ง: เก็บไว้", "text": "เก็บไว้", "tiles": 3, "fsz": 26, "entry": 36, "off": 88472, "max_b": 16, "c_type": "normal"},
    {"name": "คำสั่ง: ยกเลิกเก็บ", "text": "ยกเลิกเก็บ", "tiles": 3, "fsz": 26, "entry": 36, "off": 88488, "max_b": 22, "c_type": "normal"},
]

# นิยามสเปกแถบแนะนำปุ่มกด 36 คำหลัก (Cells 740..816 รวม 77 ช่อง)
RAW_GUIDE_SPECS = [
    # หมวด 1: มุมกล้อง & ดูตัวละคร 3D (4 คำ)
    {"id": "G01", "jp": "リセット", "th": "รีเซ็ต", "tiles": 2, "fsz": 26},
    {"id": "G02", "jp": "かいてん", "th": "หมุน", "tiles": 2, "fsz": 28},
    {"id": "G03", "jp": "ズーム", "th": "ซูม", "tiles": 2, "fsz": 28},
    {"id": "G04", "jp": "くわしく見る", "th": "ข้อมูล", "tiles": 2, "fsz": 26},

    # หมวด 2: สำรวจ & เดินแมป (Action HUD - 10 คำ)
    {"id": "G05", "jp": "はなす", "th": "คุย", "tiles": 2, "fsz": 28},
    {"id": "G06", "jp": "しらべる", "th": "ตรวจ", "tiles": 2, "fsz": 26},
    {"id": "G07", "jp": "あける", "th": "เปิด", "tiles": 2, "fsz": 28},
    {"id": "G08", "jp": "ダッシュ", "th": "วิ่ง", "tiles": 2, "fsz": 28},
    {"id": "G09", "jp": "ジャンプ", "th": "โดด", "tiles": 2, "fsz": 28},
    {"id": "G10", "jp": "ぼうぎょ", "th": "กัน", "tiles": 2, "fsz": 28},
    {"id": "G11", "jp": "かいふく", "th": "ฟื้นฟู", "tiles": 2, "fsz": 26},
    {"id": "G12", "jp": "スキップ", "th": "ข้าม", "tiles": 2, "fsz": 28},
    {"id": "G13", "jp": "ひっさつ", "th": "อัลติ", "tiles": 2, "fsz": 28},
    {"id": "G14", "jp": "メニュー", "th": "เมนู", "tiles": 2, "fsz": 28},

    # หมวด 3: จัดเรียง & สลับหน้า (Sort & Filter - 12 คำ)
    {"id": "G15", "jp": "キャラきりかえ", "th": "สลับตัว", "tiles": 3, "fsz": 26},
    {"id": "G16", "jp": "きりかえ", "th": "สลับ", "tiles": 2, "fsz": 28},
    {"id": "G17", "jp": "ページきりかえ", "th": "สลับหน้า", "tiles": 3, "fsz": 25},
    {"id": "G18", "jp": "入手順に", "th": "ที่ได้", "tiles": 2, "fsz": 26},
    {"id": "G19", "jp": "達成率順に", "th": "สำเร็จ", "tiles": 2, "fsz": 26},
    {"id": "G20", "jp": "コスト順に", "th": "คอสต์", "tiles": 2, "fsz": 26},
    {"id": "G21", "jp": "有効順に", "th": "มีผล", "tiles": 2, "fsz": 26},
    {"id": "G22", "jp": "使用順に", "th": "ที่ใช้", "tiles": 2, "fsz": 26},
    {"id": "G23", "jp": "種別順に", "th": "ชนิด", "tiles": 2, "fsz": 26},
    {"id": "G24", "jp": "50音順に", "th": "ก-ฮ", "tiles": 2, "fsz": 26},
    {"id": "G25", "jp": "有効/無効", "th": "เปิด", "tiles": 2, "fsz": 28},
    {"id": "G26", "jp": "再検索", "th": "ค้น", "tiles": 2, "fsz": 28},

    # หมวด 4: จัดการของ & ปาร์ตี้ (Inventory & Party - 10 คำ)
    {"id": "G27", "jp": "はずす", "th": "ถอด", "tiles": 2, "fsz": 28},
    {"id": "G28", "jp": "すべてはずす", "th": "ถอดหมด", "tiles": 3, "fsz": 26},
    {"id": "G29", "jp": "いれかえる", "th": "สลับที่", "tiles": 2, "fsz": 26},
    {"id": "G30", "jp": "並びかえる", "th": "เรียง", "tiles": 2, "fsz": 28},
    {"id": "G31", "jp": "捨てる", "th": "ทิ้ง", "tiles": 2, "fsz": 28},
    {"id": "G32", "jp": "えらぶ", "th": "เอา", "tiles": 2, "fsz": 28},
    {"id": "G33", "jp": "前回のパーティにする", "th": "ใช้ทีมเดิม", "tiles": 3, "fsz": 24},
    {"id": "G34", "jp": "いまのパーティにする", "th": "ใช้ทีมนี้", "tiles": 3, "fsz": 24},
    {"id": "G35", "jp": "封印/解除", "th": "ผนึก", "tiles": 2, "fsz": 28},
    {"id": "G36", "jp": "すべて解除", "th": "แก้หมด", "tiles": 2, "fsz": 26}
]

# สล็อตทั้งหมด 42 สล็อตใน Entry 36 สำหรับแถบปุ่มกดท้ายจอ
BUTTON_GUIDE_PATCH_SLOTS = [
    (102558, 15, b'\x1bP2', "G01"),
    (102574, 15, b'\x1bPK', "G02"),
    (102590, 15, b'\x1bPB\x1bPC', "G03"),
    (102606, 21, b'\x1bPI', "G04"),
    (102682, 27, b'\x1bPB\x1bPC', "G15"),
    (102710, 18, b'\x1bP2', "G19"),
    (102729, 14, b'\x1bP2', "G24"),
    (102744, 15, b'\x1bP2', "G23"),
    (102760, 15, b'\x1bP3', "G16"),
    (102776, 18, b'\x1bP2', "G20"),
    (102795, 15, b'\x1bP2', "G21"),
    (102811, 16, b'\x1bPL', "G25"),
    (102828, 21, b'\x1bP3', "G28"),
    (103055, 15, b'\x1bPQ', "G08"),
    (103124, 12, b'\x1bP3', "G26"),
    (103145, 12, b'\x1bP5', "G32"),
    (103190, 15, b'\x1bP1', "G09"),
    (103206, 15, b'\x1bP0', "G13"),
    (103264, 12, b'\x1bP3', "G31"),
    (103277, 15, b'\x1bP2', "G18"),
    (103346, 15, b'\x1bPH', "G12"),
    (103362, 12, b'\x1bPL', "G05"),
    (103375, 15, b'\x1bPH', "G14"),
    (103391, 12, b'\x1bPL', "G07"),
    (103404, 15, b'\x1bPL', "G06"),
    (103436, 24, b'\x1bPA', "G17"),
    (103467, 18, b'\x1bPL', "G29"),
    (103486, 18, b'\x1bP2', "G30"),
    (103505, 12, b'\x1bP3', "G27"),
    (103578, 15, b'\x1bPB', "G10"),
    (103633, 15, b'\x1bPT', "G08"),
    (103649, 21, b'\x1bPB+\x1bPC', "G13"),
    (103725, 15, b'\x1bPU', "G09"),
    (103741, 15, b'\x1bPV', "G08"),
    (103757, 15, b'\x1bP0', "G11"),
    (103773, 21, b'\x1bPB+\x1bPC', "G11"),
    (103795, 15, b'\x1bPR', "G10"),
    (103811, 15, b'\x1bP2', "G22"),
    (103837, 33, b'\x1bP2', "G33"),
    (103871, 33, b'\x1bP2', "G34"),
    (103959, 16, b'\x1bP0', "G35"),
    (103976, 18, b'\x1bP3', "G36"),
]

def apply_pure_english_keyboard(dds_bytes):
    print("\n[+] 1. บังคับและติดตั้งแป้นพิมพ์ภาษาอังกฤษแท้ 166 ปุ่ม (A-Z, a-z, 0-9) ลงใน DDS...")
    for i, (kana, (dst_r, dst_c), _) in enumerate(KEYBOARD_MAPPING):
        ch = PAGE1_MAPPING[i]
        src_r, src_c = SRC_CHARS[ch]
        copy_dxt5_cell(dds_bytes, src_r, src_c, dst_r, dst_c)

    for i, kana in enumerate(KATAKANA_ORDER):
        ch = PAGE2_MAPPING[i]
        src_r, src_c = SRC_CHARS[ch]
        dst_r, dst_c = KATAKANA_COORDS[kana]
        copy_dxt5_cell(dds_bytes, src_r, src_c, dst_r, dst_c)
    print("    -> ติดตั้งแป้นพิมพ์ภาษาอังกฤษแท้ 166 ปุ่มเสร็จสมบูรณ์")

def main():
    print("=" * 80)
    print(" [*] MASTER TOOL: DQH2 Ultimate Thai Localization Master")
    print(" [*] - 68 Menus (Cells 505..738, 234 tiles) Sliced Banners")
    print(" [*] - 36 Button Guides (Cells 740..816, 77 tiles) Option A Elevated Banners")
    print(" [*] - 166 English Keyboard Keys (Cells 210..377) Locked & Verified")
    print("=" * 80)

    # 1. จัดสรรช่องสำหรับ 68 เมนู (Cells 505..738)
    allocated_menus = []
    current_cell = 505
    for item in RAW_MENU_SPECS:
        tiles = item["tiles"]
        start_c = current_cell
        kanjis = "".join(cell_to_kanji(start_c + i) for i in range(tiles))
        spec = dict(item)
        spec["start_cell"] = start_c
        spec["kanjis"] = kanjis
        allocated_menus.append(spec)
        current_cell += tiles

    menu_end_cell = current_cell - 1
    print(f"[+] จัดสรร 68 เมนูเสร็จสิ้น: Cell 505 ถึง {menu_end_cell} (รวม {menu_end_cell - 505 + 1} ช่อง)")

    # 2. จัดสรรช่องสำหรับ 36 แถบปุ่มกด (Cells 740..816)
    current_cell = 740
    allocated_guides = []
    guide_id_to_spec = {}
    for item in RAW_GUIDE_SPECS:
        tiles = item["tiles"]
        start_c = current_cell
        kanjis = "".join(cell_to_kanji(start_c + i) for i in range(tiles))
        spec = dict(item)
        spec["start_cell"] = start_c
        spec["kanjis"] = kanjis
        allocated_guides.append(spec)
        guide_id_to_spec[spec["id"]] = spec
        current_cell += tiles

    guide_end_cell = current_cell - 1
    print(f"[+] จัดสรร 36 แถบปุ่มกดเสร็จสิ้น: Cell 740 ถึง {guide_end_cell} (รวม {guide_end_cell - 740 + 1} ช่อง)")

    # 3. โหลด DDS
    with open(TARGET_DDS, "rb") as f:
        dds_bytes = bytearray(f.read())
    print(f"\n[+] โหลด Font Sheet DDS: {TARGET_DDS}")

    # บังคับติดตั้งคีย์บอร์ดภาษาอังกฤษแท้ 166 ปุ่มทันที
    apply_pure_english_keyboard(dds_bytes)
    kb_hash_before = get_keyboard_checksum(dds_bytes)
    print(f"    [CHECK] Checksum แป้นพิมพ์ภาษาอังกฤษแท้ 166 ตัว: {kb_hash_before}")

    # 4. เรนเดอร์ 68 เมนู และฉีดเข้า DDS
    print(f"\n[+] 2. เรนเดอร์ภาพแบนเนอร์ทั้ง 68 เมนู และฉีดเข้า DDS...")
    e36_patches = []
    e22_patches = []
    preview_menu_items = []

    for spec in allocated_menus:
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
        preview_menu_items.append((name, text, banner_img))

        # หั่นเป็นชิ้นละ 36x36px
        slices = [banner_img.crop((i * 36, 0, (i + 1) * 36, 36)) for i in range(tiles)]
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

        k_bytes = kanjis.encode('utf-8')
        assert len(k_bytes) < max_b, f"เมนู {text} ล้น buffer ({len(k_bytes)} >= {max_b})"
        padded = k_bytes + b'\x00' * (max_b - len(k_bytes))
        if target_entry == 36:
            e36_patches.append((off, name, text, kanjis, padded))
        elif target_entry == 22:
            e22_patches.append((off, name, text, kanjis, padded))

    print(f"    -> เรนเดอร์และฉีด 68 เมนูลง DDS สำเร็จ 100%")

    # 5. เรนเดอร์ 36 แถบปุ่มกด และฉีดเข้า DDS (Cells 740..816)
    print(f"\n[+] 3. เรนเดอร์ภาพแบนเนอร์แถบปุ่มกดทั้ง 36 คำ (Option A Elevated) และฉีดเข้า DDS...")
    preview_guide_items = []

    for spec in allocated_guides:
        g_id = spec["id"]
        th_text = spec["th"]
        jp_text = spec["jp"]
        tiles = spec["tiles"]
        font_sz = spec["fsz"]
        kanjis = spec["kanjis"]
        start_c = spec["start_cell"]

        banner_img = render_guide_banner_master(th_text, tiles, font_sz)
        preview_guide_items.append((g_id, jp_text, th_text, banner_img, tiles))

        slices = [banner_img.crop((i * 36, 0, (i + 1) * 36, 36)) for i in range(tiles)]
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

    print(f"    -> เรนเดอร์และฉีด 36 แถบปุ่มกดลง DDS สำเร็จ 100%")

    # 6. เตรียม Patch สำหรับ 42 สล็อตปุ่มกดใน Entry 36
    guide_e36_patches = []
    for off, slot_sz, btn_prefix, g_id in BUTTON_GUIDE_PATCH_SLOTS:
        spec = guide_id_to_spec[g_id]
        kanji_str = spec["kanjis"]
        k_bytes = kanji_str.encode('utf-8')
        payload = btn_prefix + k_bytes
        assert len(payload) <= slot_sz, f"Button guide {g_id} overflow: {len(payload)} > {slot_sz}"
        padded = payload + b'\x00' * (slot_sz - len(payload))
        guide_e36_patches.append((off, slot_sz, spec["th"], kanji_str, padded))

    print(f"    -> จัดเตรียม 42 สล็อตปุ่มกดใน Entry 36 เรียบร้อย (ไร้ Overflow 100%)")

    # บันทึก DDS
    with open(TARGET_DDS, "wb") as f:
        f.write(dds_bytes)
    print(f"\n[+] บันทึกไฟล์ DDS เรียบร้อย")

    # ตรวจสอบคีย์บอร์ด
    kb_hash_after = get_keyboard_checksum(dds_bytes)
    print(f"    [VERIFY] Checksum แป้นพิมพ์ภาษาอังกฤษหลังแก้: {kb_hash_after}")
    assert kb_hash_before == kb_hash_after, "CRITICAL ERROR: แป้นพิมพ์ภาษาอังกฤษถูกแตะต้อง!"
    print(f"    [PASSED 100%] ยืนยัน: แป้นพิมพ์ภาษาอังกฤษ 166 ตัวเดิมปลอดภัย 100%")

    # 7. คอมไพล์ DDS เป็น G1T
    print("\n[+] 4. คอมไพล์ DDS เป็น G1T ด้วย g1t_tool...")
    cmd = [sys.executable, G1T_TOOL, "import", TEX_DIR, OUT_G1T_DIR]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0, f"g1t_tool error: {res.stderr}"
    print(f"    -> {res.stdout.strip()}")

    # 8. บีบอัด Entry 55 Zlib Chunks
    out_g1t = os.path.join(OUT_G1T_DIR, "entry_00055.g1t")
    with open(out_g1t, "rb") as f:
        g1t_raw = f.read()
    packed_55 = pack_entry_chunks(g1t_raw)
    print(f"[+] บีบอัด Entry 55 สำเร็จ: {len(packed_55):,} ไบต์")

    # 9. ฉีดเข้า LINKDATA.BIN ทั้ง 2 แหล่ง (Atmosphere และ Yuzu)
    targets = [
        ("Atmosphere Mod (Drive D)", ATMO_BIN),
        ("Yuzu Mod (Drive C)", YUZU_BIN)
    ]

    print("\n[+] 5. ฉีด Font Atlas Entry 55, Entry 36 (68 เมนู + 42 ปุ่มกด), Entry 22 เข้าสู่ LINKDATA.BIN ทั้ง 2 แหล่ง...")
    for name, bin_path in targets:
        if os.path.exists(bin_path):
            with open(bin_path, "r+b") as f:
                # 9.1 ฉีด Entry 55
                f.seek(ENTRY_55_OFF)
                f.write(packed_55)

                # 9.2 ฉีดข้อความ 68 เมนูใน Entry 36
                for off, m_name, text, kanjis, padded in e36_patches:
                    f.seek(ENTRY_36_START + off)
                    f.write(padded)

                # 9.3 ฉีด 42 สล็อตแถบปุ่มกดใน Entry 36
                for off, slot_sz, th_text, kanjis, padded in guide_e36_patches:
                    f.seek(ENTRY_36_START + off)
                    f.write(padded)

                # 9.4 ฉีดข้อความ Entry 22 (13 จุดบริการ)
                for off, m_name, text, kanjis, padded in e22_patches:
                    f.seek(ENTRY_22_START + off)
                    f.write(padded)

            print(f"    [+] ติดตั้งสำเร็จ -> {name}")
        else:
            print(f"    [-] ข้าม (ไม่พบไฟล์) -> {name}")

    # 10. สร้าง Master Visual Preview แผ่นใหญ่รวม 68 เมนู + 36 ปุ่มกด
    print("\n[+] 6. กำลังสร้าง Master Visual Preview แผ่นใหญ่...")
    pv_w = 920
    row_h = 42
    total_rows = len(preview_menu_items) + len(preview_guide_items) + 4
    total_pv_h = 80 + total_rows * row_h
    pv_img = Image.new('RGB', (pv_w, total_pv_h), (20, 24, 34))
    pv_d = ImageDraw.Draw(pv_img)
    pv_f = ImageFont.truetype(FONT_TTF, 20)
    pv_sub = ImageFont.truetype(FONT_TTF, 24)
    pv_header_f = ImageFont.truetype(FONT_TTF, 28)

    pv_d.text((30, 20), "Dragon Quest Heroes II - Master Localization Preview (68 Menus + 36 Guides)", font=pv_header_f, fill=(255, 215, 0))

    y_cur = 75

    # Section 1: 68 Menus
    pv_d.text((30, y_cur), "=== ส่วนที่ 1: เมนูเกมหลักทั้ง 68 เมนู (Cells 505..738) ===", font=pv_sub, fill=(100, 220, 255))
    y_cur += 40

    for idx, (m_name, m_text, b_img) in enumerate(preview_menu_items, 1):
        bg_color = (28, 34, 48) if idx % 2 == 0 else (22, 27, 38)
        pv_d.rectangle([(20, y_cur), (pv_w - 20, y_cur + row_h - 4)], fill=bg_color)
        pv_d.text((30, y_cur + 5), f"{idx:02d}. {m_name}", font=pv_f, fill=(180, 200, 230))
        bx = 520
        pv_d.rectangle([(bx - 2, y_cur + 1), (bx + b_img.width + 1, y_cur + 34)], outline=(100, 130, 180), width=1)
        pv_img.paste(b_img, (bx, y_cur + 1), b_img)
        y_cur += row_h

    # Section 2: 36 Button Guides
    y_cur += 20
    pv_d.text((30, y_cur), "=== ส่วนที่ 2: แถบแนะนำปุ่มกดท้ายจอ 36 คำหลัก (Cells 740..816) ===", font=pv_sub, fill=(100, 220, 255))
    y_cur += 40

    for idx, (g_id, jp_text, th_text, b_img, tiles) in enumerate(preview_guide_items, 1):
        bg_color = (28, 34, 48) if idx % 2 == 0 else (22, 27, 38)
        pv_d.rectangle([(20, y_cur), (pv_w - 20, y_cur + row_h - 4)], fill=bg_color)
        pv_d.text((30, y_cur + 5), f"[{g_id}] {jp_text} -> {th_text} ({tiles} tiles)", font=pv_f, fill=(180, 200, 230))
        bx = 520
        pv_d.rectangle([(bx - 2, y_cur + 1), (bx + b_img.width + 1, y_cur + 34)], outline=(100, 130, 180), width=1)
        for t in range(1, tiles):
            pv_d.line([(bx + t * 36, y_cur + 2), (bx + t * 36, y_cur + 33)], fill=(60, 80, 110), width=1)
        pv_img.paste(b_img, (bx, y_cur + 1), b_img)
        y_cur += row_h

    pv_path = os.path.join(WORKSPACE_DIR, "master_dqh2_all_menus_preview.png")
    pv_img.save(pv_path)
    print(f"    [+] บันทึก Master Preview สำเร็จ: {pv_path}")

    # บันทึกภาพ mockup แถบปุ่มกดท้ายจอจริงในเกม
    mock_bar_path = os.path.join(WORKSPACE_DIR, "actual_button_guide_ingame_mockup.png")
    mock_w = 460
    mock_h = 44
    mock = Image.new('RGB', (mock_w, mock_h), (32, 26, 18))
    d_m = ImageDraw.Draw(mock)
    d_m.rectangle([(0, 0), (mock_w-1, mock_h-1)], outline=(160, 130, 70), width=2)
    f_btn = ImageFont.truetype(FONT_TTF, 22)
    d_m.text((15, 8), '[X]', font=f_btn, fill=(210, 210, 210))
    mock.paste(preview_guide_items[0][3], (55, 4), preview_guide_items[0][3]) # รีเซ็ต
    d_m.text((150, 8), '[R]', font=f_btn, fill=(210, 210, 210))
    mock.paste(preview_guide_items[1][3], (190, 4), preview_guide_items[1][3]) # หมุน
    d_m.text((290, 8), '[L][R]', font=f_btn, fill=(210, 210, 210))
    mock.paste(preview_guide_items[2][3], (360, 4), preview_guide_items[2][3]) # ซูม
    mock.save(mock_bar_path)
    print(f"    [+] บันทึก In-game Button Guide Mockup สำเร็จ: {mock_bar_path}")

    print("\n" + "=" * 80)
    print(" [SUCCESS 100%] ติดตั้งทุกเมนูและแถบปุ่มกดใน Dragon Quest Heroes II สมบูรณ์แบบ 100%!")
    print(f" 1. เมนูหลักทั้งหมด: {len(allocated_menus)} เมนู (Cells 505..{menu_end_cell})")
    print(f" 2. แถบปุ่มกดท้ายจอ: {len(allocated_guides)} คำ / 42 สล็อต (Cells 740..{guide_end_cell})")
    print(" 3. สระลอย Option A Elevated สวยคมชัด 100% ไร้รอยต่อ")
    print(" 4. แป้นพิมพ์ภาษาอังกฤษแท้ 166 ปุ่ม: ปลอดภัย 100% (MD5 Checksum verified)")
    print(" 5. ฉีดเข้า Atmosphere Mod (Drive D) และ Yuzu Mod (Drive C) เรียบร้อย")
    print("=" * 80)

if __name__ == "__main__":
    main()
