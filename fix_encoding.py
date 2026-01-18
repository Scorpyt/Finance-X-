
import os

source_path = 'static/terminal.js'
dest_path = 'static/terminal_final.js'

print(f"Reading {source_path}...")
with open(source_path, 'rb') as f:
    raw = f.read()

# Attempt detection/fix
text = ""
try:
    # Try UTF-8 first
    text = raw.decode('utf-8')
    print("Decoded as UTF-8")
except UnicodeDecodeError:
    try:
        # Try UTF-16 (little endian is common on Windows for "Unicode")
        text = raw.decode('utf-16')
        print("Decoded as UTF-16")
    except UnicodeDecodeError:
        # Fallback to Latin-1 (binary safe)
        text = raw.decode('latin-1')
        print("Decoded as Latin-1")

# Clean up common artifacts of bad encoding conversions
# If it was double-spaced (null bytes), remove them
if '\x00' in text:
    print("Detected null bytes, removing...")
    text = text.replace('\x00', '')

# Write clean file
print(f"Writing clean content to {dest_path}...")
with open(dest_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Done.")
