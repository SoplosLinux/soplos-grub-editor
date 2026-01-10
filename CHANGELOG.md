# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-01-10

### 🎉 Major Release - Complete Rewrite

#### ✨ New Features
- **Smart Light/Dark Theme Detection** - Automatically detects user theme (GNOME, KDE, XFCE) before privilege elevation
- **GRUB Theme Installer** - Install themes from .tar.gz, .tar.xz, .tar.bz2, .zip archives
- **GRUB Theme Remover** - Remove installed themes with confirmation
- **UUID Option** - Checkbox to enable/disable GRUB_DISABLE_LINUX_UUID
- **Expanded Resolutions** - Support for 16:9, 16:10, 4:3, and legacy resolutions (up to 4K)
- **Enhanced Theme Preview** - Checks for preview.png, preview.jpg, background.png/jpg

#### 🔧 Improvements
- **Rewritten save_config** - Updates existing lines in place, handling commented lines correctly
- **Colors loaded from GRUB** - Color buttons now reflect actual GRUB_COLOR_* values
- **State Synchronization** - read_config() called after save to keep internal state in sync
- **Optimized get_config** - Only sends keys that have changed or already exist

#### 🐛 Fixes
- **Duplicate Lines Removed** - No longer adds duplicate lines to GRUB config
- **Empty Lines Handling** - Prevents accumulation of blank lines
- **Dynamic Preview** - Background preview updates correctly when typing path
- **Default Colors on Disable** - Sets white/black defaults when a theme is disabled

#### 📦 Documentation
- **Man Page Added** - docs/soplos-grub-editor.1
- **Debian Copyright** - debian/copyright
- **Updated Metainfo** - 8 languages with v2.0.0 release notes

## [1.0.4] - 2025-07-27

### 🎨 Changed
- Program icon changed.

## [1.0.3] - 2025-07-18

### 🛠️ Changes
- Metainfo update for AppStream/DEP-11 compliance.
- Renamed screenshots to screenshot1.png, screenshot2.png, etc.
- Minor documentation and metadata improvements.
- No functional changes.

## [1.0.2] - 2025-06-15

### 🌍 Added - Complete Internationalization
- **Dynamic translation system** with on-demand loading
- **8 languages fully supported**:
  - 🇪🇸 Spanish (es) - 100%
  - 🇺🇸 English (en) - 100%
  - 🇫🇷 French (fr) - 100%
  - 🇵🇹 Portuguese (pt) - 100%
  - 🇩🇪 German (de) - 100%
  - 🇮🇹 Italian (it) - 100%
  - 🇷🇺 Russian (ru) - 100%
  - 🇷🇴 Romanian (ro) - 100%
- **Automatic detection** of system language based on `$LANG`
- **Robust fallback system** with English as backup
- **Improved translation API** with optimized `_()` function
- **`set_language()` function** for dynamic language switching
- **`get_available_languages()` function** to list available languages

### 🔧 Improved - Translation System
- **Complete restructuring** of `translations/` module
- **Optimized loading** of translations per language
- **Improved memory management** - only loads necessary language
- **Robust validation** of translation keys
- **Enhanced logging** for translation errors
- **Backwards compatibility** maintained

### 🐛 Fixed - Internationalization
- **Hardcoded strings** completely removed
- **Logging errors** now translated
- **Technical messages** internationalized
- **Generated code comments** translated
- **Configuring `_()` before use** in `main.py`
- **Import optimizations**

### 📁 Changed - File Structure
- **`locale/` directory removed** to avoid conflicts
- **New `translations/` system** more robust
- **Centralized `strings.py`** for management
- **Separate language modules** in `locales/`
- **Modular configuration** improved

### 🚀 Performance
- **On-demand loading** of languages
- **Reduced memory usage** (only active language)
- **Faster application startup**
- **Efficient management** of translations

### 📝 Documentation
- **README.md updated** with language info
- **Metainfo.xml expanded** with full translations
- **Changelog created** with detailed history
- **Improved code comments**
- **API documentation** for translations

### 🛠️ Development
- **Simplified development system** for translations
- **Automatic validation** of language completeness
- **Verification tools** for translations
- **Consistent structure** across languages

## [1.0.1] - 2025-06-14

### 🔧 Improved
- **Font conversion system** more robust
- **Error handling** improved in font installation
- **User Interface** more responsive
- **Theme installation** optimized

### 🐛 Fixed
- Errors in TTF/OTF to PF2 conversion
- Permission issues in `/boot/grub/fonts/`
- UI crashes when loading large themes
- Memory errors when processing fonts

### 📁 Changed
- Improved structure of `utils/` modules
- Import optimization
- Cleanup of duplicate code

## [1.0.0] - 2025-06-13

### 🎉 Initial Release
- **Complete graphical editor** for GRUB2 configuration
- **Intuitive GTK3 interface** with organized tabs
- **GRUB Theme management** - installation and application
- **Font conversion** TTF/OTF → PF2
- **Background wallpaper** configuration
- **Custom boot entries** management
- **Advanced kernel configuration**
- **Automatic OS detection**
- **Automatic backup system**
- **Secure integration** with update-grub

### 🌟 Key Features
- **General Tab**: Timeout, default entry, resolution, kernel params
- **Appearance Tab**: Themes, fonts, colors, backgrounds
- **Entries Tab**: Manage custom boot entries
- **Keyboard shortcuts**
- **Configuration validation**
- **Detailed logging** for debugging

### 🔒 Security
- **Minimum privileges** - only root when necessary
- **Robust input validation**
- **Automatic backups** before changes
- **Integrity verification** of files

### 📦 Packaging
- **Debian package** ready for production
- **.desktop files** with icons
- **AppStream metadata** complete
- **Integration with package managers**

### 🎯 Compatibility
- **Soplos Linux** (main distribution)
- **Ubuntu/Debian** and derivatives
- **GRUB 2.x** in all versions
- **Python 3.8+** with PyGObject

---

## Types of Changes

- **Added** for new features
- **Changed** for changes in existing functionality
- **Deprecated** for features soon to be removed
- **Removed** for now removed features
- **Fixed** for any bug fixes
- **Security** in case of vulnerabilities

## Links

- [1.0.3]: https://github.com/SoplosLinux/soplos-grub-editor/compare/v1.0.2...v1.0.3
- [1.0.2]: https://github.com/SoplosLinux/soplos-grub-editor/compare/v1.0.1...v1.0.2
- [1.0.1]: https://github.com/SoplosLinux/soplos-grub-editor/compare/v1.0.0...v1.0.1
- [1.0.0]: https://github.com/SoplosLinux/soplos-grub-editor/releases/tag/v1.0.0

## Contribute

To report bugs or request features:
- **Issues**: https://github.com/SoplosLinux/soplos-grub-editor/issues
- **Discussions**: https://github.com/SoplosLinux/soplos-grub-editor/discussions
- **Email**: info@soploslinux.com

To contribute translations:
1. Create file `translations/locales/XX.py` (XX = language code)
2. Copy structure from `translations/locales/en.py`
3. Translate all `STRINGS`
4. Add language to `SUPPORTED_LANGUAGES` in `strings.py`
5. Submit Pull Request

## Support

- **Documentation**: https://soplos.org/docs/soplos-grub-editor
- **Community**: https://soplos.org/community
- **Support**: support@soploslinux.com
