import os
import base64

TTF_PATH = r"D:\Game\dragon quest heroes i & ii\switch\fonts\Pridi-Bold.ttf"
with open(TTF_PATH, "rb") as f:
    b64_font = base64.b64encode(f.read()).decode('ascii')

html_content = f"""<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="UTF-8">
<title>Dragon Quest Heroes II - Thai Font & Word Tester</title>
<style>
  @font-face {{
    font-family: 'PridiBold';
    src: url(data:font/truetype;charset=utf-8;base64,{b64_font}) format('truetype');
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background: #121620;
    color: #e2e8f0;
    font-family: 'Segoe UI', Tahoma, sans-serif;
    padding: 20px;
  }}
  .container {{
    max-width: 1000px;
    margin: 0 auto;
    background: #1a202c;
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.5);
    border: 1px solid #2d3748;
  }}
  h1 {{
    color: #ecc94b;
    font-size: 22px;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 10px;
  }}
  .subtitle {{
    color: #a0aec0;
    font-size: 14px;
    margin-bottom: 20px;
  }}
  .input-panel {{
    background: #232d3f;
    padding: 16px;
    border-radius: 8px;
    margin-bottom: 20px;
    border: 1px solid #3b4c68;
  }}
  .input-row {{
    display: flex;
    gap: 12px;
    margin-bottom: 12px;
  }}
  input[type="text"] {{
    flex: 1;
    background: #101622;
    border: 1px solid #4a5568;
    color: #fff;
    font-size: 18px;
    font-family: 'PridiBold', sans-serif;
    padding: 10px 14px;
    border-radius: 6px;
    outline: none;
  }}
  input[type="text"]:focus {{
    border-color: #3b82f6;
  }}
  .btn {{
    background: #3b82f6;
    color: #fff;
    border: none;
    padding: 10px 18px;
    border-radius: 6px;
    cursor: pointer;
    font-weight: bold;
    font-size: 14px;
  }}
  .btn:hover {{ background: #2563eb; }}
  .presets {{
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    align-items: center;
  }}
  .preset-btn {{
    background: #2d3748;
    color: #cbd5e0;
    border: 1px solid #4a5568;
    padding: 5px 12px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 13px;
  }}
  .preset-btn:hover {{
    background: #4a5568;
    color: #fff;
  }}
  .options {{
    display: flex;
    gap: 18px;
    margin-top: 12px;
    font-size: 14px;
    color: #cbd5e0;
  }}
  .canvas-box {{
    background: #0d111a;
    border-radius: 8px;
    padding: 20px;
    border: 1px solid #2d3748;
    text-align: center;
    overflow-x: auto;
  }}
  canvas {{
    background: transparent;
    display: block;
    margin: 0 auto;
    image-rendering: pixelated;
  }}
  .gallery-section {{
    margin-top: 24px;
    background: #232d3f;
    padding: 16px;
    border-radius: 8px;
    border: 1px solid #3b4c68;
  }}
  .gallery-title {{
    color: #63b3ed;
    font-weight: bold;
    font-size: 15px;
    margin-bottom: 10px;
  }}
  .char-grid {{
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-bottom: 14px;
  }}
  .char-tile {{
    width: 44px;
    height: 44px;
    background: #141b28;
    border: 1px solid #3a4a66;
    color: #fff;
    font-family: 'PridiBold', sans-serif;
    font-size: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    border-radius: 4px;
    transition: all 0.15s;
    user-select: none;
  }}
  .char-tile:hover {{
    background: #3b82f6;
    border-color: #60a5fa;
    transform: translateY(-2px);
  }}
</style>
</head>
<body>
<div class="container">
  <h1>⚔️ Dragon Quest Heroes II - Thai Font & Word Tester</h1>
  <div class="subtitle">โปรแกรมพรีวิวตัวอักษรและทดสอบคำภาษาไทย (สูตรฟอนต์ Pridi-Bold 36x36 Cell สมบูรณ์แบบ)</div>

  <div class="input-panel">
    <div class="input-row">
      <input type="text" id="wordInput" value="เริ่มเล่น สร้างเซฟ ลบเซฟ" placeholder="พิมพ์คำภาษาไทยที่ต้องการทดสอบ...">
      <button class="btn" onclick="saveImage()">💾 บันทึกภาพ PNG</button>
    </div>
    <div class="presets">
      <span style="color:#a0aec0; font-size:13px;">คำแนะนำ:</span>
      <button class="preset-btn" onclick="setWord('เริ่มเล่น')">เริ่มเล่น</button>
      <button class="preset-btn" onclick="setWord('สร้างเซฟ')">สร้างเซฟ</button>
      <button class="preset-btn" onclick="setWord('ลบเซฟ')">ลบเซฟ</button>
      <button class="preset-btn" onclick="setWord('ชื่อตัวละครหลัก')">ชื่อตัวละครหลัก</button>
      <button class="preset-btn" onclick="setWord('ภารกิจใหม่')">ภารกิจใหม่</button>
      <button class="preset-btn" onclick="setWord('กระเป๋าไอเทม')">กระเป๋าไอเทม</button>
      <button class="preset-btn" onclick="setWord('เวทมนตร์คาถา')">เวทมนตร์คาถา</button>
    </div>
    <div class="options">
      <label><input type="checkbox" id="chkGrid" checked onchange="render()"> แสดงเส้นกรอบ 36x36 (Cell Grid)</label>
      <label><input type="checkbox" id="chkLines" checked onchange="render()"> แสดงเส้นระดับเพดาน-ฐาน (Guidelines)</label>
      <label><input type="checkbox" id="chkCombine" checked onchange="render()"> รวมสระหน้า (เริ่, เล่, เซ)</label>
      <label>ซูม: 
        <select id="selZoom" onchange="render()" style="background:#101622; color:#fff; border:1px solid #4a5568; padding:2px 6px; border-radius:4px;">
          <option value="1">1x</option>
          <option value="2" selected>2x (แนะนำ)</option>
          <option value="3">3x (HD)</option>
        </select>
      </label>
    </div>
  </div>

  <div class="canvas-box">
    <canvas id="previewCanvas"></canvas>
  </div>

  <div class="gallery-section">
    <div class="gallery-title">คลิกที่ตัวอักษรเพื่อใส่ลงในช่องทดสอบคำได้ทันที:</div>
    
    <div style="font-size:12px; color:#a0aec0; margin-bottom:6px;">พยัญชนะไทย 44 ตัว (ก - ฮ):</div>
    <div class="char-grid" id="consonantsGrid"></div>

    <div style="font-size:12px; color:#a0aec0; margin-bottom:6px;">สระและวรรณยุกต์:</div>
    <div class="char-grid" id="vowelsGrid"></div>

    <div style="font-size:12px; color:#a0aec0; margin-bottom:6px;">คลัสเตอร์ผสม 2-3 ชั้นยอดนิยม:</div>
    <div class="char-grid" id="clustersGrid"></div>
  </div>
</div>

<script>
const UPPER_MARKS = new Set(['ั', 'ิ', 'ี', 'ึ', 'ื', 'ํ']);
const LOWER_MARKS = new Set(['ุ', 'ู', 'ฺ']);
const TONE_MARKS  = new Set(['่', '้', '๊', '๋', '์', '็']);

function tokenize(text, combineLeading) {{
  const tokens = [];
  let i = 0;
  const n = text.length;
  while (i < n) {{
    const ch = text[i];
    if ('เแโใไ'.includes(ch)) {{
      if (combineLeading && i + 1 < n && text[i+1] >= 'ก' && text[i+1] <= 'ฮ') {{
        let base = text[i+1];
        let idx = i + 2;
        let marks = '';
        while (idx < n && (UPPER_MARKS.has(text[idx]) || LOWER_MARKS.has(text[idx]) || TONE_MARKS.has(text[idx]))) {{
          marks += text[idx];
          idx++;
        }}
        tokens.push(ch + base + marks);
        i = idx;
      }} else {{
        tokens.push(ch);
        i++;
      }}
    }} else if (ch >= 'ก' && ch <= 'ฮ' || ch === 'ฤ' || ch === 'ฦ') {{
      let base = ch;
      let idx = i + 1;
      let marks = '';
      while (idx < n && (UPPER_MARKS.has(text[idx]) || LOWER_MARKS.has(text[idx]) || TONE_MARKS.has(text[idx]))) {{
        marks += text[idx];
        idx++;
      }}
      tokens.push(base + marks);
      i = idx;
    }} else {{
      tokens.push(ch);
      i++;
    }}
  }}
  return tokens;
}}

const canvas = document.getElementById('previewCanvas');
const ctx = canvas.getContext('2d');
const input = document.getElementById('wordInput');

function setWord(w) {{
  input.value = w;
  render();
}}

function appendChar(c) {{
  input.value += c;
  render();
}}

input.addEventListener('input', render);

function render() {{
  const text = input.value || ' ';
  const combine = document.getElementById('chkCombine').checked;
  const showGrid = document.getElementById('chkGrid').checked;
  const showLines = document.getElementById('chkLines').checked;
  const zoom = parseInt(document.getElementById('selZoom').value, 10);

  const lines = text.split('\\n');
  const maxTokens = Math.max(...lines.map(l => tokenize(l, combine).length), 1);
  const nativeW = maxTokens * 36 + 48;
  const nativeH = lines.length * 64 + 32;

  // Offscreen native canvas
  const off = document.createElement('canvas');
  off.width = nativeW;
  off.height = nativeH;
  const octx = off.getContext('2d');

  octx.fillStyle = '#141a26';
  octx.fillRect(0, 0, nativeW, nativeH);

  let yCursor = 20;
  for (const line of lines) {{
    const tokens = tokenize(line, combine);
    const boxW = tokens.length * 36 + 24;
    const boxH = 44;

    // Game button background (Dragon Quest UI)
    octx.fillStyle = '#1a2436';
    octx.strokeStyle = '#c3a055';
    octx.lineWidth = 2;
    roundRect(octx, 24, yCursor, boxW, boxH, 6, true, true);

    octx.strokeStyle = '#283c5f';
    octx.lineWidth = 1;
    roundRect(octx, 26, yCursor + 2, boxW - 4, boxH - 4, 5, false, true);

    if (showLines) {{
      octx.strokeStyle = 'rgba(255, 70, 70, 0.6)';
      octx.beginPath();
      octx.moveTo(28, yCursor + 4 + 6);
      octx.lineTo(24 + boxW - 4, yCursor + 4 + 6);
      octx.stroke();

      octx.strokeStyle = 'rgba(70, 255, 70, 0.6)';
      octx.beginPath();
      octx.moveTo(28, yCursor + 4 + 33);
      octx.lineTo(24 + boxW - 4, yCursor + 4 + 33);
      octx.stroke();
    }}

    let xChar = 36;
    for (const token of tokens) {{
      if (showGrid && token !== ' ') {{
        octx.strokeStyle = 'rgba(65, 85, 125, 0.4)';
        octx.strokeRect(xChar, yCursor + 4, 35, 35);
      }}

      // Render token with PridiBold
      octx.font = 'bold 31px PridiBold, sans-serif';
      octx.fillStyle = '#ffffff';
      octx.textAlign = 'center';
      octx.textBaseline = 'alphabetic';
      octx.fillText(token, xChar + 18, yCursor + 4 + 31);

      xChar += 36;
    }}
    yCursor += boxH + 18;
  }}

  // Resize main canvas
  canvas.width = nativeW * zoom;
  canvas.height = nativeH * zoom;
  ctx.imageSmoothingEnabled = false;
  ctx.drawImage(off, 0, 0, canvas.width, canvas.height);
}}

function roundRect(ctx, x, y, w, h, r, fill, stroke) {{
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.arcTo(x + w, y, x + w, y + h, r);
  ctx.arcTo(x + w, y + h, x, y + h, r);
  ctx.arcTo(x, y + h, x, y, r);
  ctx.arcTo(x, y, x + w, y, r);
  ctx.closePath();
  if (fill) ctx.fill();
  if (stroke) ctx.stroke();
}}

function saveImage() {{
  const link = document.createElement('a');
  link.download = 'DQH2_Thai_Preview.png';
  link.href = canvas.toDataURL();
  link.click();
}}

// Setup Character Grids
const consonants = 'กขฃคฅฆงจฉชซฌญฎฏฐฑฒณดตถทธนบปผฝพฟภมยรลวศษสหฬอฮ';
const vowels = ['ะ', 'า', 'ำ', 'เ', 'แ', 'โ', 'ใ', 'ไ', 'ฤ', 'ฦ', 'ิ', 'ี', 'ึ', 'ื', 'ุ', 'ู', '่', '้', '๊', '๋', '์', '็'];
const clusters = ['กิ่', 'กิ้', 'ริ่', 'ร้', 'ล่', 'ล้', 'ชื่', 'ตั้', 'ลั้', 'ผู้', 'รู้', 'ปี้', 'เริ่', 'เล่', 'เซ', 'เต', 'เน', 'เก'];

function fillGrid(id, items) {{
  const el = document.getElementById(id);
  for (const item of items) {{
    const tile = document.createElement('div');
    tile.className = 'char-tile';
    tile.textContent = item;
    tile.onclick = () => appendChar(item);
    el.appendChild(tile);
  }}
}}

fillGrid('consonantsGrid', consonants.split(''));
fillGrid('vowelsGrid', vowels);
fillGrid('clustersGrid', clusters);

// Initial render once font is ready
document.fonts.ready.then(() => {{
  render();
}});
</script>
</body>
</html>
"""

out_html_desktop = r"C:\Users\Supakiat\Desktop\DQH2_Thai_Font_Preview.html"
out_html_tools   = r"D:\Game\dragon quest heroes i & ii\switch\tools\DQH2_Thai_Font_Preview.html"

with open(out_html_desktop, "w", encoding="utf-8") as f:
    f.write(html_content)

with open(out_html_tools, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"[+] สร้าง HTML Tool สำเร็จ: {out_html_desktop}")
