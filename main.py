#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Soplos Grub Editor 2.0.0 - GRUB Configuration Editor
Main application entry point.
"""

import sys
import os
import warnings
from pathlib import Path

# Add the project root to PYTHONPATH
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Suppress accessibility warnings for a cleaner output
warnings.filterwarnings('ignore', '.*Couldn\'t connect to accessibility bus.*', Warning)
warnings.filterwarnings('ignore', '.*Failed to connect to socket.*', Warning)

# Disable accessibility bridge unless explicitly enabled
if not os.environ.get('ENABLE_ACCESSIBILITY'):
    os.environ['NO_AT_BRIDGE'] = '1'
    os.environ['AT_SPI_BUS'] = '0'

def cleanup_pycache():
    """Recursively remove __pycache__ directories."""
    import shutil
    try:
        # PROJECT_ROOT is defined globally
        for p in PROJECT_ROOT.rglob('__pycache__'):
            if p.is_dir():
                shutil.rmtree(p, ignore_errors=True)
    except Exception as e:
        print(f"Warning: Failed to cleanup pycache: {e}")

def main():
    """Main entry point for Soplos Grub Editor."""
    
    # Auto-elevate to root if not already root
    if os.geteuid() != 0:
        import subprocess
        
        # Preserve all important environment variables for desktop detection
        env_vars = []
        important_vars = [
            'DISPLAY', 'XAUTHORITY', 'XDG_RUNTIME_DIR', 'XDG_SESSION_TYPE',
            'XDG_CURRENT_DESKTOP', 'XDG_SESSION_DESKTOP', 'DESKTOP_SESSION',
            'WAYLAND_DISPLAY', 'DBUS_SESSION_BUS_ADDRESS', 'GTK_THEME',
            'HOME', 'LANG', 'LANGUAGE', 'LC_ALL'
        ]
        for var in important_vars:
            val = os.environ.get(var, '')
            if val:
                env_vars.append(f"{var}={val}")
        
        # Detect user's GTK theme and theme type (dark/light) before elevating
        # This is crucial because running as root loses access to user's settings
        theme = None
        theme_type = None  # 'dark' or 'light'
        
        # Detect XFCE theme
        try:
            result = subprocess.run(['xfconf-query', '-c', 'xsettings', '-p', '/Net/ThemeName'],
                                   capture_output=True, text=True)
            if result.returncode == 0:
                theme = result.stdout.strip()
                theme_type = 'dark' if 'dark' in theme.lower() else 'light'
        except Exception:
            pass
        
        # Detect GNOME theme
        if not theme:
            try:
                # First try color-scheme (GNOME 42+)
                result = subprocess.run(['gsettings', 'get', 'org.gnome.desktop.interface', 'color-scheme'],
                                       capture_output=True, text=True)
                if result.returncode == 0 and 'dark' in result.stdout.lower():
                    theme_type = 'dark'
                else:
                    theme_type = 'light'
                    
                # Get actual theme name
                result = subprocess.run(['gsettings', 'get', 'org.gnome.desktop.interface', 'gtk-theme'],
                                       capture_output=True, text=True)
                if result.returncode == 0:
                    theme = result.stdout.strip().strip("'")
                    if 'dark' in theme.lower():
                        theme_type = 'dark'
            except Exception:
                pass
        
        # Detect KDE theme
        if not theme:
            try:
                kdeglobals = os.path.expanduser('~/.config/kdeglobals')
                if os.path.exists(kdeglobals):
                    with open(kdeglobals, 'r') as f:
                        content = f.read()
                        for line in content.split('\n'):
                            if line.startswith('widgetStyle='):
                                theme = line.split('=', 1)[1].strip()
                            if 'ColorScheme=' in line:
                                scheme = line.split('=', 1)[1].strip().lower()
                                if 'dark' in scheme or 'black' in scheme:
                                    theme_type = 'dark'
                        if theme and not theme_type:
                            theme_type = 'dark' if 'dark' in theme.lower() else 'light'
            except Exception:
                pass
        
        if theme:
            env_vars.append(f"GTK_THEME={theme}")
        if theme_type:
            env_vars.append(f"SOPLOS_THEME_TYPE={theme_type}")
        
        script_path = str(Path(__file__).resolve())
        cmd = ['pkexec', 'env'] + env_vars + [sys.executable, script_path]
        
        try:
            result = subprocess.run(cmd)
            return result.returncode
        except Exception as e:
            print(f"Failed to elevate privileges: {e}")
            return 1
    
    exit_code = 0
    try:
        from core.application import run_application
        exit_code = run_application()
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Ensure all dependencies are installed:")
        print("  sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0")
        import traceback
        traceback.print_exc()
        exit_code = 1
        
    except Exception as e:
        print(f"Application error: {e}")
        import traceback
        traceback.print_exc()
        exit_code = 1
        
    finally:
        cleanup_pycache()
        return exit_code

if __name__ == '__main__':
    sys.exit(main())
