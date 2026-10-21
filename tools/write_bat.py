# write_bat.py
content = """@echo off
title DQH2 Thai Font and Word Tester
python "D:\\Game\\dragon quest heroes i & ii\\switch\\tools\\thai_font_preview_gui.py"
if %ERRORLEVEL% NEQ 0 pause
"""
with open(r"C:\Users\Supakiat\Desktop\DQH2_Thai_Font_Preview.bat", "wb") as f:
    f.write(content.replace("\n", "\r\n").encode("ascii"))

with open(r"D:\Game\dragon quest heroes i & ii\switch\tools\DQH2_Thai_Font_Preview.bat", "wb") as f:
    f.write(content.replace("\n", "\r\n").encode("ascii"))

print("Bat files written successfully!")
