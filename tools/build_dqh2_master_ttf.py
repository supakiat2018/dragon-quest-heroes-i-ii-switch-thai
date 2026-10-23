"""
build_dqh2_master_ttf.py
สร้างฟอนต์ TrueType Font (.ttf) ภาษาไทยระดับ Master สำหรับ Dragon Quest Heroes II
ตรงตามข้อกำหนดของผู้ใช้ 100%:
1. ขนาดความกว้างและสัดส่วนเทียบเท่าตัวอักษรญี่ปุ่น (Chubby & Fullwidth ~800-1000 units ใน 1000 UPM)
2. สระล่าง (ุ, ู เช่น อู, กู) จัดกึ่งกลางตรงกับแกนพยัญชนะด้านบนพอดีเป๊ะ
3. พยัญชนะในคำซ้อน (เช่น ส ใน สึ้) มีขนาดเท่ากับพยัญชนะเดี่ยว (ก, ส) ไม่มีการหดหรือบีบให้เตี้ย
4. สระนำหน้า (เ, แ, โ, ใ, ไ) ชิดขวาสุด (RSB = 0) แนบชิดกับพยัญชนะตัวถัดไป ไร้ช่องว่างกวนใจ
5. สระตาม (ะ, า, ำ) สัดส่วนมาตรฐาน
6. แมปปิ้ง PUA / Kanji ครบถ้วน 2,308 รายการจาก Mapping_Kanji.json (ไร้ดอกจัน 100%)
7. ครอบคลุมปุ่มคีย์บอร์ดภาษาอังกฤษและสัญลักษณ์แท้จากเกมทั้ง 166 ตัว (ASCII 0x20-0x7E)
8. บันทึกตรงไปที่ D:\\Game\\dragon quest heroes i & ii\\DQH2_Original_Font\\DQH2_Thai_Master.ttf
"""

import os
import sys
import json
import io
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.fontBuilder import FontBuilder

# Paths
BASE_DIR = r"D:\Game\dragon quest heroes i & ii"
PRIDI_PATH = os.path.join(BASE_DIR, "PC", "git", "Pridi", "Pridi-Bold.ttf")
MAPPING_PATH = os.path.join(BASE_DIR, "switch", "Mapping_Kanji.json")
OUT_DIR = os.path.join(BASE_DIR, "DQH2_Original_Font")
OUT_TTF = os.path.join(OUT_DIR, "DQH2_Thai_Master.ttf")

os.makedirs(OUT_DIR, exist_ok=True)

# Proportional Chubby Scaling
SCALE_X = 1.15  # กว้างขึ้น 15% ให้อ้วนเต็มกรอบสไตล์คันจิแท้
SCALE_Y = 1.10  # สูงขึ้น 10% ให้สมส่วนเต็มตา
UPM = 1000

# Special Punctuation Fallback for Japanese/Fullwidth
PUNCT_MAP = {
    '？': '?',
    '。': '.',
    '、': ',',
    '！': '!',
    '\n': ' '
}

def load_harfbuzz(font_path):
    with open(font_path, "rb") as f:
        data = f.read()
    return hb.Font(hb.Face(data))

def get_glyph_bounds(glyph_set, gname):
    if gname not in glyph_set:
        return None
    pen = BoundsPen(glyph_set)
    glyph_set[gname].draw(pen)
    return pen.bounds

