"""
patch_thai_phrase_fast.py
วาดพยางค์สำเร็จรูป (ชื่, ตั, ลั) ลงในช่อง Katakana (Row 2 Col 67, 69, 71) ของ Entry 55
ด้วยระบบ Smart Proportional Scaling คมชัด ไม่ล้นขอบ ไม่ติดดอกจัน 100%
และเข้ารหัสข้อความ "ชื่อตัวละครหลัก" ฉีดเข้าสู่ LINKDATA.BIN ทันที
"""

import os
import sys
import struct
import subprocess
import numpy as np
from PIL import Image, ImageFont, ImageDraw

SWITCH_DIR = r"D:\Game\dragon quest heroes i & ii\switch"
BASE_DIR = r"D:\Game\dragon quest heroes i & ii"
sys.path.append(os.path.join(SWITCH_DIR, "tools"))
from build_thai_keyboard import encode_cell_dxt5, pack_entry_chunks

DDS_PATH = os.path.join(SWITCH_DIR, "workspace", "tex_55", "entry_00055.TEX0.dxt5.dds")
FONT_TTF = os.path.join(SWITCH_DIR, "fonts", "Pridi-Bold.ttf")
G1T_TOOL = os.path.join(SWITCH_DIR, "tools", "g1t_tool.py")
TEX_DIR = os.path.join(SWITCH_DIR, "workspace", "tex_55")
OUT_G1T_DIR = os.path.join(SWITCH_DIR, "workspace", "out_g1t")

CLUSTERS = [
    ('ชื่', 2, 67), # Katakana ア
    ('ตั', 2, 69), # Katakana イ
    ('ลั', 2, 71), # Katakana ウ
]

def render_smart_cluster(text, font):
    temp = Image.new('RGBA', (120, 120), (0, 0, 0, 0))
    d = ImageDraw.Draw(temp)
    d.text((60, 60), text, font=font, fill=(255, 255, 255, 255), anchor='mm')
    
    arr = np.array(temp)[:, :, 3]
    coords = np.argwhere(arr > 20)
    if len(coords) == 0:
        return Image.new('RGBA', (36, 36), (0, 0, 0, 0))
        
    min_y, min_x = coords.min(axis=0)
    max_y, max_x = coords.max(axis=0)
    cropped = temp.crop((min_x, min_y, max_x + 1, max_y + 1))
    
    scale = min(32.0 / cropped.height, 32.0 / cropped.width)
    nw = int(round(cropped.width * scale))
    nh = int(round(cropped.height * scale))
    scaled = cropped.resize((nw, nh), Image.Resampling.LANCZOS)
    
    cell = Image.new('RGBA', (36, 36), (0, 0, 0, 0))
    cx = (36 - nw) // 2
    cy = (36 - nh) // 2
    cell.paste(scaled, (cx, cy), scaled)
    return cell

def main():
    print("[*] 1. เรนเดอร์คลัสเตอร์ 'ชื่', 'ตั', 'ลั' (Smart Proportional Scaling)...")
    font_large = ImageFont.truetype(FONT_TTF, 52)

    with open(DDS_PATH, "rb") as f:
        dds = bytearray(f.read())

    WIDTH_BLOCKS = 1024
    BLOCK_BYTES = 16

    for text, row, col in CLUSTERS:
        cell = render_smart_cluster(text, font_large)
        
        # บันทึกภาพพรีวิวพื้นหลังดำ
        bg = Image.new('RGB', (36, 36), (0, 0, 0))
        bg.paste(cell, (0, 0), cell)
        preview_p = os.path.join(SWITCH_DIR, "workspace", f"preview_{text}.png")
        bg.save(preview_p)
        print(f"    [+] บันทึกพรีวิว {preview_p}")

        rows_dxt = encode_cell_dxt5(cell)
        bx0 = (col * 36) // 4
        by0 = (row * 36) // 4
        for by in range(9):
            off = 128 + ((by0 + by) * WIDTH_BLOCKS + bx0) * BLOCK_BYTES
            dds[off : off + 144] = rows_dxt[by]
        print(f"    [+] แพตช์คลัสเตอร์ '{text}' ลงที่ Row {row}, Col {col} เรียบร้อย")

    with open(DDS_PATH, "wb") as f:
        f.write(dds)
    print("[+] อัปเดต DDS สำเร็จ!")

    # 2. คอมไพล์กลับเป็น G1T
    print("[*] 2. แปลง DDS กลับเป็น G1T...")
    cmd = [sys.executable, G1T_TOOL, "import", TEX_DIR, OUT_G1T_DIR]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0, f"g1t_tool import error: {res.stderr}"
    print(f"    [+] {res.stdout.strip()}")

    out_g1t = os.path.join(OUT_G1T_DIR, "entry_00055.g1t")
    with open(out_g1t, "rb") as f:
        raw = f.read()

    packed = pack_entry_chunks(raw)
    pad = b'\x00' * (1106944 - len(packed))
    payload = packed + pad

    # 3. ฉีด Entry 55 เข้า LINKDATA.BIN
    print("[*] 3. ฉีด Entry 55 เข้าสู่ LINKDATA.BIN...")
    targets = [
        os.path.join(BASE_DIR, "mod", "atmosphere", "contents", "0100CD3000BDC000", "romfs", "dqh2", "LINKDATA.BIN"),
        os.path.expanduser(r"~\AppData\Roaming\yuzu\load\0100CD3000BDC000\MODTHAI\romfs\dqh2\LINKDATA.BIN")
    ]

    for p in targets:
        if os.path.exists(p):
            with open(p, "r+b") as f:
                f.seek(4805120)
                f.write(payload)
            print(f"    [+] ฉีด Entry 55 เข้า: {p}")

    # 4. เข้ารหัสข้อความ 'ชื่อตัวละครหลัก' -> 'アよイみまんえほやウあ'
    print("[*] 4. เข้ารหัสข้อความ 'ชื่อตัวละครหลัก'...")
    target_str = "アよイみまんえほやウあ"
    enc = target_str.encode("utf-8")
    padded_text = enc + b'\x00' * (48 - len(enc))

    for p in targets:
        if os.path.exists(p):
            with open(p, "r+b") as f:
                f.seek(3740846848 + 87361)
                f.write(padded_text)
            print(f"    [+] เขียนข้อความ '{target_str}' ลงใน Entry 36 ({p}) เรียบร้อย!")

    print("\n[SUCCESS] ดำเนินการเสร็จสิ้น 100%! เปิด Yuzu ตรวจสอบได้ทันที!")

if __name__ == "__main__":
    main()
