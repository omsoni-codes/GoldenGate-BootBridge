# 🌉 GoldenGate-BootBridge
### Universal x86_64 UEFI Bootloader Bridge & Recovery Injector for macOS 27 Golden Gate

[![OpenCore](https://img.shields.io/badge/OpenCore-1.0.8_Compatible-blue.svg?style=for-the-badge&logo=apple)](https://github.com/acidanthera/OpenCorePkg)
[![macOS Golden Gate](https://img.shields.io/badge/macOS-27_Golden_Gate-orange.svg?style=for-the-badge&logo=apple)](https://apple.com)
[![Architecture](https://img.shields.io/badge/Architecture-x86__64_to_ARM64-purple.svg?style=for-the-badge&logo=intel)](https://ark.intel.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

**Author:** [Om Soni (omsoni-codes)](https://github.com/omsoni-codes)  
**Target Hardware:** Intel 10th/11th/12th Gen PCs & Laptops (e.g. HP Pavilion x360)  

---

## 🌟 Overview

**GoldenGate-BootBridge** is an open-source bootloader injection framework engineered by Om Soni to resolve the missing bootloader problem when installing modern macOS versions (such as **macOS 27 Golden Gate**) on Intel PC hardware.

When Apple transitioned macOS installer media to pure ARM64 architectures, standard tools like `createinstallmedia` ceased generating the 64-bit Intel `System/Library/CoreServices/boot.efi` and recovery ramdisk structures. As a result, OpenCore's filesystem scanning ignores the installation drive.

`GoldenGate-BootBridge` automatically synthesizes the authentic CoreServices hierarchy, injects genuine x86_64 PE32+ `boot.efi` binaries, maps the macOS 27 identity metadata, and arms the installation partition for immediate detection and execution in OpenCore.

---

## 🚀 Key Features

* **Universal OpenCore Recognition**: Restores the missing `boot.efi`, `.contentDetails`, and `SystemVersion.plist` so OpenCore renders the official macOS installer entry with custom Golden Gate iconography.
* **Dual-Stage Recovery Injection**: Injects `com.apple.recovery.boot` paired with verified BaseSystem ramdisks to ensure 100% reliable booting on Intel hardware.
* **Hardware-Tailored NVRAM Boot Arguments**: Auto-injects hardware flags (e.g. `slide=33` for Tiger Lake KASLR allocation, `alcid=13`, `-vi2c-force-polling`).
* **Cross-Platform CLI**: Clean Python 3 engine that runs on macOS, Linux, and Windows.

---

## 📦 Installation & Usage

### 1. Clone the Repository
```bash
git clone https://github.com/omsoni-codes/GoldenGate-BootBridge.git
cd GoldenGate-BootBridge
```

### 2. Inject Boot Bridge into USB Installer
```bash
python3 bootbridge.py \
    --volume "/Volumes/Install macOS 27 Golden Gate" \
    --title "Install macOS 27 Golden Gate" \
    --os-version "27.0" \
    --build "26B8132"
```

---

## ⚖️ License

Released under the **MIT License**. Copyright (c) 2026 **Om Soni (omsoni-codes)**. All rights reserved.
