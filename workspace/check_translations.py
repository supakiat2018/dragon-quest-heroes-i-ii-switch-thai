import re

LEAD_VOWELS = set('เแโใไ')
TRAIL_VOWELS = set('ะาำฤฦๅ')
UPPER_MARKS = set('ิีึืั็ํ')
LOWER_MARKS = set('ฺุู')
TONE_MARKS = set('่้๊๋์')

def tokenize_formula_949(text):
    tokens = []
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if ch in ['\n', ' ', '?', '!', '.', ',', ':', '-', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
            tokens.append(ch)
            i += 1
        elif ch in LEAD_VOWELS or ch in TRAIL_VOWELS:
            tokens.append(ch)
            i += 1
        elif ch in UPPER_MARKS or ch in LOWER_MARKS or ch in TONE_MARKS:
            tokens.append(ch)
            i += 1
        else:
            combo = ch
            j = i + 1
            while j < n and (text[j] in UPPER_MARKS or text[j] in LOWER_MARKS or text[j] in TONE_MARKS):
                combo += text[j]
                j += 1
            tokens.append(combo)
            i = j
    return tokens

# Prompt 1 (Max 45 bytes)
print("=== PROMPT 1 (Max 45 bytes) ===")
p1_candidates = [
    'สร้างเซฟ ช่องใด?',
    'สร้างบันทึก เล่มใด?',
    'เลือกช่องบันทึก?',
    'สร้างเซฟ เล่มใด?'
]
for p in p1_candidates:
    toks = tokenize_formula_949(p)
    b_len = sum(3 if ord(t[0]) > 127 else len(t.encode('utf-8')) for t in toks)
    print(f'P1: "{p}" -> {len(toks)} toks, {b_len} bytes (max 45)')
    print('   Tokens:', toks)

# Prompt 2 (Max 167 bytes)
print("\n=== PROMPT 2 (Max 167 bytes) ===")
p2 = (
    "ต่อไปนี้ จะเลือกตัวเอกที่ผจญภัย\n"
    "ไม่ว่าจะเลือก ชาย หรือ หญิง\n"
    "เนื้อหาของเกม จะไม่เปลี่ยนแปลง"
)
toks2 = tokenize_formula_949(p2)
b_len2 = sum(3 if ord(t[0]) > 127 else len(t.encode('utf-8')) for t in toks2)
print(f'P2 -> {len(toks2)} toks, {b_len2} bytes (max 167)')
print('Lines:')
for line in p2.split('\n'):
    t_line = tokenize_formula_949(line)
    print(f'  "{line}" -> {len(t_line)} chars on screen: {t_line}')

# Prompt 3 (Max 85 bytes)
print("\n=== PROMPT 3 (Max 85 bytes) ===")
p3 = (
    "ต่อไป จะตั้งชื่อลูกพี่ลูกน้อง\n"
    "ที่จะร่วมผจญภัยกับตัวเอก"
)
toks3 = tokenize_formula_949(p3)
b_len3 = sum(3 if ord(t[0]) > 127 else len(t.encode('utf-8')) for t in toks3)
print(f'P3 -> {len(toks3)} toks, {b_len3} bytes (max 85)')
print('Lines:')
for line in p3.split('\n'):
    t_line = tokenize_formula_949(line)
    print(f'  "{line}" -> {len(t_line)} chars on screen: {t_line}')
