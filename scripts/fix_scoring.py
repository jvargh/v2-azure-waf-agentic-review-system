"""Fix the scoring penalty logic"""
import re

with open('backend/server.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the penalty section
old_pattern = r"""    # Apply negative indicator penalty - if document mentions many things as "not configured" or "missing"
    # This is key: comprehensive documentation showing gaps should score LOWER, not higher
    if negative_mentions > 5:
        # Aggressively penalize - each gap significantly reduces score
        # With 50\+ gaps, this should bring scores down to 20-40 range
        negative_penalty = min\(0\.70, negative_mentions / 50\)  # Up to 70% reduction
        adjusted_score = int\(adjusted_score \* \(1 - negative_penalty\)\)
        print\(f"\[conservative_score\] \{code\}: \{negative_mentions\} gaps found, applying \{int\(negative_penalty\*100\)\}% penalty"\)"""

new_text = """    # Apply penalty for ACTUAL gaps (positive negations already filtered)
    if negative_mentions > 3:
        negative_penalty = min(0.70, (negative_mentions - 3) / 70)
        adjusted_score = int(adjusted_score * (1 - negative_penalty))
        print(f"[conservative_score] {code}: {negative_mentions} gaps found, applying {int(negative_penalty*100)}% penalty")
    elif negative_mentions > 0:
        negative_penalty = negative_mentions * 0.02
        adjusted_score = int(adjusted_score * (1 - negative_penalty))
        print(f"[conservative_score] {code}: {negative_mentions} minor gaps, applying {int(negative_penalty*100)}% penalty")
    else:
        if coverage_pct > 70 and corpus_size > 500:
            adjusted_score = min(100, int(adjusted_score * 1.15))
            print(f"[conservative_score] {code}: no gaps, clean architecture bonus applied")"""

content = re.sub(old_pattern, new_text, content, flags=re.MULTILINE)

# Also fix the density multiplier comment
content = content.replace(
    "# Apply density multiplier - but cap it lower\n    # Even comprehensive docs shouldn't score high if they document gaps\n    adjusted_score = int(raw_score * density_multiplier * 0.8)  # Additional 20% reduction",
    "# Apply density multiplier\n    adjusted_score = int(raw_score * density_multiplier)"
)

with open('backend/server.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Scoring logic updated successfully!")
