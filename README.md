# Soplos GRUB Editor

[![License: GPL-3.0+](https://img.shields.io/badge/License-GPL--3.0%2B-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Version](https://img.shields.io/badge/version-2.0.1-green.svg)]()

Advanced graphical editor for GRUB2 configuration, compatible with XFCE, Plasma and GNOME.

*Editor gráfico avanzado para la configuración de GRUB2, compatible con XFCE, Plasma y GNOME.*

## 📝 Description

A GTK3 graphical interface to configure and customize the GRUB2 bootloader: entries, themes, fonts, backgrounds, advanced parameters and more, with complete internationalization support.

## ✨ Features

- 🗂️ Visual editing of GRUB2 configuration
- 🎨 Theme and background management and installation
- 🔤 Custom font conversion and installation
- 📝 Custom boot entry management
- ⚙️ Advanced kernel parameter configuration
- 💾 Automatic backup and restore
- 🌍 Complete internationalization (8 languages)
- 🖥️ Compatible with XFCE, Plasma and GNOME
- 🌊 **Full support for Wayland and X11**
- ⌨️ Keyboard shortcuts for all actions

## 📸 Screenshots

![General Configuration](https://raw.githubusercontent.com/SoplosLinux/soplos-grub-editor/main/assets/screenshots/screenshot1.png)
*General Configuration*

![Boot Entries Management](https://raw.githubusercontent.com/SoplosLinux/soplos-grub-editor/main/assets/screenshots/screenshot2.png)
*Boot Entries Management*

![Theme Selector](https://raw.githubusercontent.com/SoplosLinux/soplos-grub-editor/main/assets/screenshots/screenshot3.png)
*Theme Selector*

![Background Selector](https://raw.githubusercontent.com/SoplosLinux/soplos-grub-editor/main/assets/screenshots/screenshot4.png)
*Background Selector*

![Font Selector](https://raw.githubusercontent.com/SoplosLinux/soplos-grub-editor/main/assets/screenshots/screenshot5.png)
*Font Selector*

## 🛠️ Requirements

- Python 3.8+
- GTK 3.0
- GRUB 2.x installed
- Dependencies: PyGObject, pycairo, python-xlib, polib, python-dbus, Pillow

## 📥 Installation

```bash
# System dependencies
sudo apt install python3-gi gir1.2-gtk-3.0 python3-gi-cairo grub2-common pkexec imagemagick python3-cairo python3-xlib python3-polib python3-dbus python3-pil

# Python installation
pip3 install -r requirements.txt

# Manual installation
sudo python3 setup.py install

# Install desktop files and icons
sudo cp assets/com.soplos.grubeditor.desktop /usr/share/applications/
sudo cp assets/icons/com.soplos.grubeditor.png /usr/share/icons/hicolor/128x128/apps/
sudo cp debian/com.soplos.grubeditor.metainfo.xml /usr/share/metainfo/
sudo update-desktop-database
sudo gtk-update-icon-cache /usr/share/icons/hicolor/
```

## 🚀 Usage

```bash
# Run the application
soplos-grub-editor
```

The application will automatically request administrator privileges using `pkexec`.

## 🌊 Wayland Compatibility

The application is **fully compatible with Wayland** and works perfectly on:

- **Plasma 6 + Wayland** (Soplos Linux Tyson)
- **GNOME + Wayland**
- **Sway** and other Wayland compositors
- **X11** (all traditional environments)

### Wayland Specific Features:
- ✅ Automatic window protocol detection
- ✅ Automatic theme application (including dark theme on Plasma 6)
- ✅ Correct scaling on HiDPI monitors
- ✅ Native integration with the compositor

### Theme Troubleshooting:

If the application is not using the correct theme:

```bash
# Force dark theme
GTK_THEME=Adwaita:dark soplos-grub-editor

# Force light theme
GTK_THEME=Adwaita soplos-grub-editor

# For Plasma with Breeze theme
GTK_THEME=Breeze-Dark soplos-grub-editor
```

## 🖥️ Main Features

- **General**: Timeout, default entry, resolution, kernel parameters, OS detection
- **Appearance**: Themes, fonts, colors, backgrounds
- **Entries**: Add, edit and manage custom boot entries
- **Security**: Automatic backups before applying changes
- **Validation**: Syntax and structure verification before saving

## 🌐 Supported Languages

- 🇪🇸 Spanish
- 🇺🇸 English
- 🇵🇹 Portuguese
- 🇫🇷 French
- 🇩🇪 German
- 🇮🇹 Italian
- 🇷🇴 Romanian
- 🇷🇺 Russian

## 🐧 Distribution Compatibility

- ✅ **Soplos Linux Tyson** (Plasma 6 + Wayland)
- ✅ Ubuntu/Debian (GNOME/X11/Wayland)
- ✅ Fedora (GNOME/KDE/Wayland)
- ✅ Arch Linux (any DE)
- ✅ openSUSE (KDE/GNOME)

## 📄 License

This project is licensed under [GPL-3.0+](https://www.gnu.org/licenses/gpl-3.0.html).

## 👥 Developers

Developed by Sergi Perich

## 🔗 Links

- [Website](https://soplos.org)
- [Report Issues](https://github.com/SoplosLinux/soplos-grub-editor/issues)
- [Documentation](https://soplos.org/docs/soplos-grub-editor)

## 🆕 New in version 2.0.1 (March 7, 2026)

### Fixes
- **Robust Theme Management**: Prevents system conflicts by reliably disabling background defaults from Debian and Soplos scripts.
- **Cache Cleanup**: Solves the "invalid argument" GRUB crash by deleting stale progressive JPEG `.background_cache` files.
- **Smart UI Automation**: Automatically grays out and unchecks the "Show boot menu" option when Timeout is exactly 0.

## 🆕 New in version 2.0.0 (January 10, 2026)

### New Features
- **Complete Internationalization** - Native support for 8 languages (ES, EN, DE, FR, IT, PT, RO, RU)
- **Smart Light/Dark Theme Detection** - Compatible with GNOME, KDE and XFCE
- **Improved Desktop & Environment Detection** - Accurate detection of Wayland/X11 and DE
- **Refined UI Layout** - Compact two-column design for advanced options
- **GRUB Theme Installer/Remover** - Support for .tar.gz, .zip, .tar.xz
- **UUID Option** - Control of GRUB_DISABLE_LINUX_UUID
- **Expanded Resolutions** - 16:9, 16:10, 4:3 and 4K

### Improvements
- GRUB configuration without duplicate lines
- Colors loaded from real GRUB values
- Theme preview with jpg/png support

### Documentation
- Man page added
- Debian Copyright added
- Metainfo updated in 8 languages

## 🆕 New in version 1.0.4 (July 27, 2025)

- Program icon changed.

## 🆕 New in version 1.0.3 (July 18, 2025)

- Metainfo update for AppStream/DEP-11 compliance.
- Renamed screenshots to screenshot1.png, screenshot2.png, etc.
- Minor documentation and metadata improvements.
- No functional changes.

## 🆕 New in version 1.0.2 (June 15, 2025)

- Complete Internationalization (8 languages)
- Dynamic and robust translation system
- Improvements in theme and font management
- Structure and performance optimization

## 🆕 New in version 1.0.1 (June 14, 2025)

- Improvements in font conversion and installation
- Stability improvements and bug fixes

## 🆕 New in version 1.0.0 (June 13, 2025)

- Initial stable release
- Complete GRUB2 configuration management
- Support for custom themes, fonts and entries