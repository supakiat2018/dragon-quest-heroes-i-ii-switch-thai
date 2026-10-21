import os
import json

slots_path = r"D:\Game\dragon quest heroes i & ii\switch\workspace\kanji_cluster_slots.json"
slots = json.load(open(slots_path, encoding='utf-8'))
mapping = {x['thai']: x['kanji'] for x in slots}

def jis_to_sjis_char(ku, ten):
    b1 = ((ku - 1) >> 1) + (0x81 if ku <= 62 else 0xc1)
    if ku % 2 == 1:
        b2 = ten + 0x3f + (1 if ten > 63 else 0)
    else:
        b2 = ten + 0x9e
    return bytes([b1, b2]).decode('shift-jis')

BASIC_70 = (
    list('กขฃคฅฆงจฉชซฌญฎฏฐฑฒณดตถทธนบปผฝพฟภมยรลวศษสหฬอฮ')
    + list('ะาำเแโใไฤฦๅ')
    + ['ิ', 'ี', 'ึ', 'ื', 'ุ', 'ู', 'ั', '็']
    + ['่', '้', '๊', '๋', '์', 'ๆ', 'ฯ']
)
for i, ch in enumerate(BASIC_70):
    kanji = jis_to_sjis_char(16, i + 1)
    if ch not in mapping:
        mapping[ch] = kanji

mapping[' '] = '\u3000'
mapping['\n'] = '\n'
mapping['?'] = '？'
mapping['.'] = '。'

max_len = max(len(k) for k in mapping.keys())

def convert(text):
    res = []
    i = 0
    n = len(text)
    while i < n:
        matched = False
        for l in range(min(max_len, n - i), 0, -1):
            sub = text[i:i+l]
            if sub in mapping:
                res.append(mapping[sub])
                i += l
                matched = True
                break
        if not matched:
            res.append(text[i])
            i += 1
    return ''.join(res)

tests = [
    ("ต้องการสร้างบันทึกการเดินทางในช่องใด", 45),
    ("จะสร้างบันทึกการเดินทางในช่องใด？", 45),
    ("จากนี้ จะทำการเลือกผู้กล้าที่จะออกผจญภัยในโลกนี้\nไม่ว่าจะเลือกชายหรือหญิง\nเนื้อหาของเกมก็จะไม่เปลี่ยนแปลง", 167),
    ("โปรดเลือกผู้กล้า", 39),
    ("นักเรียนนายร้อยผู้รักความยุติธรรม\nนักดาบรุ่นเยาว์ผู้ก้าวไปข้างหน้า\nด้วยความร่าเริงและใจอันเร่าร้อน", 116),
    ("นักเรียนนายร้อยผู้เพียบพร้อม\nนักดาบสาวผู้มีความสุขุม\nคอยนำทางพรรคพวกอยู่เสมอ", 107),
    ("โปรดตั้งชื่อของตัวเอก", 48),
    ("โปรดตั้งชื่อของตัวเอก。", 48),
    ("กลับ", 6),
    ("ตกลง", 6),
]

for t, max_b in tests:
    conv = convert(t)
    b = conv.encode('utf-8')
    unmapped = [c for c in conv if ord(c) < 128 and c not in '\n']
    ok = len(b) <= max_b
    print(f'[{t[:25]:25s}] -> {len(b):3d}b / {max_b:3d}b (OK: {ok}) | Unmapped: {unmapped}')