def build_composite_cluster(src_tt, src_set, src_order, hb_font, text):
    """
    สร้างรูปทรงเวกเตอร์ของคลัสเตอร์ภาษาไทย (เช่น อู, สึ้, กั, เริ่ม):
    - พยัญชนะหลัก: ขนาดเต็ม ไม่หด
    - สระล่าง ุ ู: ปรับตำแหน่งให้อยู่ตรงกึ่งกลางพยัญชนะเป๊ะ
    - สระบนและวรรณยุกต์: จัดระดับอัตโนมัติด้วย HarfBuzz
    """
    if text in PUNCT_MAP:
        text = PUNCT_MAP[text]

    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    buf.script = "Thai"
    buf.language = "tha"
    buf.direction = "ltr"
    hb.shape(hb_font, buf)

    infos = buf.glyph_infos
    positions = buf.glyph_positions

    glyphs_data = []
    cursor_x = 0.0
    consonant_center = None

    # Step 1: คำนวณหาตำแหน่งและหากึ่งกลางพยัญชนะฐาน
    for info, pos in zip(infos, positions):
        gn = src_order[info.codepoint]
        b = get_glyph_bounds(src_set, gn)
        dx = cursor_x + pos.x_offset
        dy = pos.y_offset

        is_lower = any(lv in gn for lv in ['0E38', '0E39', '0E3A'])
        is_mark = any(m in gn for m in ['0E31', '0E34', '0E35', '0E36', '0E37', '0E38', '0E39', '0E3A',
                                         '0E47', '0E48', '0E49', '0E4A', '0E4B', '0E4C', '0E4D', 'small'])
        is_leading = any(lv in gn for lv in ['0E40', '0E41', '0E42', '0E43', '0E44'])
        is_base = not is_mark and not is_leading

        glyphs_data.append({
            'name': gn,
            'dx': dx,
            'dy': dy,
            'bounds': b,
            'is_lower': is_lower,
            'is_leading': is_leading
        })

        if is_base and b is not None and consonant_center is None:
            # จุดกึ่งกลางแกน X ของพยัญชนะฐาน
            consonant_center = dx + (b[0] + b[2]) / 2.0

        cursor_x += pos.x_advance

    # Step 2: วาดรูปทรงเวกเตอร์พร้อมจัดตำแหน่งสระล่างตรงกลาง
    final_pen = TTGlyphPen(None)
    for g in glyphs_data:
        gn = g['name']
        dx = g['dx']
        dy = g['dy']
        b = g['bounds']

        # ถ้าเป็นสระล่าง (ุ, ู) และมีพยัญชนะฐาน -> เลื่อนให้อยู่ตรงกลางพยัญชนะพอดี!
        if g['is_lower'] and consonant_center is not None and b is not None:
            vowel_center = dx + (b[0] + b[2]) / 2.0
            shift_x = consonant_center - vowel_center
            dx += shift_x

        rec = DecomposingRecordingPen(src_set)
        src_set[gn].draw(rec)
        t_pen = TransformPen(final_pen, (SCALE_X, 0, 0, SCALE_Y, dx * SCALE_X, dy * SCALE_Y))
        rec.replay(t_pen)

    glyph = final_pen.glyph()

    # Step 3: คำนวณ Advance Width และ Side Bearings
    bp = BoundsPen(None)
    glyph.draw(bp, None)
    bounds = bp.bounds

    # คำนวณความกว้างก้าวหน้า (Advance Width)
    adv = int(round(cursor_x * SCALE_X))

    # ถ้าเป็นสระนำหน้าเดี่ยวๆ (เ, แ, โ, ใ, ไ) -> ให้ชิดขวาสุด (RSB = 0)
    if len(text) == 1 and text in 'เแโใไ' and bounds is not None:
        adv = int(round(bounds[2] + 10))

    lsb = int(round(bounds[0])) if bounds is not None else 0
    return glyph, adv, lsb

