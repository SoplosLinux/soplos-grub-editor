"""Minimal environment detection for Soplos GRUB Editor.

Focused, small implementation that:
- seeds hints from `SOPLOS_ENV_FILE` written by the non-privileged launcher
- prefers `SOPLOS_*` overrides when present
- uses common XDG variables
- falls back to `loginctl` when elevated to determine session type
"""

import os
import subprocess
from typing import Dict, Optional
from enum import Enum
from pathlib import Path
import pwd
import configparser
import re


class DesktopEnvironment(Enum):
    GNOME = "gnome"
    KDE = "kde"
    XFCE = "xfce"
    UNKNOWN = "unknown"


class DisplayProtocol(Enum):
    X11 = "x11"
    WAYLAND = "wayland"
    UNKNOWN = "unknown"


class ThemeType(Enum):
    LIGHT = "light"
    DARK = "dark"
    UNKNOWN = "unknown"


class EnvironmentDetector:
    def __init__(self):
        self._desktop = DesktopEnvironment.UNKNOWN
        self._display = DisplayProtocol.UNKNOWN
        self._theme = ThemeType.LIGHT
        self._gtk_theme_name = None

    def detect_all(self) -> Dict[str, str]:
        # Load parent-provided hints if available (kept for backward compat)
        self.load_parent_hints()

        self._detect_desktop()
        self._detect_display()
        self._detect_theme()

        return {
            'desktop_environment': self._desktop.value,
            'display_protocol': self._display.value,
            'theme_type': self._theme.value,
            'gtk_theme_name': self._gtk_theme_name,
        }

    def _detect_desktop(self):
        d = os.environ.get('SOPLOS_DESKTOP') or os.environ.get('XDG_CURRENT_DESKTOP')
        if not d:
            d = os.environ.get('XDG_SESSION_DESKTOP') or os.environ.get('DESKTOP_SESSION', '')
        d = (d or '').lower()
        if ':' in d:
            d = d.split(':', 1)[0]
        if 'gnome' in d:
            self._desktop = DesktopEnvironment.GNOME
            return
        if 'kde' in d or 'plasma' in d:
            self._desktop = DesktopEnvironment.KDE
            return
        if 'xfce' in d:
            self._desktop = DesktopEnvironment.XFCE
            return

        # Small fallback: check a few common process names
        for name, env in (('gnome-shell', DesktopEnvironment.GNOME), ('plasmashell', DesktopEnvironment.KDE), ('xfwm4', DesktopEnvironment.XFCE)):
            try:
                if subprocess.run(['pgrep', '-x', name], capture_output=True).returncode == 0:
                    self._desktop = env
                    return
            except Exception:
                pass

    def _detect_display(self):
        st = (os.environ.get('SOPLOS_SESSION_TYPE') or os.environ.get('XDG_SESSION_TYPE') or '').lower()
        if not st:
            if os.environ.get('WAYLAND_DISPLAY'):
                st = 'wayland'
            elif os.environ.get('DISPLAY'):
                st = 'x11'

        if st == 'wayland':
            self._display = DisplayProtocol.WAYLAND
            return
        if st == 'x11':
            self._display = DisplayProtocol.X11
            return

        # When elevated, try to query the active user's session via loginctl
        sudo_user = os.environ.get('SUDO_USER')
        if os.geteuid() == 0 and sudo_user:
            try:
                # Find active session for user
                r = subprocess.run(['loginctl', 'list-sessions', '--no-legend'], capture_output=True, text=True, timeout=2)
                if r.returncode == 0 and r.stdout:
                    for line in r.stdout.splitlines():
                        parts = line.split()
                        # ID UID USER SEAT TTY
                        if len(parts) >= 3 and parts[2] == sudo_user:
                            sid = parts[0]
                            # Check if active
                            r_state = subprocess.run(['loginctl', 'show-session', sid, '-p', 'State', '--value'], capture_output=True, text=True, timeout=1)
                            if r_state.returncode == 0 and 'active' in (r_state.stdout or '').lower():
                                r2 = subprocess.run(['loginctl', 'show-session', sid, '-p', 'Type', '--value'], capture_output=True, text=True, timeout=1)
                                if r2.returncode == 0:
                                    t = (r2.stdout or '').strip().lower()
                                    if 'wayland' in t:
                                        self._display = DisplayProtocol.WAYLAND
                                        return
                                    if 'x11' in t or 'xorg' in t:
                                        self._display = DisplayProtocol.X11
                                        return
            except Exception:
                pass

            # Fallback: inspect the real user's runtime directory for wayland sockets
            try:
                if sudo_user:
                    try:
                        pu = pwd.getpwnam(sudo_user)
                        user_run = Path(f"/run/user/{pu.pw_uid}")
                        if user_run.exists():
                            for p in user_run.iterdir():
                                if p.name.startswith('wayland-'):
                                    self._display = DisplayProtocol.WAYLAND
                                    return
                    except Exception:
                        pass
            except Exception:
                pass

    def _get_real_user_home(self) -> Path:
        """Get the home directory of the real user when running as root."""
        if os.geteuid() == 0:
            # Check SUDO_USER (from sudo)
            sudo_user = os.environ.get('SUDO_USER')
            if sudo_user:
                try:
                    return Path(pwd.getpwnam(sudo_user).pw_dir)
                except Exception:
                    pass
            
            # Check PKEXEC_UID (from pkexec)
            pkexec_uid = os.environ.get('PKEXEC_UID')
            if pkexec_uid:
                try:
                    uid = int(pkexec_uid)
                    return Path(pwd.getpwuid(uid).pw_dir)
                except Exception:
                    pass
                    
        return Path.home()

    def _detect_theme(self):
        # Parent override is authoritative
        t = (os.environ.get('SOPLOS_THEME_TYPE') or '').lower()
        if t == 'dark':
            self._theme = ThemeType.DARK
            return
        if t == 'light':
            self._theme = ThemeType.LIGHT
            return

        # Try Gtk.Settings when available
        try:
            import gi
            gi.require_version('Gtk', '3.0')
            from gi.repository import Gtk
            s = Gtk.Settings.get_default()
            if s is not None:
                try:
                    if s.get_property('gtk-application-prefer-dark-theme'):
                        self._theme = ThemeType.DARK
                        return
                except Exception:
                    pass
                try:
                    # Fallback: inspect theme name for 'dark' substring
                    tn = s.get_property('gtk-theme-name')
                    self._gtk_theme_name = tn
                    if tn and isinstance(tn, str) and 'dark' in tn.lower():
                        self._theme = ThemeType.DARK
                        return
                except Exception:
                    pass
        except Exception:
            pass

        # Next fallback: check GTK config files (per-user and system)
        try:
            cfg = configparser.ConfigParser()
            
            # Use real user home for config detection
            home = self._get_real_user_home()
            user_cfg = home / '.config' / 'gtk-3.0' / 'settings.ini'
            
            sys_cfg = Path('/etc/gtk-3.0/settings.ini')
            read_files = cfg.read([str(user_cfg), str(sys_cfg)])
            if cfg.has_option('Settings', 'gtk-application-prefer-dark-theme'):
                v = cfg.get('Settings', 'gtk-application-prefer-dark-theme')
                if v.strip() in ('1', 'true', 'True'):
                    self._theme = ThemeType.DARK
                    return
            if cfg.has_option('Settings', 'gtk-theme-name'):
                tn = cfg.get('Settings', 'gtk-theme-name')
                self._gtk_theme_name = tn
                if tn and 'dark' in tn.lower():
                    self._theme = ThemeType.DARK
                    return
        except Exception:
            pass

        # KDE fallback: check kdeglobals by parsing colors
        try:
            home = self._get_real_user_home()
            kde_files = [home / '.config' / 'kdeglobals', Path('/etc/xdg/kdeglobals')]
            
            for kf in kde_files:
                if kf.exists():
                    try:
                        # Parse kdeglobals manually or via ConfigParser
                        # ConfigParser can be strict, so we handle it gracefully
                        kcfg = configparser.ConfigParser(strict=False, interpolation=None)
                        kcfg.read(str(kf))
                        
                        bg_color_str = None
                        if kcfg.has_section('Colors:Window') and kcfg.has_option('Colors:Window', 'BackgroundNormal'):
                             bg_color_str = kcfg.get('Colors:Window', 'BackgroundNormal')
                        elif kcfg.has_section('Colors:View') and kcfg.has_option('Colors:View', 'BackgroundNormal'):
                             bg_color_str = kcfg.get('Colors:View', 'BackgroundNormal')
                             
                        if bg_color_str:
                            # Format is r,g,b like 43,45,47
                            parts = [int(p.strip()) for p in bg_color_str.split(',')]
                            if len(parts) == 3:
                                r, g, b = parts
                                # Calculate luminance: standard formula
                                luminance = 0.299 * r + 0.587 * g + 0.114 * b
                                if luminance < 128:
                                    self._theme = ThemeType.DARK
                                    return
                                else:
                                    # Explicitly light background found
                                    self._theme = ThemeType.LIGHT
                                    return
                                    
                        # Fallback for older regex check if color parsing fails but "dark" is mentioned in General
                        if kcfg.has_section('General') and kcfg.has_option('General', 'ColorScheme'):
                             scheme = kcfg.get('General', 'ColorScheme').lower()
                             if 'dark' in scheme or 'black' in scheme:
                                 self._theme = ThemeType.DARK
                                 return
                    except Exception:
                        pass
        except Exception:
            pass

        self._theme = ThemeType.LIGHT

    # Compatibility helpers for other modules expecting these properties
    @property
    def desktop_environment(self) -> DesktopEnvironment:
        if self._desktop is None:
            self._detect_desktop()
        return self._desktop

    @property
    def display_protocol(self) -> DisplayProtocol:
        if self._display is None:
            self._detect_display()
        return self._display

    @property
    def gtk_theme_name(self) -> Optional[str]:
        if self._gtk_theme_name is None:
            self._detect_theme()
        return self._gtk_theme_name

    @property
    def is_wayland(self) -> bool:
        return self.display_protocol == DisplayProtocol.WAYLAND

    @property
    def is_dark_theme(self) -> bool:
        return self.theme_type == ThemeType.DARK

    def configure_environment_variables(self):
        """Set minimal environment variables useful for GTK behaviour.

        This is intentionally conservative: do not force `GTK_THEME` or other
        desktop-wide settings. Only set backend hints and accessibility toggles.
        """
        try:
            if self.is_wayland:
                os.environ['GTK_USE_PORTAL'] = '1'
                os.environ['GDK_BACKEND'] = 'wayland'
            # Reduce accessibility bus noise if not explicitly requested
            if not os.environ.get('ENABLE_ACCESSIBILITY'):
                os.environ['NO_AT_BRIDGE'] = '1'
                os.environ['AT_SPI_BUS'] = '0'
        except Exception:
            pass

    def load_parent_hints(self):
        """Load hints written by the unprivileged launcher via SOPLOS_ENV_FILE.

        This method is idempotent and safe to call multiple times. It only
        sets environment variables and attempts to remove the hint file.
        """
        env_file = os.environ.get('SOPLOS_ENV_FILE')
        if not env_file:
            return
        try:
            import json
            p = Path(env_file)
            if p.exists():
                data = json.loads(p.read_text(encoding='utf-8'))
                for k, v in data.items():
                    if v:
                        os.environ.setdefault(k, v)
                try:
                    p.unlink()
                except Exception:
                    pass
        except Exception:
            pass


# Global instance
_environment_detector = None


def get_environment_detector() -> EnvironmentDetector:
    global _environment_detector
    if _environment_detector is None:
        _environment_detector = EnvironmentDetector()
    return _environment_detector


def detect_environment() -> Dict[str, str]:
    return get_environment_detector().detect_all()
