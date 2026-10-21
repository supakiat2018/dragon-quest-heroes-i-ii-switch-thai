import os

gui_path = r"D:\Game\dragon quest heroes i & ii\switch\tools\thai_font_preview_gui.py"
with open(gui_path, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Update render_tuned_single_glyph default offsets to ox=14, oy=1
old_offsets = '''    elif ch == 'เ':
        default_ox, default_oy, default_w, default_h = 14, 0, 10, 19
    elif ch == 'แ':
        default_ox, default_oy, default_w, default_h = 9, 0, 18, 19
    elif ch in 'โใไ':
        default_ox, default_oy, default_w, default_h = 11, 0, 14, 26'''

new_offsets = '''    elif ch == 'เ':
        default_ox, default_oy, default_w, default_h = 14, 1, 10, 19
    elif ch == 'แ':
        default_ox, default_oy, default_w, default_h = 14, 1, 18, 19
    elif ch in 'โใไ':
        default_ox, default_oy, default_w, default_h = 14, 1, 14, 26'''

assert old_offsets in code, "old_offsets not found!"
code = code.replace(old_offsets, new_offsets)

# 2. Update tight presets to ox=14, oy=1 for all leading vowels
old_tight = '''            'เ': {'offset_x': 14, 'offset_y': 0, 'width': 10, 'height': 19},
            'แ': {'offset_x': 9, 'offset_y': 0, 'width': 18, 'height': 19},
            'โ': {'offset_x': 11, 'offset_y': 0, 'width': 14, 'height': 26},
            'ใ': {'offset_x': 11, 'offset_y': 0, 'width': 14, 'height': 26},
            'ไ': {'offset_x': 11, 'offset_y': 0, 'width': 14, 'height': 26},'''

new_tight = '''            'เ': {'offset_x': 14, 'offset_y': 1, 'width': 10, 'height': 19},
            'แ': {'offset_x': 14, 'offset_y': 1, 'width': 18, 'height': 19},
            'โ': {'offset_x': 14, 'offset_y': 1, 'width': 14, 'height': 26},
            'ใ': {'offset_x': 14, 'offset_y': 1, 'width': 14, 'height': 26},
            'ไ': {'offset_x': 14, 'offset_y': 1, 'width': 14, 'height': 26},'''

assert old_tight in code, "old_tight not found!"
code = code.replace(old_tight, new_tight)

# 3. Expand slider ranges from [-14..14] to [-18..18] for comfortable tuning
code = code.replace('from_=-14, to=14', 'from_=-18, to=18')

with open(gui_path, "w", encoding="utf-8") as f:
    f.write(code)

print("Applied leading vowels +14px, +1px and slider range update successfully!")
