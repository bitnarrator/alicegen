#!/usr/bin/env python3
"""AVM-Alice-PICs nach den statisch rekonstruierten Setup-Regeln erzeugen.

Python 3.8+, keine Zusatzpakete.

Beispiele:
    python avm_alice_generator.py
    python avm_alice_generator.py --count 25 --product 01461
    python avm_alice_generator.py --mode update --version 021219
    python avm_alice_generator.py --mode install
    python avm_alice_generator.py --count 100 > codes.txt

Die Regeln wurden aus Binary.AVMSetupDLL rekonstruiert. Die erzeugten Codes
wurden nicht in einem Installationslauf getestet. Eine separate Pruefung auf
Vorinstallation oder Original-CD bleibt bestehen. Ein Code ist kein
Nachweis einer Lizenzberechtigung.
"""

import argparse
import random
import re
from typing import List


VERSIONS = (
    "990702", "991109", "000114", "000417",
    "001116", "010108", "021219", "030812",
)
PRODUCTS = ("01460", "01461")
FORMAT = re.compile(r"[0-9]{3}\.[0-9]{3}/[0-9]{3}\.[0-9]{3}/[0-9]{3}\.[0-9]{3}")


def check_options(product: str, version: str, mode: str) -> None:
    if product not in PRODUCTS:
        raise ValueError("Produktkennung muss 01460 oder 01461 sein.")
    if mode not in ("install", "update"):
        raise ValueError("Modus muss install oder update sein.")
    if version not in VERSIONS:
        raise ValueError("Unbekannte Versionskennung.")
    if mode == "install" and version != "030812":
        raise ValueError("Bei Neuinstallation ist nur Version 030812 zulaessig.")


def build_code(prefix: str, product: str = "01460",
               version: str = "030812", mode: str = "update") -> str:
    """Code aus genau sechs Ziffern und den gewaehlten Kennungen bilden."""
    check_options(product, version, mode)
    if re.fullmatch(r"[0-9]{6}", prefix) is None:
        raise ValueError("Praefix muss aus genau sechs ASCII-Ziffern bestehen.")
    # Die DLL vergleicht das ERSTE Zeichen der dezimalen Ziffernsumme.
    # Kein Modulo 10 und keine wiederholte Quersummenbildung!
    checksum = str(sum(int(digit) for digit in prefix))[0]
    middle = checksum + product
    return (f"{prefix[:3]}.{prefix[3:]}/"
            f"{middle[:3]}.{middle[3:]}/"
            f"{version[:3]}.{version[3:]}")


def validate_code(code: str, mode: str = "update") -> bool:
    """Prueft die rekonstruierten Regeln; fuehrt keine Aktivierung durch."""
    if FORMAT.fullmatch(code) is None:
        return False
    digits = code.replace(".", "").replace("/", "")
    try:
        expected = build_code(digits[:6], digits[7:12], digits[12:], mode)
    except ValueError:
        return False
    return code == expected


def generate_codes(count: int = 10, product: str = "01460",
                   version: str = "030812", mode: str = "update") -> List[str]:
    """Unterschiedliche Praefixe ohne Wiederholung zufaellig auswaehlen."""
    check_options(product, version, mode)
    if not 1 <= count <= 1_000_000:
        raise ValueError("Anzahl muss zwischen 1 und 1000000 liegen.")
    prefixes = random.SystemRandom().sample(range(1_000_000), count)
    return [build_code(f"{value:06d}", product, version, mode)
            for value in prefixes]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="AVM-Alice-PIC-Generator nach rekonstruierten Setup-Regeln.",
        epilog="Separate Original-CD-/Vorinstallationspruefung bleibt bestehen.",
    )
    parser.add_argument("-n", "--count", type=int, default=10,
                        help="Anzahl unterschiedlicher Codes (Standard: 10)")
    parser.add_argument("--product", choices=PRODUCTS, default="01460",
                        help="Produktkennung (Standard: 01460)")
    parser.add_argument("--version", choices=VERSIONS, default="030812",
                        help="Versionskennung (Standard: 030812)")
    parser.add_argument("--mode", choices=("install", "update"), default="update",
                        help="Installationsmodus (Standard: update)")
    args = parser.parse_args()
    try:
        codes = generate_codes(args.count, args.product, args.version, args.mode)
    except ValueError as exc:
        parser.error(str(exc))
    for code in codes:
        print(code)


if __name__ == "__main__":
    main()
