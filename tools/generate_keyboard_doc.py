import sys, os

sys.path.append(r"D:\Game\dragon quest heroes i & ii\switch\tools")
from build_thai_keyboard import KEYBOARD_MAPPING
from restore_and_deploy_pure_english import PAGE1_MAPPING, PAGE2_MAPPING, KATAKANA_ORDER, KATAKANA_COORDS, SRC_CHARS

md_lines = []
md_lines.append("# เอกสารผังคีย์บอร์ดภาษาอังกฤษ 166 ปุ่ม (English Software Keyboard 166 Keys)")
md_lines.append("**เกม:** Dragon Quest Heroes I & II (Nintendo Switch - `0100CD3000BDC000`)")
md_lines.append("**ไฟล์ที่แก้ไข:** RomFS Font Atlas `Entry 55` (`entry_00055.TEX0.dxt5.dds`)")
md_lines.append("")
md_lines.append("---")
md_lines.append("## 1. ฟอนต์ที่ใช้คือฟอนต์อะไร? (ไม่ได้วาดใหม่ ก๊อปปี้จากของแท้ในเกม 100%)")
md_lines.append("* **ไม่ได้วาดใหม่แม้แต่จุดเดียว (Zero Redrawing / No TTF):**")
md_lines.append("  * ไม่มีการวาดฟอนต์ขึ้นมาใหม่ด้วยมือ หรือนำไฟล์ฟอนต์ TTF/OTF จากภายนอกมาเรนเดอร์เลยแม้แต่นิดเดียว")
md_lines.append("* **แหล่งที่ก๊อปปี้มา (Copy Source):**")
md_lines.append("  * ก๊อปปี้มาจาก **ตัวอักษรภาษาอังกฤษแท้ดั้งเดิม** ที่ผู้พัฒนาเกม (Square Enix / Koei Tecmo) วางไว้ในแผ่นภาพ **`Entry 55`** อยู่แล้ว:")
md_lines.append("    * **ตัวเลขอารบิก `0 - 9`:** ก๊อปปี้จาก Entry 55 แถว 1 (Row 1) คอลัมน์ 34 ถึง 43")
md_lines.append("    * **ตัวพิมพ์ใหญ่ `A - Z`:** ก๊อปปี้จาก Entry 55 แถว 1 (Row 1) คอลัมน์ 44 ถึง 69")
md_lines.append("    * **ตัวพิมพ์เล็ก `a - z`:** ก๊อปปี้จาก Entry 55 แถว 1 (Row 1) คอลัมน์ 70 ถึง 95")
md_lines.append("    * **เครื่องหมายและสัญลักษณ์ (`!`, `?`, `-`, `.`, `/`, `:`, `;`, `_`, `+`, `=`, `~`):** ก๊อปปี้จาก Entry 55 แถว 0 (Row 0)")
md_lines.append("* **วิธีการก๊อปปี้ (Copy Technique):**")
md_lines.append("  * ใช้เทคนิคการคัดลอกระดับต่ำแบบ **Lossless DXT5 Block-by-Block (100% Bit-for-Bit)**")
md_lines.append("  * ก๊อปปี้บล็อกไบต์ขนาด 36×36 พิกเซล (9×9 DXT5 Blocks = 1,296 ไบต์/ตัว) จากพิกัดต้นทาง มาแปะทับลงในช่องปุ่มกดคีย์บอร์ดปลายทางตรงๆ")
md_lines.append("  * ตัวหนังสือจึงมีสี แสงเงา ขอบ และความคมชัดสมบูรณ์แบบระดับพิกเซล กลืนกับกราฟิกดั้งเดิมของเกม 100%")
md_lines.append("")
md_lines.append("---")
md_lines.append("## 2. แทนตัวอักษรใดในเกมบ้าง?")
md_lines.append("ระบบคีย์บอร์ดตั้งชื่อตัวละครของเกมเดิมมี **2 หน้า รวม 166 ช่อง**:")
md_lines.append("1. **หน้า 1 (เดิมคือ ฮิรางานะ `かな` 83 ตัว):** ถูกแทนที่ด้วย **ตัวพิมพ์ใหญ่ `A-Z`, ตัวเลขอารบิก `0-9`, สระช่วยพิมพ์ `A,E,I,O,U` และเครื่องหมาย**")
md_lines.append("2. **หน้า 2 (เดิมคือ คาตาคานะ `カナ` 83 ตัว):** ถูกแทนที่ด้วย **ตัวพิมพ์เล็ก `a-z`, ตัวเลขอารบิก `0-9`, สระช่วยพิมพ์ `a,e,i,o,u` และเครื่องหมาย**")
md_lines.append("")
md_lines.append("---")
md_lines.append("## 3. ตารางแจกแจงปุ่มหน้า 1 (83 ปุ่ม: ตัวพิมพ์ใหญ่ + ตัวเลข)")
md_lines.append("| ลำดับ | ตัวเดิมในเกม (ฮิรางานะ) | พิกัดปลายทางใน Entry 55 | ตัวใหม่ที่ใส่แทน | แหล่งที่ก๊อปปี้ตัวอักษรแท้มา (ต้นทาง) |")
md_lines.append("|:---:|:---:|:---:|:---:|:---:|")

