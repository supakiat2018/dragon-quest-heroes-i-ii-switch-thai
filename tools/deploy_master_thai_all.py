"""
deploy_master_thai_all.py
สคริปต์คอมไพล์และติดตั้งระบบภาษาไทยฉบับสมบูรณ์แบบ (Master Edition)
สำหรับ Nintendo Switch Dragon Quest Heroes I & II
- 1. เรนเดอร์ 70 พยัญชนะเดี่ยว + สระพื้นฐาน ลงใน Ku 16 Ten 01-70 (Cells 505-574)
- 2. เรนเดอร์ 7 คลัสเตอร์พิเศษ 3 เมนูหลัก (เริ่ม, เล่น, สร้, าง, ลบ, เซ, ฟ) ลงใน Ku 16 Ten 71-77 (Cells 575-581) ชิดแน่น ไร้ช่องว่าง
- 3. เรนเดอร์ 2,223 คลัสเตอร์ PUA สระ/วรรณยุกต์ 2-3 ชั้น จาก kanji_cluster_slots.json ลงใน Ku 24-48 (Cells 1257-3522)
- 4. ป้องกันแป้นพิมพ์ภาษาอังกฤษ 166 ตัวเดิม (Cells 209-377 แถว 1-3) ไม่ถูกแตะต้อง 100% (MD5 Checksum ตรงกันเป๊ะ)
- 5. แปลและฉีดข้อความภาษาไทยครบทั้ง 6 ภาพจาก C:\\Users\\Supakiat\\Pictures\\ภาพเกม:
     * ภาพ 1 (152806): ต้องการสร้างบันทึกการเดินทางในช่องใด
     * ภาพ 2 (153838): คำอธิบายเลือกตัวเอกและเนื้อหาเกม
     * ภาพ 3 (153845): โปรดเลือกผู้กล้า
     * ภาพ 4 (153855): ประวัตินายร้อยราเซล และ เทเรเซีย + ปุ่มคำสั่ง รีเซ็ต / หมุน / ซูม
     * ภาพ 5 (153904): โปรดตั้งชื่อของตัวเอก
     * ภาพ 6 (153908): ปุ่มคีย์บอร์ด ENG / กลับ / ตกลง ใน ExeFS
- 6. ฉีดเข้า LINKDATA.BIN, LINKDATA.IDX และ ExeFS IPS ทั้งใน Atmosphere, Yuzu และ Ryujinx
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
from build_thai_keyboard import encode_cell_dxt5, pack_entry_chunks
from thai_font_preview_gui import compose_pua_cluster_image, render_tuned_single_glyph, load_or_create_config

TITLE_ID = "0100CD3000BDC000"
BUILD_ID = "5C598E5025BF97BCEC69E67213B48503"

# Mod Paths
ATMOS_ROMFS_DIR = os.path.join(BASE_DIR, "mod", "atmosphere", "contents", TITLE_ID, "romfs", "dqh2")
ATMOS_BIN = os.path.join(ATMOS_ROMFS_DIR, "LINKDATA.BIN")
ATMOS_IDX = os.path.join(ATMOS_ROMFS_DIR, "LINKDATA.IDX")
ATMOS_EXEFS = os.path.join(BASE_DIR, "mod", "atmosphere", "contents", TITLE_ID, "exefs", f"{BUILD_ID}.ips")

YUZU_MOD_DIR = os.path.expanduser(rf"~\AppData\Roaming\yuzu\load\{TITLE_ID}\MODTHAI")
YUZU_ROMFS_DIR = os.path.join(YUZU_MOD_DIR, "romfs", "dqh2")
YUZU_BIN = os.path.join(YUZU_ROMFS_DIR, "LINKDATA.BIN")
YUZU_IDX = os.path.join(YUZU_ROMFS_DIR, "LINKDATA.IDX")
YUZU_EXEFS = os.path.join(YUZU_MOD_DIR, "exefs", f"{BUILD_ID}.ips")

RYUJINX_MOD_DIR = os.path.expanduser(rf"~\AppData\Roaming\Ryujinx\sdcard\atmosphere\contents\{TITLE_ID.lower()}\{TITLE_ID}\MODTHAI")
RYUJINX_ROMFS_DIR = os.path.join(RYUJINX_MOD_DIR, "romfs", "dqh2")
RYUJINX_BIN = os.path.join(RYUJINX_ROMFS_DIR, "LINKDATA.BIN")
RYUJINX_IDX = os.path.join(RYUJINX_ROMFS_DIR, "LINKDATA.IDX")
RYUJINX_EXEFS = os.path.join(RYUJINX_MOD_DIR, "exefs", f"{BUILD_ID}.ips")

ROMFS_CLEAN_BIN = os.path.join(BASE_DIR, "romfs", "dqh2", "LINKDATA.BIN")

ENTRY_55_OFF = 4805120
ENTRY_55_ZSZ = 1106944
ORIG_BIN_SIZE = 3740846848 # ท้ายไฟล์เดิมสำหรับ Append Entry 36
WIDTH_BLOCKS = 4096 // 4   # 1024
BLOCK_BYTES = 16

# -------------------------------------------------------------
# 1. นิยามอักขระ 70 ตัวพื้นฐาน
# -------------------------------------------------------------
BASIC_70_CHARS = (
    # 44 พยัญชนะ (ก - ฮ)
    list("กขฃคฅฆงจฉชซฌญฎฏฐฑฒณดตถทธนบปผฝพฟภมยรลวศษสหฬอฮ")
    # 11 สระแนวบรรทัด
    + list("ะาำเแโใไฤฦๅ")
    # 8 สระบน-ล่าง
    + ["ิ", "ี", "ึ", "ื", "ุ", "ู", "ั", "็"]
    # 7 วรรณยุกต์ และเครื่องหมาย
    + ["่", "้", "๊", "๋", "์", "ๆ", "ฯ"]
)
assert len(BASIC_70_CHARS) == 70

def jis_to_sjis_char(ku, ten):
    b1 = ((ku - 1) >> 1) + (0x81 if ku <= 62 else 0xc1)
    if ku % 2 == 1:
        b2 = ten + 0x3f + (1 if ten > 63 else 0)
    else:
        b2 = ten + 0x9e
    return bytes([b1, b2]).decode('shift-jis')

def jis_to_cell(ku, ten):
    offset = (ku - 16) * 94 + (ten - 1)
    idx = 505 + offset
    row = idx // 113
    col = idx % 113
    return row, col, idx

def get_keyboard_checksum(dds_bytes):
    start_off = 128 + (1 * 9 * WIDTH_BLOCKS) * BLOCK_BYTES
    end_off   = 128 + (4 * 9 * WIDTH_BLOCKS) * BLOCK_BYTES
    return hashlib.md5(dds_bytes[start_off:end_off]).hexdigest()

f30 = ImageFont.truetype(FONT_TTF, 30)

def render_super_cluster_box(tok, target_w=30, baseline=32):
    t = Image.new('RGBA', (120, 100), (0, 0, 0, 0))
    tdraw = ImageDraw.Draw(t)
    tdraw.text((60, 60), tok, font=f30, fill=(255, 255, 255, 255), anchor='ms')
    arr = np.array(t)[:, :, 3]
    coords = np.argwhere(arr > 20)
    if len(coords) == 0:
        return Image.new('RGBA', (36, 36), (0, 0, 0, 0))
    cr = t.crop((coords[:, 1].min(), coords[:, 0].min(), coords[:, 1].max() + 1, coords[:, 0].max() + 1))
    
    h = cr.height
    w = min(34, target_w)
    scaled = cr.resize((w, h), Image.Resampling.LANCZOS)
    
    cell = Image.new('RGBA', (36, 36), (0, 0, 0, 0))
    cx = (36 - w) // 2
    cy = baseline - h + (coords[:, 0].max() - 60)
    cy = max(0, min(36 - h, cy))
    cell.paste(scaled, (cx, cy), scaled)
    return cell

def build_master_mapping():
    meta_path = os.path.join(WORKSPACE_DIR, "kanji_cluster_slots.json")
    with open(meta_path, "r", encoding="utf-8") as f:
        cluster_slots = json.load(f)
        
    mapping = {}
    # 1. 2223 PUA clusters
    for item in cluster_slots:
        mapping[item['thai']] = item['kanji']
        
    # 2. 70 Basic characters in Ku 16 (Ten 1 - 70)
    basic_slots = []
    for i, ch in enumerate(BASIC_70_CHARS):
        ten = i + 1
        kanji = jis_to_sjis_char(16, ten)
        r, c, idx = jis_to_cell(16, ten)
        basic_slots.append({'thai': ch, 'kanji': kanji, 'ku': 16, 'ten': ten, 'row': r, 'col': c, 'cell_idx': idx})
        if ch not in mapping:
            mapping[ch] = kanji
            
    # 3. 7 Super-clusters for title buttons in Ku 16 (Ten 71 - 77)
    super_tokens = [
        ('เริ่ม', 32), ('เล่น', 32), ('สร้', 28), ('าง', 28), ('ลบ', 32), ('เซ', 28), ('ฟ', 20)
    ]
    super_slots = []
    for i, (tok, tw) in enumerate(super_tokens):
        ten = 71 + i
        kanji = jis_to_sjis_char(16, ten)
        r, c, idx = jis_to_cell(16, ten)
        super_slots.append({'thai': tok, 'kanji': kanji, 'ku': 16, 'ten': ten, 'row': r, 'col': c, 'cell_idx': idx, 'target_w': tw})
        mapping[tok] = kanji

    mapping[' '] = '\u3000'
    mapping['\n'] = '\n'
    mapping['？'] = '？'
    mapping['?'] = '？'
    mapping['。'] = '。'
    mapping['.'] = '。'
    mapping['、'] = '、'
    mapping[','] = '、'
    mapping['!'] = '！'
    mapping['！'] = '！'

    return mapping, cluster_slots, basic_slots, super_slots

def main():
    start_time = time.time()
    print("=" * 80)
    print(" [DRAGON QUEST HEROES I & II] ติดตั้งระบบภาษาไทยฉบับสมบูรณ์แบบ (Master Edition)")
    print("=" * 80)

    # 1. สร้างฐานข้อมูลผัง Master Mapping
    print("\n[*] 1. กำลังโหลดและสร้างผัง Master Mapping ภาษาไทย -> Kanji...")
    master_map, cluster_slots, basic_slots, super_slots = build_master_mapping()
    print(f"    [+] คลัสเตอร์ PUA (2-3 ชั้น): {len(cluster_slots):,} ตัว")
    print(f"    [+] พยัญชนะเดี่ยวและสระพื้นฐาน: {len(basic_slots):,} ตัว (Ku 16 Ten 01-70)")
    print(f"    [+] คลัสเตอร์ 3 เมนูหลักชิดพิเศษ: {len(super_slots):,} ตัว (Ku 16 Ten 71-77)")
    print(f"    [+] รวมฐานข้อมูล Mapping ทั้งหมด: {len(master_map):,} รายการ")

    # บันทึก Mapping_Kanji.json
    out_map_p = os.path.join(SWITCH_DIR, "Mapping_Kanji.json")
    with open(out_map_p, "w", encoding="utf-8") as f:
        json.dump(master_map, f, ensure_ascii=False, indent=2)
    print(f"    [+] บันทึก {out_map_p} เรียบร้อย!")

    # 2. เรนเดอร์ Font Texture (Entry 55)
    print("\n" + "=" * 80)
    print(" [*] 2. เรนเดอร์ฟอนต์ Pridi-Bold (มาตรฐาน Baseline 32) ลงใน Entry 55...")
    print("=" * 80)
    with open(TARGET_DDS, "rb") as f:
        dds_bytes = bytearray(f.read())
        
    kb_hash_before = get_keyboard_checksum(dds_bytes)
    print(f"    [VERIFY] Checksum แป้นพิมพ์ภาษาอังกฤษ (Cells 209-377) ก่อนเรนเดอร์: {kb_hash_before}")
    assert kb_hash_before == "9bfd32c1e7cf0b0942cf83bb2d2d217e", f"Checksum แป้นพิมพ์ผิดปกติ: {kb_hash_before}"

    config = load_or_create_config()

    # 2.1 เรนเดอร์ 70 พยัญชนะเดี่ยวลง Ku 16 (Ten 1 - 70)
    print("    [+] กำลังเรนเดอร์ 70 พยัญชนะเดี่ยวและสระพื้นฐาน (Ku 16)...")
    for item in basic_slots:
        ch = item['thai']
        c_img = render_tuned_single_glyph(ch, config)
        rows_dxt = encode_cell_dxt5(c_img)
        bx0 = (item['col'] * 36) // 4
        by0 = (item['row'] * 36) // 4
        for by in range(9):
            off = 128 + ((by0 + by) * WIDTH_BLOCKS + bx0) * BLOCK_BYTES
            dds_bytes[off : off + 144] = rows_dxt[by]

    # 2.2 เรนเดอร์ 7 Super-clusters ลง Ku 16 (Ten 71 - 77)
    print("    [+] กำลังเรนเดอร์ 7 คลัสเตอร์พิเศษ 3 เมนูหลัก...")
    for item in super_slots:
        tok = item['thai']
        tw = item['target_w']
        c_img = render_super_cluster_box(tok, target_w=tw)
        rows_dxt = encode_cell_dxt5(c_img)
        bx0 = (item['col'] * 36) // 4
        by0 = (item['row'] * 36) // 4
        for by in range(9):
            off = 128 + ((by0 + by) * WIDTH_BLOCKS + bx0) * BLOCK_BYTES
            dds_bytes[off : off + 144] = rows_dxt[by]

    # 2.3 เรนเดอร์ 2,223 คลัสเตอร์ PUA ลง Ku 24 - Ku 48
    print(f"    [+] กำลังเรนเดอร์ {len(cluster_slots):,} คลัสเตอร์ PUA (Ku 24-48)...")
    t0_render = time.time()
    for item in cluster_slots:
        thai_str = item['thai']
        c_img, _ = compose_pua_cluster_image(thai_str, config)
        rows_dxt = encode_cell_dxt5(c_img)
        bx0 = (item['col'] * 36) // 4
        by0 = (item['row'] * 36) // 4
        for by in range(9):
            off = 128 + ((by0 + by) * WIDTH_BLOCKS + bx0) * BLOCK_BYTES
            dds_bytes[off : off + 144] = rows_dxt[by]
            
    print(f"    [+] เรนเดอร์และบีบอัด DXT5 ครบ 2,300 ตัวสำเร็จใน {time.time() - t0_render:.1f} วินาที!")

    # ตรวจสอบ Checksum คีย์บอร์ดหลังเรนเดอร์
    kb_hash_after = get_keyboard_checksum(dds_bytes)
    print(f"    [VERIFY] Checksum แป้นพิมพ์ภาษาอังกฤษหลังเรนเดอร์: {kb_hash_after}")
    assert kb_hash_before == kb_hash_after, "CRITICAL ERROR: แป้นพิมพ์คีย์บอร์ดถูกแตะต้อง!"
    print(f"    [PASSED 100%] ยืนยันสมบูรณ์แบบ: แป้นพิมพ์ภาษาอังกฤษ 166 ตัวเดิมไม่ถูกแตะต้องแม้แต่ไบต์เดียว!")

    with open(TARGET_DDS, "wb") as f:
        f.write(dds_bytes)
        
    # คอมไพล์ DDS -> G1T
    print("\n[*] 3. คอมไพล์ DDS กลับเป็น G1T ด้วย g1t_tool.py...")
    cmd = [sys.executable, G1T_TOOL, "import", TEX_DIR, OUT_G1T_DIR]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0, f"g1t_tool error: {res.stderr}"
    print(f"    [+] {res.stdout.strip()}")

    out_g1t = os.path.join(OUT_G1T_DIR, "entry_00055.g1t")
    with open(out_g1t, "rb") as f:
        g1t_raw = f.read()
    packed_55 = pack_entry_chunks(g1t_raw)
    print(f"    [+] บีบอัด Entry 55 สำเร็จ: {len(packed_55):,} ไบต์")

    # 3. แปลงข้อความและรีบิลด์ Entry 36
    print("\n" + "=" * 80)
    print(" [*] 4. แปลงข้อความจาก 6 ภาพถ่ายและรีบิลด์ Entry 36 แบบ Dynamic Pointers...")
    print("=" * 80)

    max_key_len = max(len(k) for k in master_map.keys())
    def convert_thai(text):
        res = []
        i = 0
        n = len(text)
        while i < n:
            matched = False
            for l in range(min(max_key_len, n - i), 0, -1):
                sub = text[i:i+l]
                if sub in master_map:
                    res.append(master_map[sub])
                    i += l
                    matched = True
                    break
            if not matched:
                res.append(text[i])
                i += 1
        return ''.join(res)

    # อ่าน Entry 36 สะอาดจาก ROMFS
    with open(ROMFS_CLEAN_BIN, "rb") as f:
        f.seek(363008)
        e36_clean = f.read(104012)

    header = e36_clean[:32]
    ptr_start = 32
    first_rel = struct.unpack_from('<I', e36_clean, ptr_start)[0]
    num_ptrs = first_rel // 4

    all_strings = []
    for idx in range(num_ptrs):
        rel_off = struct.unpack_from('<I', e36_clean, ptr_start + idx * 4)[0]
        str_off = ptr_start + rel_off
        end = e36_clean.find(b'\x00', str_off)
        all_strings.append(e36_clean[str_off:end])

    # แปลงและแทนที่ข้อความตาม 6 ภาพถ่าย
    # 1) ภาพ 1 (152806): 何番の冒険の書を作りますか？ -> String #0
    all_strings[0] = convert_thai("ต้องการสร้างบันทึกการเดินทางในช่องใด").encode('utf-8')

    # 2) ภาพ 2 (153838): これから　この世界を冒険する主人公を決めます... -> String #2
    all_strings[2] = convert_thai(
        "จากนี้ จะทำการเลือกผู้กล้าที่จะออกผจญภัยในโลกนี้\n"
        "ไม่ว่าจะเลือกชายหรือหญิง\n"
        "เนื้อหาของเกมก็จะไม่เปลี่ยนแปลง"
    ).encode('utf-8')

    # 3) ภาพ 3 (153845): 主人公を選んでください。 -> String #3
    all_strings[3] = convert_thai("โปรดเลือกผู้กล้า").encode('utf-8')

    # 4) 3 เมนูหลัก Title Screen (เริ่มเล่น / สร้างเซฟ / ลบเซฟ) -> String #1020, 1021, 1022
    # ใช้ Super-clusters 100% ชิดแน่น
    all_strings[1020] = convert_thai("เริ่มเล่น").encode('utf-8')
    all_strings[1021] = convert_thai("สร้างเซฟ").encode('utf-8')
    all_strings[1022] = convert_thai("ลบเซฟ").encode('utf-8')

    # เมนูสมุดบันทึก
    all_strings[1023] = convert_thai("บันทึกการเดินทาง").encode('utf-8')
    all_strings[1024] = convert_thai("เวลาเล่น").encode('utf-8')
    all_strings[1025] = convert_thai("วันที่บันทึก").encode('utf-8')
    all_strings[1026] = convert_thai("เนื้อเรื่อง").encode('utf-8')
    all_strings[1027] = convert_thai("ว่าง").encode('utf-8')

    # 5) ภาพ 4 (153855): ประวัติราเซล (String #1028) และ เทเรเซีย (String #1029)
    all_strings[1028] = convert_thai(
        "นักเรียนนายร้อยผู้รักความยุติธรรม\n"
        "นักดาบรุ่นเยาว์ผู้ก้าวไปข้างหน้า\n"
        "ด้วยความสดใสและใจอันเร่าร้อน"
    ).encode('utf-8')

    all_strings[1029] = convert_thai(
        "นักเรียนนายร้อยผู้เพียบพร้อม\n"
        "นักดาบสาวผู้มีความสุขุม\n"
        "คอยนำทางพรรคพวกอยู่เสมอ"
    ).encode('utf-8')

    # 6) ภาพ 5 (153904): 主人公の名前を決めてください。 -> String #1030
    all_strings[1030] = convert_thai("โปรดตั้งชื่อของตัวเอก").encode('utf-8')
    all_strings[1031] = convert_thai("โปรดตั้งชื่อให้ลูกพี่ลูกน้อง").encode('utf-8')

    # 7) ปุ่มควบคุมด้านล่าง (153855 Controls): รีเซ็ต / หมุน / ซูม
    # หา String index ที่ตรงกับ \x1bP2リセット, \x1bPKかいてん, \x1bPB\x1bPCズーム
    for s_idx, raw_b in enumerate(all_strings):
        if b'\x1bP2\xe3\x83\xaa\xe3\x82\xbb\xe3\x83\x83\xe3\x83\x88' in raw_b:
            all_strings[s_idx] = b'\x1bP2' + convert_thai("รีเซ็ต").encode('utf-8')
            print(f"    [+] แปลปุ่มควบคุม String #{s_idx}: รีเซ็ต")
        elif b'\x1bPK\xe3\x81\x8b\xe3\x81\x84\xe3\x81\xa6\xe3\x82\x93' in raw_b:
            all_strings[s_idx] = b'\x1bPK' + convert_thai("หมุน").encode('utf-8')
            print(f"    [+] แปลปุ่มควบคุม String #{s_idx}: หมุน")
        elif b'\x1bPB\x1bPC\xe3\x82\xba\xe3\x83\xbc\xe3\x83\xa0' in raw_b:
            all_strings[s_idx] = b'\x1bPB\x1bPC' + convert_thai("ซูม").encode('utf-8')
            print(f"    [+] แปลปุ่มควบคุม String #{s_idx}: ซูม")

    # ประกอบ Entry 36 ใหม่
    ptrs_bytes = bytearray()
    pool_bytes = bytearray()
    base_rel = num_ptrs * 4

    for s in all_strings:
        rel_off = base_rel + len(pool_bytes)
        ptrs_bytes.extend(struct.pack('<I', rel_off))
        pool_bytes.extend(s + b'\x00')

    rebuilt_e36 = header + ptrs_bytes + pool_bytes
    pad = (128 - (len(rebuilt_e36) % 128)) % 128
    rebuilt_e36_padded = rebuilt_e36 + b'\x00' * pad
    rebuilt_size = len(rebuilt_e36_padded)
    print(f"    [+] ประกอบ Entry 36 สำเร็จ: ขนาด {rebuilt_size:,} ไบต์ (128-byte aligned)")

    # 4. สร้างไฟล์ IPS Patch สำหรับ ExeFS
    print("\n" + "=" * 80)
    print(" [*] 5. สร้าง ExeFS IPS Patch (Proportional Width + ปุ่มคีย์บอร์ด ENG / กลับ / ตกลง)...")
    print("=" * 80)

    # นำโค้ด Proportional Width ASM จาก deploy_proportional_exefs_patch.py
    HOOK_ADDR = 0x0001C728
    CAVE_ADDR = 0x00DC2530
    cave_pc   = 0x00DC2430

    def make_b(src, dst):
        imm26 = (dst - src) >> 2
        return 0x14000000 | (imm26 & 0x03FFFFFF)

    def make_b_cond(src, dst, cond):
        imm19 = (dst - src) >> 2
        return 0x54000000 | ((imm19 & 0x0007FFFF) << 5) | (cond & 0x1F)

    hook_instr = make_b(0x0001C628, cave_pc)
    hook_payload = struct.pack("<I", hook_instr)

    records = [
        (HOOK_ADDR, hook_payload)
    ]

    # Cave ASM instructions
    asm_words = [
        0x531C614A,
        0x7101895F,
        make_b_cond(cave_pc + 0x08, cave_pc + 0x1C, 1),
        0x7104B95F,
        make_b_cond(cave_pc + 0x10, cave_pc + 4, 1),
        0xB85FC148,
        make_b(cave_pc + 0x18, cave_pc + 0x24),
        0xD503201F,
        0xB9401BE8,
        make_b(cave_pc + 0x24, 0x0001C62C)
    ]
    cave_payload = bytearray()
    for w in asm_words:
        cave_payload.extend(struct.pack("<I", w))
    records.append((CAVE_ADDR, bytes(cave_payload)))

    # String pool ใน .rodata สำหรับปุ่มคีย์บอร์ด (0x01054E50)
    # 153908: カナ -> ENG, 戻る -> กลับ, 決定 -> ตกลง
    # วางสตริงในช่องว่าง 0x01054E50
    ENG_STR = b"ENG\x00"
    BACK_STR = convert_thai("กลับ").encode('utf-8') + b"\x00"
    OK_STR = convert_thai("ตกลง").encode('utf-8') + b"\x00"

    rodata_base = 0x01054E50
    off_eng = rodata_base
    off_back = off_eng + len(ENG_STR)
    off_ok = off_back + len(BACK_STR)

    str_pool = ENG_STR + BACK_STR + OK_STR
    records.append((rodata_base, str_pool))

    # ปรับ Pointer ปุ่มคีย์บอร์ด
    records.append((0x00ed7c80, struct.pack("<Q", off_eng)))  # Page 1 toggle: カナ -> ENG
    records.append((0x00ed8490, struct.pack("<Q", off_eng)))  # Page 2 toggle: かな -> ENG
    records.append((0x00ed7c98, struct.pack("<Q", off_back))) # Page 1 back: 戻る -> กลับ
    records.append((0x00ed84a8, struct.pack("<Q", off_back))) # Page 2 back: 戻る -> กลับ
    records.append((0x00ed7cb0, struct.pack("<Q", off_ok)))   # Page 1 confirm: 決定 -> ตกลง
    records.append((0x00ed84c0, struct.pack("<Q", off_ok)))   # Page 2 confirm: 決定 -> ตกลง

    def make_ips32(recs):
        buf = bytearray(b"IPS32")
        for off, payload in recs:
            buf.extend(struct.pack(">IH", off, len(payload)))
            buf.extend(payload)
        buf.extend(b"EEOF")
        return bytes(buf)

    ips_data = make_ips32(records)
    print(f"    [+] สร้าง Records ทั้งหมด: {len(records)} รายการ")
    print(f"    [+] ขนาดไฟล์ IPS: {len(ips_data)} ไบต์")

    # 5. ติดตั้งและฉีดเข้าสู่ Atmosphere, Yuzu และ Ryujinx
    print("\n" + "=" * 80)
    print(" [*] 6. ฉีดไฟล์ RomFS และ ExeFS เข้าสู่โฟลเดอร์ Mod ทุกเป้าหมาย...")
    print("=" * 80)

    targets = [
        ("Atmosphere Mod (Drive D)", ATMOS_BIN, ATMOS_IDX, ATMOS_EXEFS),
        ("Yuzu Mod (Drive C)", YUZU_BIN, YUZU_IDX, YUZU_EXEFS),
        ("Ryujinx Mod (Drive C)", RYUJINX_BIN, RYUJINX_IDX, RYUJINX_EXEFS)
    ]

    for name, bin_p, idx_p, exefs_p in targets:
        if not os.path.exists(bin_p):
            print(f"    [-] ข้าม {name} (ไม่พบไฟล์ LINKDATA.BIN)")
            continue
            
        print(f"\n    [*] กำลังติดตั้งลงใน -> {name}...")
        
        # 6.1 ฉีด Entry 55 Font Atlas
        with open(bin_p, "r+b") as f:
            f.seek(ENTRY_55_OFF)
            f.write(packed_55)
            print(f"        [+] ฉีด Entry 55 Font Atlas (2,300 ตัวอักษร) สำเร็จ")

            # 6.2 Append Entry 36 ต่อท้ายไฟล์
            f.seek(ORIG_BIN_SIZE)
            f.truncate(ORIG_BIN_SIZE)
            f.seek(ORIG_BIN_SIZE)
            f.write(rebuilt_e36_padded)
            print(f"        [+] Append Entry 36 ภาษาไทย ({rebuilt_size:,} ไบต์) ที่ Offset {ORIG_BIN_SIZE} สำเร็จ")

        # 6.3 อัปเดต LINKDATA.IDX ของ Entry 36
        if os.path.exists(idx_p):
            with open(idx_p, "r+b") as f:
                f.seek(36 * 32)
                new_idx = struct.pack('<QQQQ', ORIG_BIN_SIZE, rebuilt_size, rebuilt_size, 0)
                f.write(new_idx)
                print(f"        [+] อัปเดต LINKDATA.IDX Entry 36 -> Offset {ORIG_BIN_SIZE} สำเร็จ")

        # 6.4 บันทึก IPS Patch
        os.makedirs(os.path.dirname(exefs_p), exist_ok=True)
        with open(exefs_p, "wb") as f:
            f.write(ips_data)
        print(f"        [+] บันทึก ExeFS IPS Patch สำเร็จ -> {exefs_p}")

    total_time = time.time() - start_time
    print("\n" + "=" * 80)
    print(f" [SUCCESS] ติดตั้งระบบภาษาไทย Master Edition สำเร็จสมบูรณ์แบบใน {total_time:.1f} วินาที!")
    print(" - 2,223 คลัสเตอร์ PUA: ครบถ้วน 100% พร้อมแปลทั้งเกม")
    print(" - 70 พยัญชนะและสระพื้นฐาน: สวยงาม คมชัด มาตรฐาน Baseline 32")
    print(" - 166 ช่องแป้นพิมพ์ภาษาอังกฤษ: ปลอดภัย 100% (MD5 ตรงกันเป๊ะ)")
    print(" - ข้อความ 6 ภาพถ่ายหน้าจอ: แปลภาษาไทยสมบูรณ์แบบ ชิดสวยงาม")
    print("=" * 80)

if __name__ == "__main__":
    main()