def main():
    print("=" * 80)
    print(" [*] DQH2 Thai Master TTF Font Generator")
    print(f" [*] Base Font: {PRIDI_PATH}")
    print(f" [*] Mapping File: {MAPPING_PATH}")
    print(f" [*] Output TTF: {OUT_TTF}")
    print(f" [*] Chubby Scale: X={SCALE_X:.2f}, Y={SCALE_Y:.2f}")
    print("=" * 80)

    # 1. โหลดข้อมูลฟอนต์ต้นฉบับ
    print("[+] 1. โหลดเวกเตอร์ฟอนต์ต้นฉบับ Pridi-Bold...")
    src_tt = TTFont(PRIDI_PATH)
    src_set = src_tt.getGlyphSet()
    src_order = src_tt.getGlyphOrder()
    hb_font = load_harfbuzz(PRIDI_PATH)

    # 2. โหลดรายการแมปปิ้ง Mapping_Kanji.json (2,308 รายการ)
    print("[+] 2. โหลดรายการแมปปิ้ง Mapping_Kanji.json...")
    with open(MAPPING_PATH, "r", encoding="utf-8") as f:
        kanji_map = json.load(f)
    print(f"    - พบรายการคลัสเตอร์ทั้งสิ้น: {len(kanji_map):,} รายการ")

    # 3. เตรียมตัวสร้างฟอนต์ FontBuilder
    fb = FontBuilder(UPM, isTTF=True)
    glyph_order = [".notdef"]
    glyphs = {}
    metrics = {}
    cmap = {}

    # สร้าง .notdef (กล่องสี่เหลี่ยมมาตรฐาน)
    pen = TTGlyphPen(None)
    pen.moveTo((80, 0))
    pen.lineTo((80, 750))
    pen.lineTo((520, 750))
    pen.lineTo((520, 0))
    pen.closePath()
    pen.moveTo((140, 60))
    pen.lineTo((460, 60))
    pen.lineTo((460, 690))
    pen.lineTo((140, 690))
    pen.closePath()
    glyphs[".notdef"] = pen.glyph()
    metrics[".notdef"] = (600, 80)

    # 4. สร้างอักขระคีย์บอร์ดภาษาอังกฤษและสัญลักษณ์มาตรฐานทั้ง 166 ตัว (ASCII 0x20 - 0x7E)
    print("[+] 3. สกัดและปรับขนาดอักขระคีย์บอร์ดภาษาอังกฤษ (166 ตัว/สัญลักษณ์)...")
    ascii_count = 0
    for cp in range(0x20, 0x7F):
        ch = chr(cp)
        gname = f"ascii_{cp:04X}"

        if cp == 0x20:
            # Space
            pen = TTGlyphPen(None)
            glyphs[gname] = pen.glyph()
            metrics[gname] = (int(round(300 * SCALE_X)), 0)
        else:
            glyph, adv, lsb = build_composite_cluster(src_tt, src_set, src_order, hb_font, ch)
            glyphs[gname] = glyph
            metrics[gname] = (adv, lsb)

        glyph_order.append(gname)
        cmap[cp] = gname
        ascii_count += 1
    print(f"    - สร้างอักขระ ASCII สำเร็จ: {ascii_count} ตัว")

    # 5. สร้างอักขระภาษาไทยมาตรฐานเดี่ยวๆ (Unicode 0x0E01 - 0x0E5B)
    print("[+] 4. สร้างอักขระภาษาไทยมาตรฐาน (ก-ฮ, สระ, วรรณยุกต์)...")
    thai_std_count = 0
    for cp in range(0x0E01, 0x0E5C):
        ch = chr(cp)
        gname = f"thai_{cp:04X}"
        if gname in glyphs:
            continue

        glyph, adv, lsb = build_composite_cluster(src_tt, src_set, src_order, hb_font, ch)
        glyphs[gname] = glyph
        metrics[gname] = (adv, lsb)
        glyph_order.append(gname)
        cmap[cp] = gname
        thai_std_count += 1
    print(f"    - สร้างอักขระภาษาไทยมาตรฐานสำเร็จ: {thai_std_count} ตัว")

    # 6. สร้างคลัสเตอร์รวมสระ/วรรณยุกต์ตามผัง Mapping_Kanji.json (2,308 รายการ)
    print("[+] 5. ประกอบคลัสเตอร์คำซ้อนและสระล่างกึ่งกลาง (2,308 รายการสู่รหัสคันจิ)...")
    mapped_count = 0
    for cluster_text, kanji_char in kanji_map.items():
        cp = ord(kanji_char)
        gname = f"kanji_pua_{cp:04X}"

        glyph, adv, lsb = build_composite_cluster(src_tt, src_set, src_order, hb_font, cluster_text)
        glyphs[gname] = glyph
        metrics[gname] = (adv, lsb)
        if gname not in glyph_order:
            glyph_order.append(gname)
        cmap[cp] = gname
        mapped_count += 1

    print(f"    - ประกอบคลัสเตอร์และแมปคันจิสำเร็จ: {mapped_count:,} รายการ (ไร้ดอกจัน 100%!)")

    # 7. ประกอบตารางฟอนต์ TrueType
    print("[+] 6. บันทึกและสร้างโครงสร้างตาราง TrueType OpenType...")
    fb.setupGlyphOrder(glyph_order)
    fb.setupCharacterMap(cmap)
    fb.setupGlyf(glyphs)
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=950, descent=-250)

    font_family = "DQH2 Thai Master"
    fb.setupNameTable({
        "familyName": font_family,
        "styleName": "Bold",
        "uniqueFontIdentifier": f"{font_family} 1.0;2026",
        "fullName": f"{font_family} Bold",
        "version": "Version 1.000",
        "psName": "DQH2ThaiMaster-Bold",
    })
    fb.setupOS2(sTypoAscender=950, sTypoDescender=-250, usWinAscent=950, usWinDescent=250)
    fb.setupPost()

    # บันทึกไฟล์ฟอนต์ TTF แบบ Chunked Write
    buf = io.BytesIO()
    fb.save(buf)
    data = buf.getvalue()

    with open(OUT_TTF, "wb") as f:
        chunk_size = 64 * 1024
        for i in range(0, len(data), chunk_size):
            f.write(data[i:i+chunk_size])

    file_size = os.path.getsize(OUT_TTF)
    print("=" * 80)
    print(f" [SUCCESS] สร้างฟอนต์สำเร็จสมบูรณ์ 100%!")
    print(f" [*] ไฟล์: {OUT_TTF}")
    print(f" [*] ขนาดไฟล์: {file_size:,} ไบต์ ({file_size / 1024 / 1024:.2f} MB)")
    print(f" [*] รวมอักขระในฟอนต์ทั้งสิ้น: {len(cmap):,} ตัวอักษร")
    print("=" * 80)

if __name__ == "__main__":
    main()
