# alicegen
AVM Alice PIC Generator

⚠️ ATTENTION: Built with AI

# AVM Alice PIC Generator

A dependency-free Python generator and validator for AVM Alice Product Identification Codes (PICs), based on static analysis of the AVM Alice 3.00.00 installer.

This README documents the reconstructed PIC rules, the separate original-CD check, and the use of `avm_alice_generator.py`.

## Requirements

- Python 3.8 or newer.
- No third-party Python packages.
- The `avm_alice_generator.py` script in your working folder or Python import path.

The generator can run on a modern computer independently of the machine used to install AVM Alice. On Windows, use `py -3` if `python` is unavailable. On Linux or macOS, use `python3` as needed.

## Quick start

Generate ten different codes using product `01460`, release `030812`, and update mode:

```shell
python avm_alice_generator.py
```

Choose a count and product identifier:

```shell
python avm_alice_generator.py --count 25 --product 01461
```

Generate codes for an older release in update mode:

```shell
python avm_alice_generator.py --mode update --version 021219
```

Use the new-installation rules:

```shell
python avm_alice_generator.py --mode install
```

Save one code per line to a text file:

```shell
python avm_alice_generator.py --count 100 > codes.txt
```

`>` replaces an existing output file. `>>` appends instead. Codes are unique within a single generation call for the selected identifiers; separate calls can produce duplicates.

## Command-line options

| Option | Default | Accepted values / behavior |
| --- | --- | --- |
| `-n`, `--count` | `10` | Integer from `1` to `1000000`. |
| `--product` | `01460` | `01460` or `01461`. |
| `--version` | `030812` | One of the eight release identifiers below. |
| `--mode` | `update` | `update` or `install`. New-installation mode requires `030812`. |
| `-h`, `--help` | — | Show usage and exit. |

The script's help and error messages are currently in German. Invalid arguments produce an error and exit status `2`.

The `--mode` option selects the generator's validation rules. It does not change the installer package or its release flags.

## PIC analysis

### Format

```text
ABC.DEF/GHI.JKL/MNO.PQR
```

The PIC contains **18 digits and five separators**, for a total of **23 characters**. Leading zeros must be preserved. Dots and slashes must appear exactly as shown.

| Field | Meaning / validation |
| --- | --- |
| `ABCDEF` | Six-digit prefix used to calculate the checksum. |
| `G` | First character of the decimal representation of the sum of the six prefix digits. |
| `HIJKL` | Product identifier: `01460` or `01461`. |
| `MNOPQR` | Release identifier, compared against a fixed list. |

### Checksum

The checksum is calculated as follows:

```python
checksum = str(sum(int(digit) for digit in prefix))[0]
```

The installer uses the **first character** of the sum, rather than modulo 10 or a repeated digit sum.

For example:

```text
Prefix:             123456
Digit sum:          1 + 2 + 3 + 4 + 5 + 6 = 21
Checksum character: 2
Product identifier: 01460
Release identifier: 030812
Result:             123.456/201.460/030.812
```

For prefix `000000`, the checksum character is `0`. For prefix `999999`, the sum is `54`, so the checksum character is `5`.

### Release identifiers and installation modes

| Mode | Installer parameter `AVM_DLLPARAM_1` | Accepted release identifiers |
| --- | --- | --- |
| New installation | `2` | `030812` only. |
| Update | `3` | `990702`, `991109`, `000114`, `000417`, `001116`, `010108`, `021219`, `030812`. |

The supplied installer is configured as an update package with `RELFLAG_UPDATE=1`.

The release identifiers resemble date codes. Their meaning has not been independently confirmed; the validator performs exact string comparisons.

### Installer integration

The PIC validator is exported as `_CheckPID@4` in `Binary.AVMSetupDLL`, at RVA `0x1000`.

The installer uses `PIDKEY` / `ProductID` for the supplied code and records the validation result in `AVM_PIDKEY_VALID`. It can also attempt to recover an existing code from an earlier installation, including the `CDKey` value under:

