"""
GRUB Manager module for Soplos Grub Editor.
Handles reading and writing configurations to /etc/default/grub,
interacting with grub-mkconfig, and managing grub-btrfs integration.
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from utils.logger import log_info, log_error, log_warning
from core.i18n_manager import _


class GrubManager:
    """
    Manages GRUB configuration and system interactions.
    """
    
    GRUB_DEFAULT_PATH = "/etc/default/grub"
    
    def __init__(self):
        """Initialize the GRUB manager."""
        self.config_path = Path(self.GRUB_DEFAULT_PATH)
        self.config_data = {}
        
    def read_config(self) -> Dict[str, str]:
        """
        Read the current GRUB configuration.
        
        Returns:
            Dictionary with configuration keys and values
        """
        self.config_data = {}
        
        if not self.config_path.exists():
            log_error(f"GRUB config not found at {self.config_path}")
            return {}
            
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                        
                    if '=' in line:
                        key, value = line.split('=', 1)
                        # Remove quotes if present
                        value = value.strip('"').strip("'")
                        self.config_data[key.strip()] = value
                        
            return self.config_data
        except Exception as e:
            log_error(f"Error reading GRUB config: {e}")
            return {}
            
    def save_config(self, new_config: Dict[str, str]) -> bool:
        """
        Save configuration to /etc/default/grub.
        Modifies existing keys in place. Deletes keys with empty values.
        Only adds new keys if they don't exist.
        """
        import os
        
        try:
            # Read file
            lines = []
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
            
            # Build result while tracking what we've processed
            result_lines = []
            processed_keys = set()
            
            for line in lines:
                stripped = line.strip()
                
                # Skip lines that are our own "Modified by" comments
                if '# Modified by Soplos GRUB Editor' in stripped:
                    continue
                # Skip commented-out lines we previously created
                if '# Cleared by Soplos' in stripped or '# Removed by Soplos' in stripped:
                    continue
                
                # Check if this is a commented key=value that we want to uncomment
                if stripped.startswith('#') and '=' in stripped:
                    # Extract key from commented line (e.g., "#GRUB_TIMEOUT_STYLE=hidden")
                    uncommented = stripped.lstrip('#').strip()
                    key = uncommented.split('=')[0].strip()
                    
                    if key in new_config and key not in processed_keys:
                        value = new_config[key]
                        processed_keys.add(key)
                        
                        # Empty value = keep it commented (or delete)
                        if value == '':
                            result_lines.append(line)  # Keep commented
                        else:
                            # Uncomment and set new value
                            if ' ' in value:
                                value = f'"{value}"'
                            result_lines.append(f'{key}={value}\n')
                        continue
                    else:
                        # Not a key we're modifying, keep original commented line
                        result_lines.append(line)
                        continue
                
                # Keep other comments and empty lines
                if not stripped or stripped.startswith('#'):
                    result_lines.append(line)
                    continue
                
                # Parse uncommented key=value lines
                if '=' in stripped:
                    key = stripped.split('=')[0].strip()
                    
                    # Skip if we already processed this key (handle duplicates)
                    if key in processed_keys:
                        continue
                    
                    if key in new_config:
                        value = new_config[key]
                        processed_keys.add(key)
                        
                        # Empty value = delete the line (don't add it to result)
                        if value == '':
                            continue
                        
                        # Write the updated value
                        if ' ' in value:
                            value = f'"{value}"'
                        result_lines.append(f'{key}={value}\n')
                    else:
                        # Key not in our config, keep original line
                        result_lines.append(line)
                else:
                    result_lines.append(line)
            
            # Add only truly new keys (don't exist in file and have non-empty values)
            new_keys = []
            for key, value in new_config.items():
                if key not in processed_keys and value != '':
                    if ' ' in value:
                        value = f'"{value}"'
                    new_keys.append(f'{key}={value}\n')
            
            # Remove trailing empty lines
            while result_lines and result_lines[-1].strip() == '':
                result_lines.pop()
            
            if new_keys:
                # Add a single blank line before our section if file doesn't end with one
                if result_lines and result_lines[-1].strip() != '':
                    result_lines.append('\n')
                result_lines.append('# Modified by Soplos GRUB Editor\n')
                result_lines.extend(new_keys)
            
            # Write file
            is_root = os.geteuid() == 0
            if is_root:
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    f.writelines(result_lines)
                self.read_config()  # Reload to keep state in sync
                log_info(_("Successfully saved config to {path}").format(path=self.config_path))
                return True
            else:
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.grub') as tmp:
                    tmp.writelines(result_lines)
                    tmp_path = tmp.name
                
                result = subprocess.run(['pkexec', 'cp', tmp_path, str(self.config_path)], 
                                        capture_output=True, text=True)
                os.unlink(tmp_path)
                
                if result.returncode == 0:
                    self.read_config()  # Reload to keep state in sync
                    log_info(_("Successfully saved config using pkexec"))
                    return True
                else:
                    log_error(_("Failed to save config: {err}").format(err=result.stderr))
                    return False
                    
        except Exception as e:
            log_error(_("Error saving GRUB config: {err}").format(err=e))
            return False


    def remove_config_key(self, key: str) -> bool:
        """
        Remove a configuration key from /etc/default/grub.
        The line is commented out rather than deleted to preserve structure.
        """
        import os
        
        try:
            lines = []
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
            
            updated_lines = []
            found = False
            for line in lines:
                line_stripped = line.strip()
                if line_stripped and not line_stripped.startswith('#') and '=' in line_stripped:
                    line_key = line_stripped.split('=')[0].strip()
                    if line_key == key:
                        # Delete the line by not adding it to result
                        found = True
                        continue
                updated_lines.append(line)
            
            if not found:
                return True  # Key already doesn't exist
            
            is_root = os.geteuid() == 0
            if is_root:
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    f.writelines(updated_lines)
                log_info(_("Removed key {key} from config").format(key=key))
                return True
            else:
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.grub') as tmp:
                    tmp.writelines(updated_lines)
                    tmp_path = tmp.name
                cmd = ['pkexec', 'cp', tmp_path, str(self.config_path)]
                result = subprocess.run(cmd, capture_output=True, text=True)
                os.unlink(tmp_path)
                if result.returncode == 0:
                    log_info(_("Removed key {key} from config").format(key=key))
                    return True
                return False
                
        except Exception as e:
            log_error(_("Error removing config key: {err}").format(err=e))
            return False

    def update_grub(self) -> bool:
        """
        Run update-grub to apply changes.
        Uses full path and detects if running as root.
        """
        import os
        
        # Check if running as root
        is_root = os.geteuid() == 0
        
        # Find update-grub path
        update_grub_paths = ['/usr/sbin/update-grub', '/sbin/update-grub', 'update-grub']
        update_grub_cmd = None
        for path in update_grub_paths:
            if os.path.exists(path):
                update_grub_cmd = path
                break
        
        if not update_grub_cmd:
            log_error(_("update-grub not found"))
            return False
        
        try:
            if is_root:
                cmd = [update_grub_cmd]
            else:
                cmd = ['pkexec', update_grub_cmd]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                log_info(_("Successfully updated GRUB"))
                return True
            else:
                log_error(_("Failed to update GRUB: {err}").format(err=result.stderr))
                return False
        except Exception as e:
            log_error(_("Error running update-grub: {err}").format(err=e))
            return False        
    
    @property
    def config(self) -> Dict[str, str]:
        """Return current config, loading if needed."""
        if not self.config_data:
            self.read_config()
        return self.config_data
    
    def get_menu_entries(self) -> List[Dict]:
        """
        Parse grub.cfg to get menu entries.
        Uses cached result to avoid multiple pkexec prompts.
        
        Returns:
            List of dictionaries with entry information
        """
        # Return cached entries if available
        if hasattr(self, '_cached_entries') and self._cached_entries:
            return self._cached_entries
            
        entries = []
        grub_cfg = Path("/boot/grub/grub.cfg")
        
        content = ""
        # Try reading directly first
        try:
            with open(grub_cfg, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except PermissionError:
            # Use pkexec to read
            try:
                result = subprocess.run(['pkexec', 'cat', str(grub_cfg)], 
                                        capture_output=True, text=True)
                if result.returncode == 0:
                    content = result.stdout
            except Exception:
                pass
        except FileNotFoundError:
            return entries
            
        if not content:
            return entries
            
        try:
                
            # Parse menuentry lines
            import re
            pattern = r"menuentry\s+['\"]([^'\"]+)['\"]"
            matches = re.findall(pattern, content)
            
            for i, name in enumerate(matches):
                entry_type = 'system'
                path = ''
                
                if 'recovery' in name.lower():
                    entry_type = 'recovery'
                elif 'memtest' in name.lower():
                    entry_type = 'memtest'
                    path = '/boot/memtest86+x64.bin' if 'x64' in name.lower() else '/boot/memtest86+.bin'
                elif 'uefi' in name.lower() or 'firmware' in name.lower():
                    entry_type = 'firmware'
                    
                entries.append({
                    'name': name,
                    'type': entry_type,
                    'path': path,
                    'enabled': True
                })
                
        except Exception as e:
            log_error(f"Error parsing grub.cfg: {e}")
            
        # Cache the results
        self._cached_entries = entries
        return entries
    
    def get_available_themes(self) -> List[str]:
        """
        Get list of installed GRUB themes.
        
        Returns:
            List of theme names
        """
        themes = []
        themes_dir = Path("/boot/grub/themes")
        
        if themes_dir.exists():
            for item in themes_dir.iterdir():
                if item.is_dir():
                    theme_file = item / "theme.txt"
                    if theme_file.exists():
                        themes.append(item.name)
                        
        return sorted(themes)
    
    def is_btrfs_root(self) -> bool:
        """Check if root filesystem is BTRFS."""
        try:
            result = subprocess.run(['findmnt', '-n', '-o', 'FSTYPE', '/'], 
                                    capture_output=True, text=True)
            return result.stdout.strip().lower() == 'btrfs'
        except Exception:
            return False


# Global instance
_grub_manager = None

def get_grub_manager() -> GrubManager:
    """Returns the global GRUB manager instance."""
    global _grub_manager
    if _grub_manager is None:
        _grub_manager = GrubManager()
    return _grub_manager
