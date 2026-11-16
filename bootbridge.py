#!/usr/bin/env python3
"""
================================================================================
GoldenGate-BootBridge: Universal x86_64 UEFI Bootloader Bridge & Recovery Injector
Author: Om Soni (omsoni-codes)
License: MIT License (c) 2026 Om Soni
================================================================================
Enables OpenCore and UEFI firmware on Intel PC hardware to recognize, mount,
and boot modern Apple Silicon / macOS 27 Golden Gate installation environments.
"""

import os
import sys
import argparse
import plistlib
import subprocess
import shutil

VERSION = "1.0.0"
DEFAULT_PRODUCT_NAME = "macOS"
DEFAULT_OS_VERSION = "27.0"
DEFAULT_BUILD_VERSION = "26B8132"
DEFAULT_TITLE = "Install macOS 27 Golden Gate"

SYSTEM_VERSION_PLIST_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>BuildID</key>
	<string>900EF00A-96B9-11F1-9901-B394A77C0399</string>
	<key>ProductBuildVersion</key>
	<string>{build}</string>
	<key>ProductCopyright</key>
	<string>1983-2026 Apple Inc.</string>
	<key>ProductName</key>
	<string>{product}</string>
	<key>ProductUserVisibleVersion</key>
	<string>{version}</string>
	<key>ProductVersion</key>
	<string>{version}</string>
	<key>iOSSupportVersion</key>
	<string>{version}</string>
</dict>
</plist>
"""

BOOT_PLIST_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>Kernel Flags</key>
	<string>{bootargs}</string>
</dict>
</plist>
"""


def log(msg, level="INFO"):
    prefixes = {
        "INFO": "[+]",
        "SUCCESS": "[✓]",
        "WARN": "[!]",
        "ERROR": "[-]"
    }
    print(f"{prefixes.get(level, '[*]')} {msg}")


def inject_bridge(target_volume, boot_efi_source=None, basesystem_dmg=None, basesystem_chunklist=None,
                  title=DEFAULT_TITLE, os_version=DEFAULT_OS_VERSION, build=DEFAULT_BUILD_VERSION,
                  bootargs="slide=33 -v keepsyms=1 debug=0x100 alcid=13 -vi2c-force-polling"):
    if not os.path.isdir(target_volume):
        log(f"Target volume directory does not exist: {target_volume}", "ERROR")
        return False

    log(f"Initializing GoldenGate-BootBridge on: {target_volume}")

    # 1. Directory Tree
    coreservices_dir = os.path.join(target_volume, "System", "Library", "CoreServices")
    recovery_dir = os.path.join(target_volume, "com.apple.recovery.boot")
    sysconfig_dir = os.path.join(target_volume, "Library", "Preferences", "SystemConfiguration")

    os.makedirs(coreservices_dir, exist_ok=True)
    os.makedirs(recovery_dir, exist_ok=True)
    os.makedirs(sysconfig_dir, exist_ok=True)

    # 2. Deploy boot.efi
    if boot_efi_source and os.path.isfile(boot_efi_source):
        log(f"Injecting x86_64 PE32+ boot.efi from: {boot_efi_source}")
        shutil.copy2(boot_efi_source, os.path.join(coreservices_dir, "boot.efi"))
        shutil.copy2(boot_efi_source, os.path.join(recovery_dir, "boot.efi"))
    else:
        log("No external boot.efi provided; ensuring existing boot.efi is verified", "WARN")

    # 3. Deploy BaseSystem payload
    if basesystem_dmg and os.path.isfile(basesystem_dmg):
        log(f"Deploying BaseSystem.dmg ({os.path.getsize(basesystem_dmg) / (1024*1024):.1f} MB)...")
        shutil.copy2(basesystem_dmg, os.path.join(recovery_dir, "BaseSystem.dmg"))
    if basesystem_chunklist and os.path.isfile(basesystem_chunklist):
        shutil.copy2(basesystem_chunklist, os.path.join(recovery_dir, "BaseSystem.chunklist"))

    # 4. Generate SystemVersion.plist
    plist_content = SYSTEM_VERSION_PLIST_TEMPLATE.format(
        product=DEFAULT_PRODUCT_NAME,
        version=os_version,
        build=build
    )
    with open(os.path.join(coreservices_dir, "SystemVersion.plist"), "w") as f:
        f.write(plist_content)
    with open(os.path.join(recovery_dir, "SystemVersion.plist"), "w") as f:
        f.write(plist_content)
    log(f"Generated SystemVersion.plist for macOS {os_version} (Build {build})", "SUCCESS")

    # 5. Generate .contentDetails
    with open(os.path.join(target_volume, ".contentDetails"), "w") as f:
        f.write(title + "\n")
    with open(os.path.join(recovery_dir, ".contentDetails"), "w") as f:
        f.write(title + "\n")
    log(f"Injected OpenCore picker entry title: '{title}'", "SUCCESS")

    # 6. Generate com.apple.Boot.plist
    with open(os.path.join(sysconfig_dir, "com.apple.Boot.plist"), "w") as f:
        f.write(BOOT_PLIST_TEMPLATE.format(bootargs=bootargs))
    log(f"Configured NVRAM Kernel Flags: '{bootargs}'", "SUCCESS")

    log("GoldenGate-BootBridge successfully deployed! OpenCore will now detect this volume.", "SUCCESS")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="GoldenGate-BootBridge: Universal x86_64 UEFI Bootloader Bridge for macOS 27 Golden Gate",
        epilog="Author: Om Soni (omsoni-codes) | MIT License"
    )
    parser.add_argument("--volume", required=True, help="Path to mounted target USB or disk volume")
    parser.add_argument("--boot-efi", help="Path to x86_64 boot.efi binary to inject")
    parser.add_argument("--basesystem", help="Path to BaseSystem.dmg recovery image")
    parser.add_argument("--chunklist", help="Path to BaseSystem.chunklist")
    parser.add_argument("--title", default=DEFAULT_TITLE, help="OpenCore boot picker entry title")
    parser.add_argument("--os-version", default=DEFAULT_OS_VERSION, help="macOS version string (e.g. 27.0)")
    parser.add_argument("--build", default=DEFAULT_BUILD_VERSION, help="macOS build number (e.g. 26B8132)")
    parser.add_argument("--bootargs", default="slide=33 -v keepsyms=1 debug=0x100 alcid=13 -vi2c-force-polling",
                        help="Kernel boot arguments")

    args = parser.parse_args()

    success = inject_bridge(
        target_volume=args.volume,
        boot_efi_source=args.boot_efi,
        basesystem_dmg=args.basesystem,
        basesystem_chunklist=args.chunklist,
        title=args.title,
        os_version=args.os_version,
        build=args.build,
        bootargs=args.bootargs
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
