"""
General Configuration View for Soplos Grub Editor.
Replicates legacy v1.x functionality with modern Soplos styling.
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib

from core.i18n_manager import _


class GeneralView(Gtk.Box):
    """General configuration tab - matches legacy GRUB Editor functionality."""
    
    def __init__(self, parent_window):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        self.parent_window = parent_window
        self.grub_manager = parent_window.grub_manager
        
        # Margins
        self.set_margin_start(20)
        self.set_margin_end(20)
        self.set_margin_top(20)
        self.set_margin_bottom(20)
        
        self._create_ui()
        self._load_data()
        
    def _create_ui(self):
        """Create the UI matching legacy layout."""
        # Section 1: Boot Configuration (Full Width)
        config_frame = Gtk.Frame(label=_("Boot Configuration"))
        config_frame.get_style_context().add_class('soplos-card')
        config_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        config_box.set_margin_start(15)
        config_box.set_margin_end(15)
        config_box.set_margin_top(10)
        config_box.set_margin_bottom(15)
        
        # Row 1: Default Boot Entry
        row1 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        label1 = Gtk.Label(label=_("Default Boot Entry:"))
        label1.set_halign(Gtk.Align.START)
        label1.set_width_chars(25)
        self.default_entry_combo = Gtk.ComboBoxText()
        self.default_entry_combo.set_hexpand(True)
        # Entries loaded dynamically in _load_data()
        row1.pack_start(label1, False, False, 0)
        row1.pack_start(self.default_entry_combo, True, True, 0)
        config_box.pack_start(row1, False, False, 0)
        
        # Row 2: Timeout (seconds)
        row2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        label2 = Gtk.Label(label=_("Timeout (seconds):"))
        label2.set_halign(Gtk.Align.START)
        label2.set_width_chars(25)
        self.timeout_spin = Gtk.SpinButton()
        self.timeout_spin.set_range(0, 60)
        self.timeout_spin.set_increments(1, 5)
        self.timeout_spin.set_value(5)
        self.timeout_spin.set_hexpand(True)
        row2.pack_start(label2, False, False, 0)
        row2.pack_start(self.timeout_spin, True, True, 0)
        config_box.pack_start(row2, False, False, 0)
        
        # Row 3: Screen Resolution
        row3 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        label3 = Gtk.Label(label=_("Screen Resolution:"))
        label3.set_halign(Gtk.Align.START)
        label3.set_width_chars(25)
        self.resolution_combo = Gtk.ComboBoxText()
        self.resolution_combo.set_hexpand(True)
        # 16:9, 16:10, 4:3, and legacy resolutions
        resolutions = [
            _("auto"),
            # 16:9 (widescreen)
            "3840x2160", "2560x1440", "1920x1080", "1600x900", "1366x768", "1280x720",
            # 16:10 (widescreen)
            "2560x1600", "1920x1200", "1680x1050", "1440x900", "1280x800",
            # 4:3 (standard/legacy)
            "1600x1200", "1280x1024", "1024x768", "800x600", "640x480",
        ]
        for res in resolutions:
            self.resolution_combo.append_text(res)
        self.resolution_combo.set_active(0)
        row3.pack_start(label3, False, False, 0)
        row3.pack_start(self.resolution_combo, True, True, 0)
        config_box.pack_start(row3, False, False, 0)
        
        config_frame.add(config_box)
        self.pack_start(config_frame, False, False, 0)
        
        # Section 2: Two Columns (Advanced Options | Kernel Parameters)
        middle_columns_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        # Force equal width for split columns
        middle_columns_box.set_homogeneous(True)
        self.pack_start(middle_columns_box, True, True, 0)
        
        # -- Column 1: Advanced Options --
        advanced_frame = Gtk.Frame(label=_("Advanced Options"))
        advanced_frame.get_style_context().add_class('soplos-card')
        advanced_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        advanced_box.set_margin_start(15)
        advanced_box.set_margin_end(15)
        advanced_box.set_margin_top(10)
        advanced_box.set_margin_bottom(15)
        
        # Checkbox: Detect other operating systems
        self.detect_os_check = Gtk.CheckButton(label=_("Detect other operating systems"))
        advanced_box.pack_start(self.detect_os_check, False, False, 0)
        
        # Checkbox: Show boot menu
        self.show_menu_check = Gtk.CheckButton(label=_("Show boot menu"))
        self.show_menu_check.set_active(True)
        advanced_box.pack_start(self.show_menu_check, False, False, 0)
        
        # Checkbox: Include recovery options
        self.recovery_check = Gtk.CheckButton(label=_("Include recovery options"))
        self.recovery_check.set_active(True)
        advanced_box.pack_start(self.recovery_check, False, False, 0)
        
        # Checkbox: Use UUID for root
        self.uuid_check = Gtk.CheckButton(label=_("Use UUID for root partition"))
        self.uuid_check.set_active(True)
        advanced_box.pack_start(self.uuid_check, False, False, 0)
        
        advanced_frame.add(advanced_box)
        middle_columns_box.pack_start(advanced_frame, True, True, 0)
        
        # -- Column 2: Kernel Parameters --
        kernel_frame = Gtk.Frame(label=_("Kernel Parameters"))
        kernel_frame.get_style_context().add_class('soplos-card')
        kernel_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        kernel_box.set_margin_start(15)
        kernel_box.set_margin_end(15)
        kernel_box.set_margin_top(10)
        kernel_box.set_margin_bottom(15)
        
        kernel_label = Gtk.Label(label=_("Kernel Parameters:"))
        kernel_label.set_halign(Gtk.Align.START)
        kernel_box.pack_start(kernel_label, False, False, 0)
        
        self.kernel_entry = Gtk.Entry()
        self.kernel_entry.set_placeholder_text(_("quiet splash resume=UUID=..."))
        kernel_box.pack_start(self.kernel_entry, False, False, 0)
        
        kernel_frame.add(kernel_box)
        middle_columns_box.pack_start(kernel_frame, True, True, 0)
        
        # Apply button (right-aligned, normal size)
        apply_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        apply_box.set_halign(Gtk.Align.END)
        apply_btn = Gtk.Button(label=_("Apply Changes"))
        apply_btn.get_style_context().add_class('suggested-action')
        apply_btn.connect('clicked', self._on_apply)
        apply_box.pack_start(apply_btn, False, False, 0)
        self.pack_start(apply_box, False, False, 10)
        
        # Spacer
        self.pack_start(Gtk.Box(), True, True, 0)
        
        self.show_all()
    
    def _load_data(self):
        """Load current GRUB configuration."""
        try:
            config = self.grub_manager.config
            
            # Load boot entries for Default Boot Entry dropdown
            entries = self.grub_manager.get_menu_entries()
            self.default_entry_combo.remove_all()
            for i, entry in enumerate(entries):
                # Format: "0: Entry Name"
                name = entry.get('name', _('Unknown'))
                display_text = f"{i}: {name}"
                self.default_entry_combo.append_text(display_text)
            
            # Select current default
            default = config.get('GRUB_DEFAULT', '0')
            try:
                default_idx = int(default)
                if default_idx < len(entries):
                    self.default_entry_combo.set_active(default_idx)
                else:
                    self.default_entry_combo.set_active(0)
            except ValueError:
                # GRUB_DEFAULT might be a string like "saved"
                self.default_entry_combo.prepend_text(f"[{default}]")
                self.default_entry_combo.set_active(0)
            
            # Timeout
            timeout = config.get('GRUB_TIMEOUT', '5')
            try:
                self.timeout_spin.set_value(int(timeout))
            except ValueError:
                self.timeout_spin.set_value(5)
            
            # Resolution
            gfxmode = config.get('GRUB_GFXMODE', 'auto')
            model = self.resolution_combo.get_model()
            for i, row in enumerate(model):
                if row[0] == gfxmode:
                    self.resolution_combo.set_active(i)
                    break
            
            # Kernel params
            cmdline = config.get('GRUB_CMDLINE_LINUX_DEFAULT', '')
            self.kernel_entry.set_text(cmdline)
            
            # Booleans
            timeout_style = config.get('GRUB_TIMEOUT_STYLE', 'menu')
            self.show_menu_check.set_active(timeout_style != 'hidden')
            
            disable_recovery = config.get('GRUB_DISABLE_RECOVERY', 'false')
            self.recovery_check.set_active(disable_recovery.lower() != 'true')
            
            disable_os_prober = config.get('GRUB_DISABLE_OS_PROBER', 'false')
            self.detect_os_check.set_active(disable_os_prober.lower() != 'true')
            
            # UUID - GRUB_DISABLE_LINUX_UUID=true means UUID is DISABLED
            disable_uuid = config.get('GRUB_DISABLE_LINUX_UUID', 'false')
            self.uuid_check.set_active(disable_uuid.lower() != 'true')
            
        except Exception as e:
            print(_("Error loading GRUB config: {}").format(e))
    
    def get_config(self):
        """Return current configuration from UI - only changed/existing keys."""
        original = self.grub_manager.config
        
        config = {}
        
        # Always include these core keys
        config['GRUB_DEFAULT'] = str(self.default_entry_combo.get_active())
        config['GRUB_TIMEOUT'] = str(int(self.timeout_spin.get_value()))
        config['GRUB_GFXMODE'] = self.resolution_combo.get_active_text() or 'auto'
        config['GRUB_CMDLINE_LINUX_DEFAULT'] = self.kernel_entry.get_text()
        
        # Only include these if they differ from default OR already exist in config
        timeout_style = 'menu' if self.show_menu_check.get_active() else 'hidden'
        if 'GRUB_TIMEOUT_STYLE' in original or timeout_style != 'menu':
            config['GRUB_TIMEOUT_STYLE'] = timeout_style
        
        disable_recovery = 'false' if self.recovery_check.get_active() else 'true'
        if 'GRUB_DISABLE_RECOVERY' in original or disable_recovery != 'false':
            config['GRUB_DISABLE_RECOVERY'] = disable_recovery
        
        disable_os_prober = 'false' if self.detect_os_check.get_active() else 'true'
        if 'GRUB_DISABLE_OS_PROBER' in original or disable_os_prober != 'false':
            config['GRUB_DISABLE_OS_PROBER'] = disable_os_prober
        
        # UUID - checked means use UUID (GRUB_DISABLE_LINUX_UUID=false or not set)
        disable_uuid = 'false' if self.uuid_check.get_active() else 'true'
        if 'GRUB_DISABLE_LINUX_UUID' in original or disable_uuid != 'false':
            config['GRUB_DISABLE_LINUX_UUID'] = disable_uuid
        
        return config
    
    def _on_apply(self, button):
        """Apply changes to GRUB configuration."""
        config = self.get_config()
        
        if self.grub_manager.save_config(config):
            # Ask to run update-grub
            dialog = Gtk.MessageDialog(
                transient_for=self.parent_window,
                flags=0,
                message_type=Gtk.MessageType.QUESTION,
                buttons=Gtk.ButtonsType.YES_NO,
                text=_("Changes Saved")
            )
            dialog.format_secondary_text(_("Run update-grub now to apply changes?"))
            response = dialog.run()
            dialog.destroy()
            
            if response == Gtk.ResponseType.YES:
                if self.grub_manager.update_grub():
                    info = Gtk.MessageDialog(
                        transient_for=self.parent_window,
                        flags=0,
                        message_type=Gtk.MessageType.INFO,
                        buttons=Gtk.ButtonsType.OK,
                        text=_("Success")
                    )
                    info.format_secondary_text(_("GRUB updated successfully!"))
                    info.run()
                    info.destroy()
                else:
                    err = Gtk.MessageDialog(
                        transient_for=self.parent_window,
                        flags=0,
                        message_type=Gtk.MessageType.ERROR,
                        buttons=Gtk.ButtonsType.OK,
                        text=_("Error")
                    )
                    err.format_secondary_text(_("Failed to update GRUB"))
                    err.run()
                    err.destroy()
        else:
            err = Gtk.MessageDialog(
                transient_for=self.parent_window,
                flags=0,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text=_("Error")
            )
            err.format_secondary_text(_("Failed to save configuration"))
            err.run()
            err.destroy()