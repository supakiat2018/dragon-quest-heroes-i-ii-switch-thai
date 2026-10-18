# Dragon Quest Heroes I & II (Nintendo Switch) - Thai Translation Mod

โปรเจกต์ม็อดแปลภาษาไทยสำหรับเกม **Dragon Quest Heroes I & II** บนเครื่อง **Nintendo Switch** (JAP: Title ID `0100CD3000BDC000`)  
รองรับการเล่นผ่าน Custom Firmware (Atmosphere LayeredFS) และโปรแกรมจำลอง Yuzu / Ryujinx

---

## ความคืบหน้าปัจจุบัน (Current Progress)

### 1. แป้นพิมพ์ภาษาไทยในเกม (In-Game Thai Keyboard) - 100%
* **เรียงพยัญชนะไทยครบ 44 ตัว (ก - ฮ)**:
  * บล็อกซ้าย (30 ปุ่ม): `ก ข ฃ ค ฅ ฆ ง จ ฉ ช ซ ฌ ญ ฎ ฏ ฐ ฑ ฒ ณ ด ต ถ ท ธ น บ ป ผ ฝ พ`
  * บล็อกกลาง (28 ปุ่ม): `ฟ ภ ม ย ร ล ว ศ ษ ส ห ฬ อ ฮ ะ า ำ เ แ โ ใ ไ ฤ ฦ ๆ - ~ .`
  * บล็อกขวา (25 ปุ่ม): `ิ ี ึ ื ุ ู ฺ ั ็ ์ ่ ้ ๊ ๋ ํ 0 1 2 3 4 5 6 7 8 9`
* แสดงผลตัวอักษรไทยคมชัดด้วยฟอนต์ Leelawadee UI (`leelawui.ttf`) บนแป้นพิมพ์ในเกม และพิมพ์ชื่อตัวละครออกมาเป็นภาษาไทยได้ทันที

---

## วิธีติดตั้งม็อด (Installation Guide)

### สำหรับ Nintendo Switch (Atmosphere)
คัดลอกโฟลเดอร์ `atmosphere` ไปวางที่ Root ของ MicroSD Card:
```text
sdcard:/atmosphere/contents/0100CD3000BDC000/romfs/dqh2/
├── LINKDATA.BIN
└── LINKDATA.IDX
```

### สำหรับ Yuzu Emulator
1. คลิกขวาที่ชื่อเกม **Dragon Quest Heroes I & II** ในหน้าจอ Yuzu
2. เลือก **Open Mod Data Location**
3. วางโฟลเดอร์ `atmosphere` หรือโฟลเดอร์ที่มีโครงสร้าง `romfs/dqh2/` ลงในนั้น
4. เปิดเกมและเข้าสู่หน้าสร้างตัวละครเพื่อใช้งานแป้นพิมพ์ภาษาไทย
