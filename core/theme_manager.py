"""Theme management for Soplos GRUB Editor.

SIMPLIFIED APPROACH (like Repo Selector):
- Each theme file (dark.css, light.css) is SELF-CONTAINED
- NO concatenation, NO separate base.css
- Single CSS provider loads ONE file directly
- Respects SOPLOS_THEME_TYPE when running as root via pkexec
"""

import os
from pathlib import Path
import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

from typing import Optional
from .environment import get_environment_detector


class ThemeManager:
    def __init__(self, assets_path: str):
        self.assets_path = Path(assets_path)
        self.themes_path = self.assets_path / 'themes'
        self.css_provider: Optional[Gtk.CssProvider] = None
        self.current_theme: Optional[str] = None
        self.env = get_environment_detector()
        self._init_css_provider()

    def _init_css_provider(self):
        """Initialize single CSS provider (like Repo Selector)."""
        self.css_provider = Gtk.CssProvider()
        screen = Gdk.Screen.get_default()
        
        # Single provider at APPLICATION priority
        Gtk.StyleContext.add_provider_for_screen(
            screen,
            self.css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        
        print("[ThemeManager] CSS provider initialized")

    def detect_optimal_theme(self) -> str:
        """Detect best theme based on environment.
        
        Respects SOPLOS_THEME_TYPE override (set by unprivileged launcher
        when running as root via pkexec).
        """
        info = self.env.detect_all()
        desktop = info.get('desktop_environment', 'unknown')
        theme_type = info.get('theme_type', 'light')

        # CRITICAL: Check SOPLOS_THEME_TYPE override
        override = os.environ.get('SOPLOS_THEME_TYPE')
        if override:
            theme_type = override
            print(f"[ThemeManager] Using SOPLOS_THEME_TYPE override: {theme_type}")

        # Build candidate list
        candidates = []
        if desktop and desktop != 'unknown':
            candidates.append(f"{desktop}-{theme_type}")
            candidates.append(desktop)
        candidates.append(theme_type)
        candidates.append('dark')  # Safe fallback
        
        print(f"[ThemeManager] Theme candidates: {candidates}")

        # Return first existing candidate
        for c in candidates:
            theme_file = self.themes_path / f"{c}.css"
            if theme_file.exists():
                print(f"[ThemeManager] Selected theme: {c}")
                return c
        
        print("[ThemeManager] WARNING: No theme found, using 'dark'")
        return 'dark'

    def load_theme(self, theme_name: str) -> bool:
        """Load theme from a SINGLE self-contained CSS file.
        
        CRITICAL: Unlike the old approach, this does NOT concatenate files.
        Each theme file must contain BOTH variables AND styles.
        
        Args:
            theme_name: Name of theme file (without .css)
            
        Returns:
            True if theme loaded successfully
        """
        theme_path = self.themes_path / f"{theme_name}.css"

        print(f"\n[ThemeManager] ========================================")
        print(f"[ThemeManager] Loading theme: {theme_name}")
        print(f"[ThemeManager] Theme file: {theme_path}")
        print(f"[ThemeManager] ========================================")

        if not theme_path.exists():
            print(f"[ThemeManager] ✗ ERROR: Theme file not found: {theme_path}")
            return False
        
        try:
            # SIMPLE: Load directly from file (like Repo Selector)
            self.css_provider.load_from_path(str(theme_path))
            print(f"[ThemeManager] ✓ Theme loaded from file")
        except Exception as e:
            print(f"[ThemeManager] ✗ ERROR loading theme: {e}")
            return False

        # Set GTK dark theme preference if needed
        try:
            settings = Gtk.Settings.get_default()
            if settings is not None:
                # Check if this is a dark theme
                is_dark = (
                    os.environ.get('SOPLOS_THEME_TYPE') == 'dark' or
                    'dark' in theme_name.lower()
                )
                settings.set_property('gtk-application-prefer-dark-theme', is_dark)
                print(f"[ThemeManager] ✓ GTK dark theme preference: {is_dark}")
        except Exception as e:
            print(f"[ThemeManager] ⚠ Could not set GTK theme preference: {e}")

        self.current_theme = theme_name
        print(f"[ThemeManager] ✓✓✓ Theme '{theme_name}' loaded successfully ✓✓✓\n")
        return True

    def switch_theme(self, theme_name: str) -> bool:
        """Switch to a different theme at runtime."""
        if theme_name == self.current_theme:
            print(f"[ThemeManager] Already using theme '{theme_name}'")
            return True
        
        print(f"[ThemeManager] Switching from '{self.current_theme}' to '{theme_name}'")
        return self.load_theme(theme_name)


# Singleton instance
_theme_manager: Optional[ThemeManager] = None


def get_theme_manager(assets_path: str = None) -> ThemeManager:
    """Get or create the global ThemeManager instance."""
    global _theme_manager
    if _theme_manager is None:
        if assets_path is None:
            current_dir = Path(__file__).parent.parent
            assets_path = current_dir / 'assets'
        _theme_manager = ThemeManager(str(assets_path))
    return _theme_manager


def initialize_theming(assets_path: str = None) -> str:
    """Initialize theming system and load optimal theme.
    
    Returns:
        Name of loaded theme, or 'none' if failed
    """
    print("\n" + "="*60)
    print("[ThemeManager] Initializing theming system...")
    print("="*60)
    
    # Debug: Show relevant environment when running as root
    if os.geteuid() == 0:
        print("[ThemeManager] Running as ROOT - checking for user theme hints:")
        for var in ['SOPLOS_THEME_TYPE', 'SOPLOS_DESKTOP', 'SOPLOS_SESSION_TYPE']:
            val = os.environ.get(var, '(not set)')
            print(f"[ThemeManager]   {var} = {val}")
    
    tm = get_theme_manager(assets_path)
    theme_name = tm.detect_optimal_theme()
    
    if tm.load_theme(theme_name):
        print(f"[ThemeManager] ✓✓✓ Theming initialized with '{theme_name}' ✓✓✓")
        print("="*60 + "\n")
        return theme_name
    
    print("[ThemeManager] ✗✗✗ Failed to initialize theming ✗✗✗")
    print("="*60 + "\n")
    return 'none'