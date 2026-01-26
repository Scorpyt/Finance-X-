"""
Fix toFixed errors in Finance-X Terminal
Adds null checks to all .toFixed() calls in HTML/JS files
"""

import re
import os

def fix_toFixed_in_file(filepath):
    """Fix all toFixed calls in a file"""
    print(f"\nProcessing: {filepath}")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        try:
            with open(filepath, 'r', encoding='utf-16le') as f:
                content = f.read()
        except Exception as e:
            print(f"  ERROR: Could not read file - {e}")
            return False
    
    original_content = content
    changes = 0
    
    # Pattern 1: variable.toFixed(n) -> (variable != null ? variable.toFixed(n) : '0.00')
    patterns = [
        # stock.price.toFixed(2)
        (r'(\w+)\.price\.toFixed\((\d+)\)', r"(\1.price != null ? \1.price.toFixed(\2) : '0.00')"),
        # stock.change_pct.toFixed(2)
        (r'(\w+)\.change_pct\.toFixed\((\d+)\)', r"(\1.change_pct != null ? \1.change_pct.toFixed(\2) : '0.00')"),
        # rate.rate.toFixed(4)
        (r'(\w+)\.rate\.toFixed\((\d+)\)', r"(\1.rate != null ? \1.rate.toFixed(\2) : '0.0000')"),
        # idx.change.toFixed(2)
        (r'(\w+)\.change\.toFixed\((\d+)\)', r"(\1.change != null ? \1.change.toFixed(\2) : '0.00')"),
        # summary.vix.toFixed(2)
        (r'(\w+)\.vix\.toFixed\((\d+)\)', r"(\1.vix != null ? \1.vix.toFixed(\2) : '0.00')"),
        # risk.baseline_water_stress.toFixed(2)
        (r'(\w+)\.baseline_water_stress\.toFixed\((\d+)\)', r"(\1.baseline_water_stress != null ? \1.baseline_water_stress.toFixed(\2) : '0.00')"),
        (r'(\w+)\.drought_risk\.toFixed\((\d+)\)', r"(\1.drought_risk != null ? \1.drought_risk.toFixed(\2) : '0.00')"),
        (r'(\w+)\.flood_risk\.toFixed\((\d+)\)', r"(\1.flood_risk != null ? \1.flood_risk.toFixed(\2) : '0.00')"),
        (r'(\w+)\.water_scarcity_2030\.toFixed\((\d+)\)', r"(\1.water_scarcity_2030 != null ? \1.water_scarcity_2030.toFixed(\2) : '0.00')"),
        (r'(\w+)\.overall_risk_score\.toFixed\((\d+)\)', r"(\1.overall_risk_score != null ? \1.overall_risk_score.toFixed(\2) : '0.00')"),
        # metrics.priceImpact.toFixed(2)
        (r'(\w+)\.priceImpact\.toFixed\((\d+)\)', r"(\1.priceImpact != null ? \1.priceImpact.toFixed(\2) : '0.00')"),
        # analysis.impact.toFixed(2)
        (r'(\w+)\.impact\.toFixed\((\d+)\)', r"(\1.impact != null ? \1.impact.toFixed(\2) : '0.00')"),
        # tanker.lat.toFixed(2)
        (r'(\w+)\.lat\.toFixed\((\d+)\)', r"(\1.lat != null ? \1.lat.toFixed(\2) : '0.00')"),
        (r'(\w+)\.lon\.toFixed\((\d+)\)', r"(\1.lon != null ? \1.lon.toFixed(\2) : '0.00')"),
        # stock.volatility
        (r'\((\w+)\.volatility \* 100\)\.toFixed\((\d+)\)', r"(\1.volatility != null ? (\1.volatility * 100).toFixed(\2) : '0.00')"),
        # sector.change_pct
        (r'(\w+)\.change_pct\.toFixed\((\d+)\)', r"(\1.change_pct != null ? \1.change_pct.toFixed(\2) : '0.00')"),
    ]
    
    for pattern, replacement in patterns:
        new_content = re.sub(pattern, replacement, content)
        if new_content != content:
            count = len(re.findall(pattern, content))
            changes += count
            print(f"  Fixed {count} instances of pattern: {pattern}")
            content = new_content
    
    if changes > 0:
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  [OK] Saved {changes} fixes to {filepath}")
            return True
        except Exception as e:
            print(f"  ERROR: Could not write file - {e}")
            return False
    else:
        print(f"  No changes needed")
        return False

# Files to fix
files_to_fix = [
    r"static\index.html",
    r"templates\terminal.html",
]

print("=" * 70)
print("  FIXING toFixed ERRORS IN FINANCE-X TERMINAL")
print("=" * 70)

total_fixed = 0
for filepath in files_to_fix:
    if os.path.exists(filepath):
        if fix_toFixed_in_file(filepath):
            total_fixed += 1
    else:
        print(f"\nFile not found: {filepath}")

print("\n" + "=" * 70)
print(f"  COMPLETE: Fixed {total_fixed} files")
print("=" * 70)
print("\nRestart the server to see changes:")
print("  python server.py")
print()
