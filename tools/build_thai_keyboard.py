r"""
build_thai_keyboard.py
สร้างแผนภาพฟอนต์คีย์บอร์ดภาษาไทย (ก-ฮ และสระ) สำหรับ Dragon Quest Heroes II บน Nintendo Switch
โดยแทนที่ตัวอักษร Kana ใน Entry 55 (4096x2048 BC3 Font Atlas)
และคอมไพล์ลงใน D:\Game\dragon quest heroes i & ii\mod เพื่อนำไปเล่นบน Switch / Yuzu ได้ทันที
"""

import os
import sys
import struct
import zlib
import subprocess
import numpy as np
from PIL import Image, ImageFont, ImageDraw

BASE_DIR = r"D:\Game\dragon quest heroes i & ii"
SWITCH_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(SWITCH_DIR)
WORKSPACE_DIR = os.path.join(SWITCH_DIR, "workspace")
TEX_DIR = os.path.join(WORKSPACE_DIR, "tex_55")
OUT_G1T_DIR = os.path.join(WORKSPACE_DIR, "out_g1t")

FONT_TTF = os.path.join(SWITCH_DIR, "fonts", "Pridi-Bold.ttf")
G1T_TOOL = os.path.join(SWITCH_DIR, "tools", "g1t_tool.py")

def encode_cell_dxt5(cell_img):
    """
    Encode a 36x36 RGBA PIL image to 9 rows of 9 DXT5 blocks (144 bytes per row).
    Returns list of 9 byte strings, each 144 bytes (9 blocks * 16 bytes).
    """
    assert cell_img.size == (36, 36)
    arr = np.array(cell_img)
    alpha = arr[:, :, 3]
    
    color_block = b'\xff\xff\xff\xff\x00\x00\x00\x00'
    pal = np.array([255, 0, 219, 182, 146, 109, 73, 36])
    
    rows_dxt = []
    for by in range(9):
        row_bytes = bytearray(9 * 16)
        for bx in range(9):
            blk = alpha[by*4:(by+1)*4, bx*4:(bx+1)*4].flatten()
            if not blk.any():
                alpha_block = b'\x00\x00\x00\x00\x00\x00\x00\x00'
                block_data = alpha_block + color_block
            else:
                diff = np.abs(blk[:, None] - pal[None, :])
                indices = np.argmin(diff, axis=1)
                bits = 0
                for p in range(16):
                    bits |= (int(indices[p]) & 7) << (3 * p)
                alpha_block = struct.pack('<BB', 255, 0) + bits.to_bytes(6, 'little')
                block_data = alpha_block + color_block
            row_bytes[bx*16:(bx+1)*16] = block_data
        rows_dxt.append(bytes(row_bytes))
    return rows_dxt

def pack_entry_chunks(data, chunk_size=0x40000):
    """
    Koei Tecmo chunk compression (Zlib level 9) with 128-byte block alignment.
    """
    full_size = len(data)
    chunks = (full_size + chunk_size - 1) // chunk_size
    zchunks = [zlib.compress(data[i*chunk_size : (i+1)*chunk_size], 9) for i in range(chunks)]
    buf = bytearray()
    buf.extend(struct.pack('<III', chunk_size, chunks, full_size))
    for z in zchunks:
        buf.extend(struct.pack('<I', 4 + len(z)))
    padding_offset = 0
    for z in zchunks:
        pos = len(buf)
        pad = (128 - ((pos - padding_offset) % 128)) % 128
        buf.extend(b'\x00' * pad)
        padding_offset = len(buf)
        buf.extend(struct.pack('<I', len(z)))
        buf.extend(z)
    return bytes(buf)

ORIG_DDS = os.path.join(TEX_DIR, "entry_00055.TEX0.dxt5.dds")
ORIG_G1T = os.path.join(TEX_DIR, "entry_00055.g1t")