for i, (orig_kana, (dst_r, dst_c), _) in enumerate(KEYBOARD_MAPPING):
    new_char = PAGE1_MAPPING[i]
    src_r, src_c = SRC_CHARS[new_char]
    char_disp = f"`{new_char}`" if new_char != ' ' else "`[Space]`"
    md_lines.append(f"| {i+1} | {orig_kana} | Row {dst_r}, Col {dst_c} | **{char_disp}** | Entry 55 (Row {src_r}, Col {src_c}) |")

md_lines.append("")
md_lines.append("---")
md_lines.append("## 4. ตารางแจกแจงปุ่มหน้า 2 (83 ปุ่ม: ตัวพิมพ์เล็ก + ตัวเลข)")
md_lines.append("| ลำดับ | ตัวเดิมในเกม (คาตาคานะ) | พิกัดปลายทางใน Entry 55 | ตัวใหม่ที่ใส่แทน | แหล่งที่ก๊อปปี้ตัวอักษรแท้มา (ต้นทาง) |")
md_lines.append("|:---:|:---:|:---:|:---:|:---:|")

for i, orig_kana in enumerate(KATAKANA_ORDER):
    new_char = PAGE2_MAPPING[i]
    dst_r, dst_c = KATAKANA_COORDS[orig_kana]
    src_r, src_c = SRC_CHARS[new_char]
    char_disp = f"`{new_char}`" if new_char != ' ' else "`[Space]`"
    md_lines.append(f"| {83+i+1} | {orig_kana} | Row {dst_r}, Col {dst_c} | **{char_disp}** | Entry 55 (Row {src_r}, Col {src_c}) |")

md_lines.append("")
md_lines.append("---")
md_lines.append("## 5. ผลกระทบต่อระบบเกม (System Safety)")
md_lines.append("* **ตัวอักษรคันจิในเกม (Kanji):** ไม่ได้รับผลกระทบใดๆ ทั้งสิ้น ตัวหนังสือในเนื้อเรื่อง เมนู ไอเทม เควสต์ ยังคงเป็นภาษาญี่ปุ่นแท้ 100% ครบทุกตัว")
md_lines.append("* **ความปลอดภัยของระบบ:** ไม่มีการใช้ ExeFS IPS Patch จึงไม่มีปัญหาเรื่องตัวหนังสือเว้นวรรคห่างหรือเกมค้าง 100%")
md_lines.append("* **การถอดถอน:** หากต้องการกลับไปใช้คีย์บอร์ดญี่ปุ่นเดิม เพียงแค่ก๊อปปี้ `clean_entry_00055.g1t` เข้ามาแทนที่")

out_path = r"D:\Game\dragon quest heroes i & ii\ENGLISH_KEYBOARD_166.md"
with open(out_path, "w", encoding="utf-8") as f:
    f.write("\n".join(md_lines))

print(f"Successfully created: {out_path} ({len(md_lines)} lines)")
