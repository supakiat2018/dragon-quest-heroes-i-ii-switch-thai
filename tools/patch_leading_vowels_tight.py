import os

gui_path = r"D:\Game\dragon quest heroes i & ii\switch\tools\thai_font_preview_gui.py"
with open(gui_path, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Update render_tuned_single_glyph default offsets
old_offsets = '''    elif ch == 'เ':
        default_ox, default_oy, default_w, default_h = 7, 0, 10, 19
    elif ch == 'แ':
        default_ox, default_oy, default_w, default_h = 6, 0, 18, 19
    elif ch in 'โใไ':
        default_ox, default_oy, default_w, default_h = -2, 0, 14, 26'''

new_offsets = '''    elif ch == 'เ':
        default_ox, default_oy, default_w, default_h = 14, 0, 10, 19
    elif ch == 'แ':
        default_ox, default_oy, default_w, default_h = 9, 0, 18, 19
    elif ch in 'โใไ':
        default_ox, default_oy, default_w, default_h = 11, 0, 14, 26'''

assert old_offsets in code, "old_offsets not found!"
code = code.replace(old_offsets, new_offsets)

# 2. Update tight_presets in apply_auto_tight_spacing
old_tight = '''            'เ': {'offset_x': 7, 'offset_y': 0, 'width': 10, 'height': 19},
            'แ': {'offset_x': 6, 'offset_y': 0, 'width': 18, 'height': 19},'''

new_tight = '''            'เ': {'offset_x': 14, 'offset_y': 0, 'width': 10, 'height': 19},
            'แ': {'offset_x': 9, 'offset_y': 0, 'width': 18, 'height': 19},
            'โ': {'offset_x': 11, 'offset_y': 0, 'width': 14, 'height': 26},
            'ใ': {'offset_x': 11, 'offset_y': 0, 'width': 14, 'height': 26},
            'ไ': {'offset_x': 11, 'offset_y': 0, 'width': 14, 'height': 26},'''

assert old_tight in code, "old_tight not found!"
code = code.replace(old_tight, new_tight)

# 3. In compose_pua_cluster_image, ensure pos_x_b respects boundary
old_pos_xb = '''            pos_x_b = (36 - w_b) // 2 + whole_ox + ox
        pos_y_b = baseline - h_b + oy
        cell.paste(sc_b, (pos_x_b, pos_y_b), sc_b)'''

new_pos_xb = '''            pos_x_b = max(0, min(36 - w_b, (36 - w_b) // 2 + whole_ox + ox))
        pos_y_b = max(0, min(36 - h_b, baseline - h_b + oy))
        cell.paste(sc_b, (pos_x_b, pos_y_b), sc_b)'''

assert old_pos_xb in code, "old_pos_xb not found!"
code = code.replace(old_pos_xb, new_pos_xb)

with open(gui_path, "w", encoding="utf-8") as f:
    f.write(code)

print("Applied leading vowels tight spacing patch successfully!")
