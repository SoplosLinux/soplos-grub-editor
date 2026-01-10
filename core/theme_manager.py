"""
Theme management system for Soplos Repo Selector.
Handles CSS theme loading, application, and dynamic theme switching.
"""

import os
from pathlib import Path
from typing import Dict, Optional, List
import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

from utils.logger import log_info, log_error, log_warning
from core.i18n_manager import _

from .environment import get_environment_detector, DesktopEnvironment, ThemeType


class ThemeManager:
    """
    Manages CSS themes for the application with automatic detection
    and desktop environment integration.
    """
    
    def __init__(self, assets_path: str):
        """
        Initialize the theme manager.
        
        Args:
            assets_path: Path to the assets directory containing themes
        """
        self.assets_path = Path(assets_path)
        self.themes_path = self.assets_path / 'themes'
        self.css_provider = None
        self.current_theme = None
        self.environment_detector = get_environment_detector()
        
        # Ensure themes directory exists
        self.themes_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize CSS provider
        self._init_css_provider()

    def get_available_themes(self) -> List[str]:
        """
        Get list of available theme names.

        Returns:
            List of theme names (without .css extension)
        """
        if not self.themes_path.exists():
            return []

        themes = []
        for theme_file in self.themes_path.glob('*.css'):
            themes.append(theme_file.stem)

        return sorted(themes)
    
    def _init_css_provider(self):
        """Initialize the GTK CSS provider."""
        self.css_provider = Gtk.CssProvider()
        
        # Add to default screen
        screen = Gdk.Screen.get_default()
        style_context = Gtk.StyleContext()
        style_context.add_provider_for_screen(
            screen, 
            self.css_provider, 
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
    
    def detect_optimal_theme(self) -> str:
        """
        Detects the optimal theme based on the current environment.
        
        Returns:
            Theme name that best matches the current environment
        """
        # Check if theme type was passed from parent process (before root elevation)
        theme_type_override = os.environ.get('SOPLOS_THEME_TYPE')
        
        if theme_type_override:
            # Use the theme type detected before root elevation
            theme_type = theme_type_override
            desktop_env = self.environment_detector.detect_all().get('desktop_environment', 'unknown')
        else:
            env_info = self.environment_detector.detect_all()
            desktop_env = env_info['desktop_environment']
            theme_type = env_info['theme_type']
        
        # Priority order for theme selection
        theme_candidates = []
        
        # 1. Desktop-specific theme with light/dark variant
        if desktop_env != 'unknown':
            theme_candidates.append(f"{desktop_env}-{theme_type}")
            theme_candidates.append(f"{desktop_env}")
        
        # 2. Generic light/dark theme
        theme_candidates.append(theme_type)
        
        # 3. Base theme
        theme_candidates.append('base')
        
        # Check availability
        for candidate in theme_candidates:
            if (self.themes_path / f"{candidate}.css").exists():
                return candidate
        
        return 'base'  # Will create if doesn't exist
    
    def load_theme(self, theme_name: str) -> bool:
        """
        Load and apply a specific theme.
        
        Args:
            theme_name: Name of the theme to load
            
        Returns:
            True if theme was loaded successfully, False otherwise
        """
        theme_path = self.themes_path / f"{theme_name}.css"
        
        if not theme_path.exists():
            # Try to create a basic theme if it doesn't exist
            if theme_name == 'base':
                self._create_base_theme()
            elif theme_name in ['dark', 'light']:
                if theme_name == 'dark':
                    self.create_dark_theme()
                else:
                    self.create_light_theme()
            else:
                log_warning(_("Theme '{name}' not found at {path}").format(name=theme_name, path=theme_path))
                return False
        
        try:
            self.css_provider.load_from_path(str(theme_path))
            self.current_theme = theme_name
            
            # Force GTK to use dark variant if we are loading a dark theme
            settings = Gtk.Settings.get_default()
            if settings:
                is_dark = 'dark' in theme_name or theme_name == 'base' # base is dark by default
                settings.set_property("gtk-application-prefer-dark-theme", is_dark)
            
            log_info(_("Successfully loaded theme: {name}").format(name=theme_name))
            return True
        except Exception as e:
            log_error(_("Error loading theme '{name}': {err}").format(name=theme_name, err=e))
            return False

    def reload_current_theme(self):
        """Reload the currently active theme."""
        if self.current_theme:
            self.load_theme(self.current_theme)

    def add_custom_css(self, css_content: str):
        """
        Add custom CSS content to the current theme.

        Args:
            css_content: CSS content to add
        """
        try:
            self.css_provider.load_from_data(css_content.encode('utf-8'))
        except Exception as e:
            log_error(_("Error adding custom CSS: {err}").format(err=e))
    
    def load_optimal_theme(self) -> str:
        """Automatically detects and loads the optimal theme."""
        optimal_theme = self.detect_optimal_theme()
        
        if self.load_theme(optimal_theme):
            return optimal_theme
        
        if self.load_theme('base'):
            return 'base'
        
        return 'none'
    
    def _create_base_theme(self):
        """Create a basic base theme if it doesn't exist."""
        base_theme_content = """
/* Base Theme for Soplos Repo Selector */

/* Application Window */
.soplos-window {
    background-color: @theme_bg_color;
    color: @theme_fg_color;
}

/* Main Content Area */
.soplos-content {
    padding: 20px;
    background-color: @theme_base_color;
    border-radius: 8px;
}

/* Buttons */
.soplos-button-primary {
    background-color: @theme_selected_bg_color;
    color: @theme_selected_fg_color;
    border-radius: 6px;
    padding: 10px 20px;
    border: 1px solid @borders;
    font-weight: bold;
}

/* Cards */
.soplos-card {
    background-color: @theme_base_color;
    border: 1px solid @borders;
    border-radius: 8px;
    padding: 16px;
    margin: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
"""
        try:
            with open(self.themes_path / 'base.css', 'w', encoding='utf-8') as f:
                f.write(base_theme_content)
        except Exception:
            pass
    
    def create_dark_theme(self):
        """Create a dark theme variant."""
        dark_theme_content = """
/* Dark Theme */
@import url('base.css');

@define-color theme_bg_color #2b2b2b;
@define-color theme_fg_color #ffffff;
@define-color theme_base_color #3c3c3c;
@define-color theme_selected_bg_color #4a90e2;
@define-color theme_selected_fg_color #ffffff;
@define-color borders #555555;
"""
        try:
            with open(self.themes_path / 'dark.css', 'w', encoding='utf-8') as f:
                f.write(dark_theme_content)
        except Exception:
            pass
            
    def create_light_theme(self):
        """Create a light theme variant."""
        light_theme_content = """
/* Light Theme */
@import url('base.css');

@define-color theme_bg_color #f5f5f5;
@define-color theme_fg_color #2c3e50;
@define-color theme_base_color #ffffff;
@define-color theme_selected_bg_color #3498db;
@define-color theme_selected_fg_color #ffffff;
@define-color borders #e0e0e0;
"""
        try:
            with open(self.themes_path / 'light.css', 'w', encoding='utf-8') as f:
                f.write(light_theme_content)
        except Exception:
            pass
            
    def initialize_default_themes(self):
        """Create default themes if they don't exist."""
        if not (self.themes_path / 'base.css').exists():
            self._create_base_theme()
        if not (self.themes_path / 'dark.css').exists():
            self.create_dark_theme()
        if not (self.themes_path / 'light.css').exists():
            self.create_light_theme()


# Global theme manager instance
_theme_manager = None

def get_theme_manager(assets_path: str = None) -> ThemeManager:
    """Returns the global theme manager instance."""
    global _theme_manager
    if _theme_manager is None:
        if assets_path is None:
            # Default path relative to this file
            current_dir = Path(__file__).parent.parent
            assets_path = current_dir / 'assets'
        _theme_manager = ThemeManager(str(assets_path))
    return _theme_manager

def initialize_theming(assets_path: str = None) -> str:
    """Initialize the theming system and load the optimal theme."""
    theme_manager = get_theme_manager(assets_path)
    theme_manager.initialize_default_themes()
    return theme_manager.load_optimal_theme()
