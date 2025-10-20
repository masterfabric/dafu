#!/usr/bin/env python3
import sys, pathlib

TURKISH = set("çğıöşüÇĞİÖŞÜ")

def has_non_ascii(text: str) -> list[tuple[int, int, str]]:
    violations = []
    for lineno, line in enumerate(text.splitlines(), 1):
        for colno, ch in enumerate(line, 1):
            # Sadece Türkçe karakterleri kontrol et, emojilere dokunma
            if ch in TURKISH:
                violations.append((lineno, colno, ch))
    return violations

def main():
    any_errors = False
    total_violations = 0
    
    for arg in sys.argv[1:]:
        p = pathlib.Path(arg)
        try:
            text = p.read_text(encoding="utf-8", errors="strict")
        except Exception:
            # İkili/binary veya okunamayan dosyaları atla
            continue
        vios = has_non_ascii(text)
        if vios:
            any_errors = True
            total_violations += len(vios)
            print(f"\n❌ {p} içinde {len(vios)} adet Türkçe karakter bulundu:")
            print("=" * 60)
            
            # Tüm hataları göster
            for i, (lineno, colno, ch) in enumerate(vios, 1):
                # Karakterin görünümünü hazırla
                char_display = ch.encode('unicode_escape').decode('ascii')
                char_name = f"'{ch}'" if len(ch) == 1 else f"'{char_display}'"
                
                # Satır içeriğini al
                lines = text.splitlines()
                if lineno <= len(lines):
                    line_content = lines[lineno - 1]
                    # Satırda karakterin konumunu işaretle
                    marker = " " * (colno - 1) + "^"
                    print(f"  {i:3d}. Satır {lineno:3d}, Sütun {colno:2d}: {char_name}")
                    print(f"       {line_content}")
                    print(f"       {marker}")
                    print()
                else:
                    print(f"  {i:3d}. Satır {lineno:3d}, Sütun {colno:2d}: {char_name}")
            
            print("=" * 60)
    
    if any_errors:
        print(f"\n🚫 TOPLAM {total_violations} adet Türkçe karakter tespit edildi!")
        print("📝 Düzeltme önerileri:")
        print("   • ç → c")
        print("   • ğ → g") 
        print("   • ı → i")
        print("   • ö → o")
        print("   • ş → s")
        print("   • ü → u")
        print("   • Ç → C")
        print("   • Ğ → G")
        print("   • İ → I")
        print("   • Ö → O")
        print("   • Ş → S")
        print("   • Ü → U")
        print("\n💡 Lütfen yukarıdaki karakterleri ASCII karşılıklarıyla değiştirin.")
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()