TITLE_ID = "0100CD3000BDC000"
MOD_DIR = os.path.join(BASE_DIR, "mod", "atmosphere", "contents", TITLE_ID, "romfs", "dqh2")
MOD_BIN = os.path.join(MOD_DIR, "LINKDATA.BIN")
MOD_IDX = os.path.join(MOD_DIR, "LINKDATA.IDX")

CELL_SIZE = 36
FONT_SIZE = 28
TARGET_BASELINE = 30

WIDTH_BLOCKS = 4096 // 4  # 1024
BLOCK_BYTES = 16

ENTRY_55_ID = 55
ENTRY_55_OFF = 4805120
ENTRY_55_ZSZ = 1106944

# ผังการจับคู่ 83 ปุ่มคีย์บอร์ดในเกม
KEYBOARD_MAPPING = [
    # --- บล็อกซ้าย (30 ปุ่ม): พยัญชนะไทย ก - พ ---
    # แถว 0
    ('あ', (1,  97), 'ก'),
    ('い', (1,  99), 'ข'),
    ('う', (1, 101), 'ฃ'),
    ('え', (1, 103), 'ค'),
    ('お', (1, 105), 'ฅ'),
    # แถว 1
    ('か', (1, 106), 'ฆ'),
    ('き', (1, 108), 'ง'),
    ('く', (1, 110), 'จ'),
    ('け', (1, 112), 'ฉ'),
    ('こ', (2,   1), 'ช'),
    # แถว 2
    ('さ', (2,   3), 'ซ'),
    ('し', (2,   5), 'ฌ'),
    ('す', (2,   7), 'ญ'),
    ('せ', (2,   9), 'ฎ'),
    ('そ', (2,  11), 'ฏ'),
    # แถว 3
    ('た', (2,  13), 'ฐ'),
    ('ち', (2,  15), 'ฑ'),
    ('つ', (2,  18), 'ฒ'),
    ('て', (2,  20), 'ณ'),
    ('と', (2,  22), 'ด'),
    # แถว 4
    ('な', (2,  24), 'ต'),
    ('に', (2,  25), 'ถ'),
    ('ぬ', (2,  26), 'ท'),
    ('ね', (2,  27), 'ธ'),
    ('の', (2,  28), 'น'),
    # แถว 5
    ('ぁ', (1,  96), 'บ'),
    ('ぃ', (1,  98), 'ป'),
    ('ぅ', (1, 100), 'ผ'),
    ('ぇ', (1, 102), 'ฝ'),
    ('ぉ', (1, 104), 'พ'),

    # --- บล็อกกลาง (28 ปุ่ม): พยัญชนะไทย ฟ - ฮ + สระแนวบรรทัด ---
    # แถว 0
    ('は', (2,  29), 'ฟ'),
    ('ひ', (2,  32), 'ภ'),
    ('ふ', (2,  35), 'ม'),
    ('へ', (2,  38), 'ย'),
    ('ほ', (2,  41), 'ร'),
    # แถว 1
    ('ま', (2,  44), 'ล'),
    ('み', (2,  45), 'ว'),
    ('む', (2,  46), 'ศ'),
    ('め', (2,  47), 'ษ'),
    ('も', (2,  48), 'ส'),
    # แถว 2
    ('や', (2,  50), 'ห'),
    ('ゆ', (2,  52), 'ฬ'),
    ('よ', (2,  54), 'อ'),
    ('わ', (2,  61), 'ฮ'),
    ('ん', (2,  65), 'ะ'),
    # แถว 3
    ('ら', (2,  55), 'า'),
    ('り', (2,  56), 'ำ'),
    ('る', (2,  57), 'เ'),
    ('れ', (2,  58), 'แ'),
    ('ろ', (2,  59), 'โ'),
    # แถว 4
    ('ゃ', (2,  49), 'ใ'),
    ('ゅ', (2,  51), 'ไ'),
    ('ょ', (2,  53), 'ฤ'),
    ('っ', (2,  17), 'ฦ'),
    ('を', (2,  64), 'ๆ'),
    # แถว 5
    ('ー', (0,  27), '-'),
    ('～', (0,  32), '~'),
    ('・', (0,   2), '.'),

    # --- บล็อกขวา (25 ปุ่ม): สระบน-ล่าง วรรณยุกต์ และตัวเลข 0-9 ---
    # แถว 0
    ('が', (1, 107), 'ิ'),
    ('ぎ', (1, 109), 'ี'),
    ('ぐ', (1, 111), 'ึ'),
    ('げ', (2,   0), 'ื'),
    ('ご', (2,   2), 'ุ'),
    # แถว 1
    ('ざ', (2,   4), 'ู'),
    ('じ', (2,   6), 'ฺ'),
    ('ず', (2,   8), 'ั'),
    ('ぜ', (2,  10), '็'),
    ('ぞ', (2,  12), '์'),
    # แถว 2
    ('だ', (2,  14), '่'),
    ('ぢ', (2,  16), '้'),
    ('づ', (2,  19), '๊'),
    ('で', (2,  21), '๋'),
    ('ど', (2,  23), 'ํ'),
    # แถว 3
    ('ば', (2,  30), '0'),
    ('び', (2,  33), '1'),
    ('ぶ', (2,  36), '2'),
    ('べ', (2,  39), '3'),
    ('ぼ', (2,  42), '4'),
    # แถว 4
    ('ぱ', (2,  31), '5'),
    ('ぴ', (2,  34), '6'),
    ('ぷ', (2,  37), '7'),
    ('ぺ', (2,  40), '8'),
    ('ぽ', (2,  43), '9'),
]

