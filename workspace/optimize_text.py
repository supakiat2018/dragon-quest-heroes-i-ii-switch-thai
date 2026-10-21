import re
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from check_translations import tokenize_formula_949

# Optimize P2: max 55 tokens
# Original JP:
# これから　この世界を冒険する主人公を決めます。 (24 chars)
# 男女ふたりのうち　どちらを選んでも (17 chars)
# ゲームの内容は　変わりません。 (15 chars)
# Total JP chars = 56 chars

candidates_p2 = [
    # Candidate 1:
    (
        "กำหนดตัวเอกที่จะออกผจญภัย\n"
        "ไม่ว่าจะเลือกชายหรือหญิง\n"
        "เนื้อหาเกมก็ไม่ต่างกัน"
    ),
    # Candidate 2:
    (
        "เลือกตัวเอกที่จะผจญภัย\n"
        "ไม่ว่าจะเลือกชายหรือหญิง\n"
        "เนื้อหาเกมจะไม่เปลี่ยนไป"
    ),
    # Candidate 3:
    (
        "เลือกตัวเอกที่จะออกผจญภัย\n"
        "เลือกชายหรือหญิงก็ได้\n"
        "เนื้อเรื่องจะไม่เปลี่ยน"
    ),
]

print("=== OPTIMIZING P2 (Must be <= 55 tokens) ===")
for idx, p in enumerate(candidates_p2):
    toks = tokenize_formula_949(p)
    b_len = sum(3 if ord(t[0]) > 127 else len(t.encode('utf-8')) for t in toks)
    print(f"Cand {idx+1}: {len(toks)} toks, {b_len} bytes (<= 167: {b_len <= 167})")
    for l in p.split('\n'):
        print(f"   {l} ({len(tokenize_formula_949(l))} toks)")

# Optimize P3: max 28 tokens
# Original JP:
# 次に　主人公と共に　冒険をする (16 chars)
# いとこの名前を　決めます。 (13 chars)
# Total JP chars = 29 chars

candidates_p3 = [
    (
        "ตั้งชื่อลูกพี่ลูกน้อง\n"
        "ที่จะร่วมผจญภัยไปด้วย"
    ),
    (
        "ตั้งชื่อลูกพี่ลูกน้อง\n"
        "ที่จะร่วมผจญภัย"
    ),
    (
        "กำหนดชื่อเพื่อนร่วมทาง\n"
        "ที่จะผจญภัยกับตัวเอก"
    )
]

print("\n=== OPTIMIZING P3 (Must be <= 28 tokens) ===")
for idx, p in enumerate(candidates_p3):
    toks = tokenize_formula_949(p)
    b_len = sum(3 if ord(t[0]) > 127 else len(t.encode('utf-8')) for t in toks)
    print(f"Cand {idx+1}: {len(toks)} toks, {b_len} bytes (<= 85: {b_len <= 85})")
    for l in p.split('\n'):
        print(f"   {l} ({len(tokenize_formula_949(l))} toks)")
