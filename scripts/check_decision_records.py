import os
import re
import sys

DECISIONS_DIR = "AGENCY/1_PRESENT/DECISIONS"
REQUIRED_FRONTMATTER = {"type", "author", "date", "context", "decision", "status"}
# Note: Using simpler regex matching for headers
REQUIRED_PATTERNS = [
    r"^# .*DECISION RECORD.*",
    r"^> \*\*Meta-Cognition Principle\*\*.*",
    r"^## \d+\. .*CONTEXT.*",
    r"^## \d+\. .*OPTIONS CONSIDERED.*",
    r"^## \d+\. .*THE DECISION.*",
    r"^## \d+\. .*PREDICTED CONSEQUENCES.*",
    r"^## \d+\. .*REVIEW TRIGGER.*"
]

def check_file(filepath):
    print(f"Checking {filepath}...")
    try:
        with open(filepath, 'r') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Could not read file: {e}")
        return False

    if not content.startswith("---"):
        print(f"❌ Missing Frontmatter start marker '---'")
        return False

    parts = content.split("---", 2)
    if len(parts) < 3:
        print(f"❌ Invalid Frontmatter format (missing end marker '---')")
        return False

    frontmatter_block = parts[1]
    body = parts[2]

    # Simple YAML parsing (key: value)
    found_keys = set()
    for line in frontmatter_block.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key = line.split(":", 1)[0].strip()
            found_keys.add(key)

    missing_keys = REQUIRED_FRONTMATTER - found_keys
    if missing_keys:
        print(f"❌ Missing frontmatter keys: {missing_keys}")
        return False

    # Check Headers in Body
    lines = body.splitlines()
    missing_patterns = []

    for pattern in REQUIRED_PATTERNS:
        found = False
        regex = re.compile(pattern, re.IGNORECASE)
        for line in lines:
            if regex.match(line):
                found = True
                break
        if not found:
            missing_patterns.append(pattern)

    if missing_patterns:
        print(f"❌ Missing required content matching patterns: {missing_patterns}")
        return False

    print(f"✅ Passed")
    return True

def main():
    if not os.path.exists(DECISIONS_DIR):
        print(f"Directory {DECISIONS_DIR} not found.")
        sys.exit(1)

    files = [f for f in os.listdir(DECISIONS_DIR) if f.endswith(".md")]
    if not files:
        print("No markdown files found to check.")
        sys.exit(0)

    failed_files = []

    for filename in files:
        filepath = os.path.join(DECISIONS_DIR, filename)
        if not check_file(filepath):
            failed_files.append(filename)

    if failed_files:
        print(f"\n❌ Checks failed for: {', '.join(failed_files)}")
        sys.exit(1)
    else:
        print("\n✅ All Decision Records are compliant!")
        sys.exit(0)

if __name__ == "__main__":
    main()