def render_thai_char(font, ch):
    """เรนเดอร์ตัวอักษรไทย 1 ตัวลงในกรอบ 36x36"""
    cell = Image.new('RGBA', (CELL_SIZE, CELL_SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(cell)
    
    upper_marks = ['ิ', 'ี', 'ึ', 'ื', '่', '้', '๊', '๋', '์', '็', 'ั', 'ํ']
    lower_marks = ['ุ', 'ู', 'ฺ']
    
    if ch in upper_marks:
        f_mark = ImageFont.truetype(FONT_TTF, 30)
        temp = Image.new('RGBA', (50, 50), (0, 0, 0, 0))
        dt = ImageDraw.Draw(temp)
        dt.text((25, 25), ch, font=f_mark, fill=(255, 255, 255, 255), anchor='mm')
        
        arr = np.array(temp)[:, :, 3]
        coords = np.argwhere(arr > 20)
        if len(coords) > 0:
            min_y, min_x = coords.min(axis=0)
            max_y, max_x = coords.max(axis=0)
            crop_mark = temp.crop((min_x, min_y, max_x + 1, max_y + 1))
            cx = (CELL_SIZE - crop_mark.width) // 2
            cy = max(2, (CELL_SIZE - crop_mark.height) // 2 - 2)
            cell.paste(crop_mark, (cx, cy), crop_mark)
        else:
            d.text((18, TARGET_BASELINE), ch, font=font, fill=(255, 255, 255, 255), anchor='ms')
    elif ch in lower_marks:
        f_mark = ImageFont.truetype(FONT_TTF, 30)
        temp = Image.new('RGBA', (50, 50), (0, 0, 0, 0))
        dt = ImageDraw.Draw(temp)
        dt.text((25, 25), ch, font=f_mark, fill=(255, 255, 255, 255), anchor='mm')
        arr = np.array(temp)[:, :, 3]
        coords = np.argwhere(arr > 20)
        if len(coords) > 0:
            min_y, min_x = coords.min(axis=0)
            max_y, max_x = coords.max(axis=0)
            crop_mark = temp.crop((min_x, min_y, max_x + 1, max_y + 1))
            cx = (CELL_SIZE - crop_mark.width) // 2
            cy = max(2, (CELL_SIZE - crop_mark.height) // 2 + 2)
            cell.paste(crop_mark, (cx, cy), crop_mark)
        else:
            d.text((18, TARGET_BASELINE), ch, font=font, fill=(255, 255, 255, 255), anchor='ms')
    else:
        d.text((18, TARGET_BASELINE), ch, font=font, fill=(255, 255, 255, 255), anchor='ms')
        
    return cell

def patch_dds():
    print(f"[*] Reading original DDS texture: {ORIG_DDS}...")
    with open(ORIG_DDS, "rb") as f:
        dds_bytes = bytearray(f.read())
        
    font = ImageFont.truetype(FONT_TTF, FONT_SIZE)
    print(f"[*] Encoding and patching {len(KEYBOARD_MAPPING)} Thai glyph cells into DDS...")
    
    for key_char, (row, col), thai_char in KEYBOARD_MAPPING:
        cell_img = render_thai_char(font, thai_char)
        rows_dxt = encode_cell_dxt5(cell_img)
        
        by0 = row * 9
        bx0 = col * 9
        
        for by in range(9):
            offset = 128 + ((by0 + by) * WIDTH_BLOCKS + bx0) * BLOCK_BYTES
            dds_bytes[offset : offset + 144] = rows_dxt[by]
            
    with open(ORIG_DDS, "wb") as f:
        f.write(dds_bytes)
    print(f"[+] Successfully patched DDS in-place: {ORIG_DDS}")

def import_g1t():
    print("[*] Re-importing patched DDS into G1T using g1t_tool...")
    os.makedirs(OUT_G1T_DIR, exist_ok=True)
    cmd = [sys.executable, G1T_TOOL, "import", TEX_DIR, OUT_G1T_DIR]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0, f"g1t_tool import failed: {res.stderr}"
    print(f"[+] {res.stdout.strip()}")
    
    out_g1t_file = os.path.join(OUT_G1T_DIR, "entry_00055.g1t")
    assert os.path.exists(out_g1t_file), "G1T file not produced!"
    return out_g1t_file

def inject_mod(g1t_file):
    print(f"[*] Reading Entry {ENTRY_55_ID} offset & size from {MOD_IDX}...")
    with open(MOD_IDX, "rb") as f_idx:
        f_idx.seek(ENTRY_55_ID * 32)
        idx_off, idx_sz, idx_zsz, idx_comp = struct.unpack("<QQQQ", f_idx.read(32))
    print(f"[*] Entry {ENTRY_55_ID} in IDX: Offset={idx_off:,}, Original Size={idx_sz:,}, Slot Limit={idx_zsz:,}")
    
    print(f"[*] Compressing Entry 55 with Koei Tecmo Chunk Compression (Zlib lvl 9)...")
    with open(g1t_file, "rb") as f:
        g1t_raw = f.read()
        
    packed = pack_entry_chunks(g1t_raw)
    print(f"[+] Packed Entry 55 size: {len(packed):,} bytes (Slot limit: {idx_zsz:,} bytes)")
    assert len(packed) <= idx_zsz, f"Error: Packed size exceeds slot limit ({len(packed)} > {idx_zsz})"
    
    print(f"[*] Injecting packed Entry 55 into modded LINKDATA.BIN...")
    assert os.path.exists(MOD_BIN), f"MOD LINKDATA.BIN not found at {MOD_BIN}!"
    
    # เขียนทับลงใน Offset เดิมของ Entry 55
    pad_bytes = b'\x00' * (idx_zsz - len(packed))
    full_payload = packed + pad_bytes
    assert len(full_payload) == idx_zsz
    
    with open(MOD_BIN, "r+b") as f:
        f.seek(idx_off)
        f.write(full_payload)
        
    print(f"[+] Successfully injected Entry 55 into {MOD_BIN} at offset {idx_off}!")

def main():
    print("=================================================================")
    print("[*] Switch Dragon Quest Heroes II - Thai Keyboard Mod Pipeline")
    print("=================================================================")
    patch_dds()
    out_g1t = import_g1t()
    inject_mod(out_g1t)
    print("=================================================================")
    print("[+] COMPLETE! Thai Keyboard Mod is ready in:")
    print(f"    {MOD_DIR}")
    print("=================================================================")

if __name__ == "__main__":
    main()