```text
HKEY_LOCAL_MACHINE\SOFTWARE\AVM\Alice
```

No online activation or hardware, username, or organization binding was identified in the inspected PIC validation function.

## Original-CD check

The update package has a **separate original-CD check**. If no suitable prior installation is detected, a CD must be present or mounted as an optical drive, with a file named **`Alice.ico` in its root directory**:

```text
D:\Alice.ico
```

`D:` is an example; the installer enumerates available drives.

The reconstructed `_CheckForOriginalCD@4` routine:

1. Enumerates logical drives using `GetLogicalDriveStringsA`.
2. Selects drives for which `GetDriveTypeA` returns `DRIVE_CDROM` (`5`).
3. Looks for `Alice.ico` directly in the drive root using `GetFileAttributesA`.
4. Accepts the entry if it exists and is not a directory.

**The contents of `Alice.ico` are not checked by this routine.** The file can contain arbitrary data, including no data; it does not have to be a valid icon. The inspected routine does not compare a file hash, CD volume label, or disc serial number.

### Preparing test media

1. Create a file named exactly `Alice.ico` in the root of the folder used to build your test disc or ISO.
2. Create a data CD or ISO image with that file at its root.
3. Insert the disc or mount the image so that the **Windows system running the installer** sees it as a CD/DVD drive. For a virtual machine, attach the ISO to that VM's virtual optical drive.
4. Confirm that the file is visible as, for example, `D:\Alice.ico`, then continue the setup.

A normal folder, an extracted ISO, or a regular disk drive containing the file does not satisfy the drive-type check. The medium must be presented as an optical drive.

The generator does not create or mount an ISO and does not change this check. A code passing PIC validation and the installer detecting acceptable CD media are independent conditions.

## Python API

Place the generator beside your own Python program, or make it available on your Python import path:

```python
from avm_alice_generator import (
    build_code,
    generate_codes,
    validate_code,
)

code = build_code(
    "123456",
    product="01460",
    version="030812",
    mode="update",
)
print(code)  # 123.456/201.460/030.812
print(validate_code(code))  # True

codes = generate_codes(
    count=10,
    product="01461",
    version="030812",
    mode="install",
)
assert len(codes) == len(set(codes)) == 10
```

| Function | Behavior |
| --- | --- |
| `build_code(prefix, product="01460", version="030812", mode="update")` | Build one code from a six-digit prefix string. Invalid input raises `ValueError`. |
| `generate_codes(count=10, product="01460", version="030812", mode="update")` | Return a list using randomly sampled prefixes without replacement. Invalid options or an out-of-range count raise `ValueError`. |
| `validate_code(code, mode="update")` | Return `True` or `False` according to the reconstructed rules. |

Importing the module does not print or generate codes automatically. This version provides validation through the Python API, not through a command-line validation option.

## Troubleshooting

| Problem | Check |
| --- | --- |
| Python is not recognized | Try `py -3` on Windows or `python3` on Linux/macOS. Confirm Python 3.8+ is available. |
| Python cannot open the script | Change to the script's folder or specify its full path. |
| An older release fails in `install` mode | Use `--mode update`, or select release `030812` for `install` mode. |
| Setup still requests the original CD | Verify that the installer sees an optical drive and that `Alice.ico` is a file in that drive's root. A folder or regular disk is insufficient. |
| A PIC is rejected by setup | Copy all 23 characters exactly and confirm that the installer package matches the analyzed version and mode. |

## Verification and scope

The Python implementation has been checked for checksum edge cases, all 16 product/release combinations in update mode, uniqueness within generated batches, rejection of older releases in new-installation mode, and command-line output/error behavior.

The findings apply to the supplied AVM Alice 3.00.00 installer streams and the generated script. A complete installer run has not been performed in this environment. The CD behavior is based on static analysis of the separate CD-check routine; runtime acceptance of particular mounted media has not been tested here.

Sources: the supplied `AVM Alice.zip`, the static analysis recorded in this conversation, and `avm_alice_generator.py`.

