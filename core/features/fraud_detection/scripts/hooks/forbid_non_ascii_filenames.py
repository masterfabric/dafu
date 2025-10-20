#!/usr/bin/env python3
import subprocess, sys

def is_ascii(s: str) -> bool:
    try:
        s.encode("ascii")
        return True
    except UnicodeEncodeError:
        return False

def staged_paths():
    res = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
        capture_output=True, text=True, check=True
    )
    return [p for p in res.stdout.splitlines() if p]

def main():
    bad = [p for p in staged_paths() if not is_ascii(p)]
    if bad:
        print("❌ Non-ASCII karakter içeren dosya/dizin adı bulundu. ASCII dışı karakterlere izin yok:\n")
        for p in bad:
            print(f" - {p}")
        print("\nLütfen dosya/dizin adlarını yalnızca ASCII karakterlerle yeniden adlandırın.")
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()
