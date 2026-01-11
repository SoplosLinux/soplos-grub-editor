#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Soplos Grub Editor 2.0.0 - GRUB Configuration Editor
Main application entry point.
"""

import sys
import os
from pathlib import Path

# Add the project root to PYTHONPATH
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Minimal main: elevate if needed, seed session info, then run application
def main():
    if os.geteuid() != 0:
        import subprocess
        import pwd
        import json
        import tempfile
        import shutil

        # Tyson-like comprehensive env propagation
        important_vars = [
            'DISPLAY', 'XAUTHORITY', 'XDG_RUNTIME_DIR', 'DBUS_SESSION_BUS_ADDRESS',
            'WAYLAND_DISPLAY', 'XDG_CURRENT_DESKTOP', 'XDG_SESSION_TYPE',
            'HOME', 'LANG', 'GDK_BACKEND', 'QT_QPA_PLATFORM', 'GTK_THEME'
        ]

        env_vars = []
        for v in important_vars:
            val = os.environ.get(v)
            if val:
                env_vars.append(f"{v}={val}")

        real_user = pwd.getpwuid(os.getuid()).pw_name
        env_vars.append(f"SUDO_USER={real_user}")   

        # Initialize variables to avoid UnboundLocalError
        user_desktop = ''
        session_type = ''
        theme_type = ''

        # Pre-elevation detection: Determine environment to pass to root
        try:
            # Add current directory to path to allow imports
            sys.path.insert(0, str(Path(__file__).parent))
            from core.environment import EnvironmentDetector
            
            detector = EnvironmentDetector()
            detector.detect_all()
            
            if detector.desktop_environment:
                user_desktop = detector.desktop_environment.value
                env_vars.append(f"SOPLOS_DESKTOP={user_desktop}")
            if detector.display_protocol:
                session_type = detector.display_protocol.value
                env_vars.append(f"SOPLOS_SESSION_TYPE={session_type}")
            if detector.theme_type:
                theme_type = detector.theme_type.value
                env_vars.append(f"SOPLOS_THEME_TYPE={theme_type}")
                
        except Exception as e:
            print(f"Warning: Pre-elevation detection failed: {e}")
            # Fallback to existing env vars if detection fails
            user_desktop = os.environ.get('XDG_CURRENT_DESKTOP', '')
            session_type = os.environ.get('XDG_SESSION_TYPE', '')
            theme_type = os.environ.get('SOPLOS_THEME_TYPE', '')
            
            if user_desktop:
                env_vars.append(f"SOPLOS_DESKTOP={user_desktop}")
            if session_type:
                env_vars.append(f"SOPLOS_SESSION_TYPE={session_type}")
            if theme_type:
                env_vars.append(f"SOPLOS_THEME_TYPE={theme_type}")

        # Write session JSON for elevated process to consume (secondary mechanism)
        env_file_path = None
        run_user_dir = f"/run/user/{os.getuid()}"
        data = {
            'SOPLOS_DESKTOP': user_desktop,
            'SOPLOS_SESSION_TYPE': session_type,
            'SOPLOS_THEME_TYPE': theme_type or ''
        }
        try:
            if os.path.isdir(run_user_dir):
                env_file_path = os.path.join(run_user_dir, f'soplos_env_{real_user}.json')
                with open(env_file_path, 'w', encoding='utf-8') as ef:
                    json.dump(data, ef)
            else:
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as ef:
                    env_file_path = ef.name
                    json.dump(data, ef)
        except Exception:
            env_file_path = None

        if env_file_path:
            env_vars.append(f"SOPLOS_ENV_FILE={env_file_path}")

        # Accessibility env often set in wrappers
        env_vars.append('NO_AT_BRIDGE=1')

        script_path = str(Path(__file__).resolve())
        pkexec_path = shutil.which('pkexec') or 'pkexec'
        cmd = [pkexec_path, 'env'] + env_vars + [sys.executable, script_path]
        try:
            return subprocess.run(cmd).returncode
        except Exception as e:
            print(f"Failed to elevate privileges: {e}")
            return 1

    # Run application as normal user/root
    try:
        from core.application import run_application
        return run_application()
    except ImportError as e:
        print(f"Import error: {e}")
        print("Ensure dependencies are installed: sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0")
        return 1
    except Exception as e:
        print(f"Application error: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
