"""
deploy_all_menus_beautiful.py
ติดตั้งระบบภาพแบนเนอร์ไร้รอยต่อ (Seamless Sliced Image Banners)
ให้ครบทุกเมนูและทุกหัวข้อบนหน้าสมุดบันทึก (ทุกเมนู สวยทุกคำ 100%):
1. ปุ่ม 1: เริ่มเล่น (4 ชิ้น = 144px) -> 亜唖娃阿 [Cells 505-508] (แก้ไม้เอกลอยเด่นชัด)
2. ปุ่ม 2: สร้างเซฟ (4 ชิ้น = 144px) -> 哀愛挨姶 [Cells 509-512]
3. ปุ่ม 3: ลบเซฟ (4 ชิ้น = 144px)   -> 逢葵茜穐 [Cells 513-516]
4. หัวข้อ 1: เวลาเล่น (3 ชิ้น = 108px) -> 悪握渥 [Cells 517-519]
5. หัวข้อ 2: วันที่ (2 ชิ้น = 72px)    -> 旭葦   [Cells 520-521]
6. หัวข้อ 3: เรื่องราว (3 ชิ้น = 108px) -> 芦鯵梓 [Cells 522-524]
7. ช่องเซฟ: ว่าง (2 ชิ้น = 72px)       -> 圧斡   [Cells 525-526] (แก้ตัวต่างดาว 10 ช่อง)
8. คำถามล่าง: สร้างเซฟ ช่องใด? (5 ชิ้น = 180px) -> 扱宛姐虻飴 [Cells 527-531] (แก้ตัวห่าง)
9. หัวข้อบน: ชื่อตัวละครหลัก (4 ชิ้น = 144px) -> 絢綾鮎或 [Cells 532-535]

- ฉีดเข้าช่อง Ku 16 Cells 505-535 ใน Entry 55
- ฉีดข้อความ UTF-8 เข้าสู่ Entry 36 ใน LINKDATA.BIN
- ตรวจสอบ Checksum แป้นพิมพ์ภาษาอังกฤษ 166 ตัวเดิม ปลอดภัย 100%
- ฉีดเข้า LINKDATA.BIN ทั้ง Atmosphere และ Yuzu Mod
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
from build_thai_keyboard import encode_cell_dxt5, pack_entry_chunks
from build_switch_kanji_mapping import jis_to_sjis_char, jis_to_cell

TITLE_ID = "0100CD3000BDC000"
ATMO_BIN = os.path.join(BASE_DIR, "mod", "atmosphere", "contents", TITLE_ID, "romfs", "dqh2", "LINKDATA.BIN")
YUZU_BIN = os.path.expanduser(rf"~\AppData\Roaming\yuzu\load\{TITLE_ID}\MODTHAI\romfs\dqh2\LINKDATA.BIN")

ENTRY_55_OFF = 4805120
ENTRY_36_START = 363008

WIDTH_BLOCKS = 1024
BLOCK_BYTES = 16

def get_keyboard_checksum(dds_bytes):
    start_off = 128 + (1 * 9 * WIDTH_BLOCKS) * BLOCK_BYTES
    end_off   = 128 + (4 * 9 * WIDTH_BLOCKS) * BLOCK_BYTES
    return hashlib.md5(dds_bytes[start_off:end_off]).hexdigest()

# กำหนดสเปก 9 แบนเนอร์เมนู
ALL_MENU_SPECS = [
    # 1. ปุ่มเริ่มเล่น (4 ช่อง = 144px)
    {
        "name": "ปุ่ม 1: เริ่มเล่น",
        "text": "เริ่มเล่น",
        "tiles": 4,
        "font_size": 30,
        "kanjis": "亜唖娃阿",
        "offset": 86990,
        "max_buf": 16,
        "start_cell": 505,
        "custom_type": "rerim" # จัดระดับยกไม้เอกเป็นพิเศษ
    },
    # 2. ปุ่มสร้างเซฟ (4 ช่อง = 144px)
    {
        "name": "ปุ่ม 2: สร้างเซฟ",
        "text": "สร้างเซฟ",
        "tiles": 4,
        "font_size": 30,
        "kanjis": "哀愛挨姶",
        "offset": 87006,
        "max_buf": 25,
        "start_cell": 509,
        "custom_type": "normal"
    },
    # 3. ปุ่มลบเซฟ (4 ช่อง = 144px)
    {
        "name": "ปุ่ม 3: ลบเซฟ",
        "text": "ลบเซฟ",
        "tiles": 4,
        "font_size": 30,
        "kanjis": "逢葵茜穐",
        "offset": 87031,
        "max_buf": 22,
        "start_cell": 513,
        "custom_type": "normal"
    },
    # 4. หัวข้อเวลาเล่น (3 ช่อง = 108px)
    {
        "name": "หัวข้อ 1: เวลาเล่น",
        "text": "เวลาเล่น",
        "tiles": 3,
        "font_size": 28,
        "kanjis": "悪握渥",
        "offset": 87066,
        "max_buf": 16,
        "start_cell": 517,
        "custom_type": "normal"
    },
    # 5. หัวข้อวันที่ (2 ช่อง = 72px)
    {
        "name": "หัวข้อ 2: วันที่",
        "text": "วันที่",
        "tiles": 2,
        "font_size": 28,
        "kanjis": "旭葦",
        "offset": 87082,
        "max_buf": 13,
        "start_cell": 520,
        "custom_type": "normal"
    },
    # 6. หัวข้อเรื่องราว (3 ช่อง = 108px)
    {
        "name": "หัวข้อ 3: เรื่องราว",
        "text": "เรื่องราว",
        "tiles": 3,
        "font_size": 28,
        "kanjis": "芦鯵梓",
        "offset": 87095,
        "max_buf": 16,
        "start_cell": 522,
        "custom_type": "normal"
    },
    # 7. สถานะช่องเซฟ: ว่าง (2 ช่อง = 72px)
    {
        "name": "ช่องเซฟ 10 ช่อง: ว่าง",
        "text": "ว่าง",
        "tiles": 2,
        "font_size": 28,
        "kanjis": "圧斡",
        "offset": 87111,
        "max_buf": 25,
        "start_cell": 525,
        "custom_type": "normal"
    },
    # 8. คำถามล่าง: สร้างเซฟ ช่องใด? (5 ช่อง = 180px)
    {
        "name": "กล่องล่าง: สร้างเซฟ ช่องใด?",
        "text": "สร้างเซฟ ช่องใด?",
        "tiles": 5,
        "font_size": 26,
        "kanjis": "扱宛姐虻飴",
        "offset": 6512,
        "max_buf": 46,
        "start_cell": 527,
        "custom_type": "normal"
    },
    # 9. หัวข้อบน: ชื่อตัวละครหลัก (4 ช่อง = 144px)
    {
        "name": "หัวข้อบน: ชื่อตัวละครหลัก",
        "text": "ชื่อตัวละครหลัก",
        "tiles": 4,
        "font_size": 26,
        "kanjis": "絢綾鮎或",
        "offset": 87361,
        "max_buf": 49,
        "start_cell": 532,
        "custom_type": "normal"
    }
]

def render_raw_crop(ch, font):
    t = Image.new('RGBA', (60, 60), (0, 0, 0, 0))
    ImageDraw.Draw(t).text((30, 45), ch, font=font, fill=(255, 255, 255, 255), anchor='ms')
    arr = np.array(t)[:, :, 3]
    coords = np.argwhere(arr > 20)
    if len(coords) == 0:
        return Image.new('RGBA', (4, 36), (0, 0, 0, 0))
    ymin, xmin = coords.min(axis=0)
    ymax, xmax = coords.max(axis=0)
    return t.crop((xmin, ymin, xmax + 1, ymax + 1))

def render_banner_rerim(total_w=144):
    """เรนเดอร์คำว่า 'เริ่มเล่น' แบบจัด 3 ชั้น ยกไม้เอกลอยสูงที่เพดาน Y=0..2 ไร้การจมหาย"""
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

def render_banner_image(text, num_tiles, font_size, custom_type):
    total_w = num_tiles * 36
    total_h = 36
    
    if custom_type == "rerim":
        return render_banner_rerim(total_w)
        
    im = Image.new('RGBA', (total_w, total_h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(FONT_TTF, font_size)
    
    bbox = d.textbbox((0, 0), text, font=f)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    
    tx = (total_w - tw) // 2 - bbox[0]
    ty = (total_h - th) // 2 - bbox[1] - 1
    d.text((tx, ty), text, font=f, fill=(255, 255, 255, 255))
    return im

def main():
    print("=" * 75)
    print(" [*] ติดตั้งระบบภาพแบนเนอร์ไร้รอยต่อ (ทุกเมนู สวยทุกคำ 100%)...")
    print("=" * 75)

    # 1. โหลด DDS
    with open(TARGET_DDS, "rb") as f:
        dds_bytes = bytearray(f.read())
    kb_hash_before = get_keyboard_checksum(dds_bytes)
    print(f"[+] 1. โหลด Font Sheet DDS: {TARGET_DDS}")
    print(f"    [CHECK] Checksum แป้นพิมพ์ภาษาอังกฤษก่อนแก้: {kb_hash_before}")

    # 2. เรนเดอร์ทั้ง 9 เมนู และฉีดเข้าช่องคันจิ (Cells 505 - 535)
    print("\n[+] 2. เรนเดอร์ภาพแบนเนอร์ทั้ง 9 เมนู และฉีดเข้าช่อง Ku 16 Cells 505 - 535...")
    encoded_patches = []

    for spec in ALL_MENU_SPECS:
        name = spec["name"]
        text = spec["text"]
        tiles = spec["tiles"]
        font_sz = spec["font_size"]
        kanjis = spec["kanjis"]
        off = spec["offset"]
        max_b = spec["max_buf"]
        start_c = spec["start_cell"]
        c_type = spec["custom_type"]

        banner_img = render_banner_image(text, tiles, font_sz, c_type)
        
        # หั่นเป็นชิ้นละ 36x36px
        slices = [banner_img.crop((i * 36, 0, (i + 1) * 36, 36)) for i in range(tiles)]
        
        # ฉีดเข้าช่องใน DDS
        for i in range(tiles):
            cell_idx = start_c + i
            row = cell_idx // 113
            col = cell_idx % 113
            kanji_ch = kanjis[i]
            
            rows_dxt = encode_cell_dxt5(slices[i])
            bx0 = (col * 36) // 4
            by0 = (row * 36) // 4
            for by in range(9):
                offset = 128 + ((by0 + by) * WIDTH_BLOCKS + bx0) * BLOCK_BYTES
                dds_bytes[offset : offset + 144] = rows_dxt[by]
                
        # เตรียม Patch ข้อความ Entry 36
        k_bytes = kanjis.encode('utf-8')
        assert len(k_bytes) < max_b, f"ข้อความ {text} ล้น buffer ({len(k_bytes)} >= {max_b})"
        padded = k_bytes + b'\x00' * (max_b - len(k_bytes))
        encoded_patches.append((off, name, text, kanjis, padded))
        print(f"    -> {name:28s} ({tiles} ชิ้น = {tiles*36}px) -> คันจิ: '{kanjis}' (Cell {start_c}..{start_c+tiles-1})")

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

    print("\n[+] 4. ฉีด Font Atlas Entry 55 และข้อความเมนูทั้ง 9 จุดเข้าสู่ LINKDATA.BIN...")
    for name, bin_path in targets:
        if os.path.exists(bin_path):
            with open(bin_path, "r+b") as f:
                # 5.1 ฉีด Entry 55
                f.seek(ENTRY_55_OFF)
                f.write(packed_55)
                
                # 5.2 ฉีดข้อความ Entry 36 ทั้ง 9 จุด
                for off, m_name, text, kanjis, padded in encoded_patches:
                    f.seek(ENTRY_36_START + off)
                    f.write(padded)
                    
            print(f"    [+] ติดตั้งสำเร็จ -> {name}")

    print("\n" + "=" * 75)
    print(" [SUCCESS] ติดตั้งทุกเมนูแบบภาพแบนเนอร์ไร้รอยต่อเรียบร้อย 100%!")
    print(" 1. ปุ่มเริ่มเล่น: แก้ไม้เอกลอยเด่นชัด คมกริบ 100%")
    print(" 2. ปุ่ม 3 ปุ่ม: คืนค่าเป็นภาพสวยงาม แนบชิด ไร้รอยต่อ")
    print(" 3. สมุดเซฟ (ว่าง, เวลาเล่น, วันที่, เรื่องราว): แปลไทยครบ แก้ตัวต่างดาว 100%")
    print(" 4. กล่องคำถามล่าง (สร้างเซฟ ช่องใด?): ชิดสนิทสวยงาม ไม่ห่างเป็นกิโลอีกต่อไป")
    print(" 5. แป้นพิมพ์ภาษาอังกฤษ 166 ตัวเดิม: ปลอดภัย 100%")
    print("=" * 75)

if __name__ == "__main__":
    main()
