import os
from PIL import Image

dir_p = r"C:\Users\Supakiat\.gemini\antigravity\brain\ab5bc3db-774b-46d7-96ba-65470fc9eb39"
files = [
    'Screenshot 2026-10-20 152806.png',
    'Screenshot 2026-10-20 153838.png',
    'Screenshot 2026-10-20 153845.png',
    'Screenshot 2026-10-20 153855.png',
    'Screenshot 2026-10-20 153904.png',
    'Screenshot 2026-10-20 153908.png'
]

html_lines = [
    '<!DOCTYPE html><html><head><meta charset="utf-8">',
    '<style>',
    'body { background: #121824; color: #fff; font-family: sans-serif; padding: 20px; }',
    '.card { background: #1e2638; border: 1px solid #334155; border-radius: 8px; margin-bottom: 25px; padding: 15px; }',
    'h3 { margin-top: 0; color: #38bdf8; }',
    'img { border: 2px solid #eab308; image-rendering: pixelated; margin-top: 10px; max-width: 100%; }',
    '</style></head><body>',
    '<h1>ภาพถ่ายหน้าจอจากเกม (C:\\Users\\Supakiat\\Pictures\\ภาพเกม)</h1>'
]

for f in files:
    html_lines.append('<div class="card">')
    html_lines.append(f'<h3>📷 {f}</h3>')
    html_lines.append(f'<img src="{f}">')
    html_lines.append('</div>')

html_lines.append('</body></html>')

out_p = os.path.join(dir_p, 'screenshots_gallery.html')
with open(out_p, 'w', encoding='utf-8') as f:
    f.write('\n'.join(html_lines))

print(f"Generated gallery: {out_p}")
