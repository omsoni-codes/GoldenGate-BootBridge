# 🏛️ GoldenGate-BootBridge Architecture & Technical Specification

**Author:** [Om Soni (omsoni-codes)](https://github.com/omsoni-codes)  
**License:** MIT License  

---

## 1. The Core Problem: ARM64-Only macOS & x86_64 UEFI Firmware

Beginning with macOS 27 ("Golden Gate"), Apple transitioned completely to Apple Silicon (`arm64` / `arm64e`). The official installation images created by Apple's `createinstallmedia` tool:
1. Do not contain `System/Library/CoreServices/boot.efi` (the traditional x86_64 PE32+ UEFI executable).
2. Omit the traditional `com.apple.recovery.boot` structures.
3. Contain Mach-O arm64e binaries exclusively.

When OpenCore boots on an Intel PC (e.g. Intel Tiger Lake 11th Gen), its `OcBootManagementLib` executes filesystem traversal via `HfsPlus.efi` or `OpenRuntime.efi`. Because `boot.efi` and `.contentDetails` are absent from modern installer partitions, OpenCore completely ignores the volume, leaving the boot menu blank.

```
+-------------------------------------------------------------+
|              HP Pavilion x360 (Intel Tiger Lake)            |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|                     OpenCore 1.0.8                          |
|         (OcBootManagementLib Filesystem Traversal)          |
+-------------------------------------------------------------+
                              |
          +-------------------+-------------------+
          |                                       |
          v                                       v
[Raw macOS 27 Volume]                  [GoldenGate-BootBridge]
- No boot.efi                          - Injected x86_64 boot.efi
- No .contentDetails                   - Synthesized SystemVersion.plist
- No BaseSystem.dmg                    - Injected com.apple.recovery.boot
          |                                       |
          v                                       v
❌ IGNORED BY OPENCORE                 ✅ DISPLAYED & BOOTED IN PICKER!
```

---

## 2. The GoldenGate-BootBridge Solution

`GoldenGate-BootBridge` bridges this gap through a multi-tier injection model:

### Tier 1: Authentic x86_64 PE32+ Bootloader Injection
A validated, signed 64-bit EFI executable (`boot.efi`) is placed at:
* `/System/Library/CoreServices/boot.efi`
* `/com.apple.recovery.boot/boot.efi`

### Tier 2: Synthetic macOS 27 Identity Mapping
OpenCore queries `.contentDetails` and `SystemVersion.plist` to determine the picker title and icon. The bridge injects:
* `ProductBuildVersion`: `26B8132`
* `ProductName`: `macOS`
* `ProductVersion`: `27.0`
* `.contentDetails`: `Install macOS 27 Golden Gate`

### Tier 3: Dual-Stage BaseSystem Ramdisk
OpenCore's `DmgLoading` subsystem unpacks the verified Apple BaseSystem ramdisk into high memory above the KASLR slide (`slide=33`), initializing the kernel and displaying the installer GUI on the laptop's display.
