"""
Appearance View for Soplos Grub Editor.
Replicates legacy v1.x functionality with modern Soplos styling.
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib

from core.i18n_manager import _


class AppearanceView(Gtk.ScrolledWindow):
    """Appearance configuration tab - matches legacy GRUB Editor functionality."""
    
    def __init__(self, parent_window):
        super().__init__()
        self.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        
        self.parent_window = parent_window
        self.grub_manager = parent_window.grub_manager
        
        # Main content box
        self.content_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=15)
        self.content_box.set_margin_start(15)
        self.content_box.set_margin_end(15)
        self.content_box.set_margin_top(15)
        self.content_box.set_margin_bottom(15)
        
        self.add(self.content_box)
        
        self._create_ui()
        self._load_data()
        
    def _create_ui(self):
        """Create the UI matching legacy layout."""
        # Left side: Theme Preview
        preview_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        
        preview_label = Gtk.Label(label=_("Theme"))
        preview_label.set_halign(Gtk.Align.START)
        preview_label.get_style_context().add_class('dim-label')
        preview_box.pack_start(preview_label, False, False, 0)
        
        preview_label2 = Gtk.Label(label=_("Preview"))
        preview_label2.set_halign(Gtk.Align.START)
        preview_box.pack_start(preview_label2, False, False, 0)
        
        # Preview image frame
        preview_frame = Gtk.Frame()
        preview_frame.get_style_context().add_class('soplos-card')
        self.preview_image = Gtk.Image()
        self.preview_image.set_size_request(280, 180)
        # Set a placeholder or load current theme preview
        self.preview_image.set_from_icon_name('image-missing', Gtk.IconSize.DIALOG)
        preview_frame.add(self.preview_image)
        preview_box.pack_start(preview_frame, False, False, 0)
        
        self.content_box.pack_start(preview_box, False, False, 0)
        
        # Right side: Controls
        controls_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        controls_box.set_hexpand(True)
        
        # Sub-notebook for Theme/Background
        sub_notebook = Gtk.Notebook()
        sub_notebook.set_tab_pos(Gtk.PositionType.TOP)
        
        # Tab 1: Theme (includes colors and fonts)
        theme_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        theme_box.set_margin_start(10)
        theme_box.set_margin_end(10)
        theme_box.set_margin_top(10)
        theme_box.set_margin_bottom(10)
        
        # Info label
        info_label = Gtk.Label(label=_("Themes include colors and fonts. Use 'Background' tab for custom setup."))
        info_label.set_line_wrap(True)
        info_label.get_style_context().add_class('dim-label')
        info_label.set_halign(Gtk.Align.START)
        theme_box.pack_start(info_label, False, False, 0)
        
        # Theme selector
        theme_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        theme_label = Gtk.Label(label=_("Theme:"))
        theme_label.set_halign(Gtk.Align.START)
        theme_row.pack_start(theme_label, False, False, 0)
        
        self.theme_combo = Gtk.ComboBoxText()
        self.theme_combo.set_hexpand(True)
        self.theme_combo.connect('changed', self._on_theme_changed)
        theme_row.pack_start(self.theme_combo, True, True, 0)
        theme_box.pack_start(theme_row, False, False, 0)
        
        # Theme buttons in a more compact layout
        theme_buttons = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        
        install_btn = Gtk.Button(label=_("Install..."))
        install_btn.connect('clicked', self._on_install_theme)
        theme_buttons.pack_start(install_btn, True, True, 0)
        
        apply_btn = Gtk.Button(label=_("Apply"))
        apply_btn.get_style_context().add_class('suggested-action')
        apply_btn.connect('clicked', self._on_apply_theme)
        theme_buttons.pack_start(apply_btn, True, True, 0)
        
        disable_btn = Gtk.Button(label=_("Disable"))
        disable_btn.connect('clicked', self._on_disable_theme)
        theme_buttons.pack_start(disable_btn, True, True, 0)
        
        remove_btn = Gtk.Button(label=_("Remove"))
        remove_btn.get_style_context().add_class('destructive-action')
        remove_btn.connect('clicked', self._on_remove_theme)
        theme_buttons.pack_start(remove_btn, True, True, 0)
        
        theme_box.pack_start(theme_buttons, False, False, 0)
        
        sub_notebook.append_page(theme_box, Gtk.Label(label=_("Theme")))
        
        # Tab 2: Background (with Colors and info about custom setup)
        bg_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        bg_box.set_margin_start(10)
        bg_box.set_margin_end(10)
        bg_box.set_margin_top(10)
        bg_box.set_margin_bottom(10)
        
        bg_label = Gtk.Label(label=_("Background image:"))
        bg_label.set_halign(Gtk.Align.START)
        bg_box.pack_start(bg_label, False, False, 0)
        
        bg_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.bg_entry = Gtk.Entry()
        self.bg_entry.set_placeholder_text(_("/boot/grub/background.png"))
        self.bg_entry.set_hexpand(True)
        self.bg_entry.connect('changed', self._on_bg_entry_changed)
        bg_row.pack_start(self.bg_entry, True, True, 0)
        
        browse_btn = Gtk.Button(label=_("Browse..."))
        browse_btn.connect('clicked', self._on_browse_background)
        bg_row.pack_start(browse_btn, False, False, 0)
        
        remove_bg_btn = Gtk.Button(label=_("Remove"))
        remove_bg_btn.get_style_context().add_class('destructive-action')
        remove_bg_btn.connect('clicked', self._on_remove_background)
        bg_row.pack_start(remove_bg_btn, False, False, 0)
        
        bg_box.pack_start(bg_row, False, False, 0)
        
        # Separator
        sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        bg_box.pack_start(sep, False, False, 5)
        
        # Colors section (inside Background tab)
        colors_label = Gtk.Label(label=_("Colors (when not using theme):"))
        colors_label.set_halign(Gtk.Align.START)
        colors_label.get_style_context().add_class('dim-label')
        bg_box.pack_start(colors_label, False, False, 0)
        
        # Text color
        text_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        text_label = Gtk.Label(label=_("Text color:"))
        text_label.set_width_chars(18)
        text_label.set_halign(Gtk.Align.START)
        text_row.pack_start(text_label, False, False, 0)
        self.text_color_btn = Gtk.ColorButton()
        self.text_color_btn.set_rgba(Gdk.RGBA(1, 1, 1, 1))
        text_row.pack_start(self.text_color_btn, False, False, 0)
        bg_box.pack_start(text_row, False, False, 0)
        
        # Background color
        bg_color_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        bg_color_label = Gtk.Label(label=_("Background color:"))
        bg_color_label.set_width_chars(18)
        bg_color_label.set_halign(Gtk.Align.START)
        bg_color_row.pack_start(bg_color_label, False, False, 0)
        self.bg_color_btn = Gtk.ColorButton()
        self.bg_color_btn.set_rgba(Gdk.RGBA(0, 0, 0, 1))
        bg_color_row.pack_start(self.bg_color_btn, False, False, 0)
        bg_box.pack_start(bg_color_row, False, False, 0)
        
        # Highlight text color
        hl_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        hl_label = Gtk.Label(label=_("Highlight text:"))
        hl_label.set_width_chars(18)
        hl_label.set_halign(Gtk.Align.START)
        hl_row.pack_start(hl_label, False, False, 0)
        self.hl_color_btn = Gtk.ColorButton()
        self.hl_color_btn.set_rgba(Gdk.RGBA(1, 0.5, 0, 1))
        hl_row.pack_start(self.hl_color_btn, False, False, 0)
        bg_box.pack_start(hl_row, False, False, 0)
        
        # Highlight background color
        hl_bg_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        hl_bg_label = Gtk.Label(label=_("Highlight background:"))
        hl_bg_label.set_width_chars(18)
        hl_bg_label.set_halign(Gtk.Align.START)
        hl_bg_row.pack_start(hl_bg_label, False, False, 0)
        self.hl_bg_color_btn = Gtk.ColorButton()
        self.hl_bg_color_btn.set_rgba(Gdk.RGBA(0.2, 0.2, 0.2, 1))
        hl_bg_row.pack_start(self.hl_bg_color_btn, False, False, 0)
        bg_box.pack_start(hl_bg_row, False, False, 0)
        
        # Apply background button
        apply_bg_btn = Gtk.Button(label=_("Apply Background Settings"))
        apply_bg_btn.get_style_context().add_class('suggested-action')
        apply_bg_btn.connect('clicked', self._on_apply_background)
        bg_box.pack_start(apply_bg_btn, False, False, 10)
        
        sub_notebook.append_page(bg_box, Gtk.Label(label=_("Background")))
        
        # Tab 3: Fonts
        fonts_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        fonts_box.set_margin_start(10)
        fonts_box.set_margin_end(10)
        fonts_box.set_margin_top(10)
        fonts_box.set_margin_bottom(10)
        
        fonts_label = Gtk.Label(label=_("Convert TrueType fonts to GRUB format (PF2):"))
        fonts_label.set_halign(Gtk.Align.START)
        fonts_label.set_line_wrap(True)
        fonts_box.pack_start(fonts_label, False, False, 0)
        
        # Font file selector
        font_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.font_entry = Gtk.Entry()
        self.font_entry.set_placeholder_text(_("Select TTF/OTF font file..."))
        self.font_entry.set_hexpand(True)
        font_row.pack_start(self.font_entry, True, True, 0)
        
        font_browse_btn = Gtk.Button(label=_("Browse..."))
        font_browse_btn.connect('clicked', self._on_browse_font)
        font_row.pack_start(font_browse_btn, False, False, 0)
        fonts_box.pack_start(font_row, False, False, 0)
        
        # Font size
        size_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        size_label = Gtk.Label(label=_("Font size:"))
        size_row.pack_start(size_label, False, False, 0)
        self.font_size_spin = Gtk.SpinButton()
        self.font_size_spin.set_range(8, 72)
        self.font_size_spin.set_increments(1, 4)
        self.font_size_spin.set_value(16)
        size_row.pack_start(self.font_size_spin, False, False, 0)
        fonts_box.pack_start(size_row, False, False, 0)
        
        # Convert button
        convert_btn = Gtk.Button(label=_("Convert and Install Font"))
        convert_btn.get_style_context().add_class('suggested-action')
        convert_btn.connect('clicked', self._on_convert_font)
        fonts_box.pack_start(convert_btn, False, False, 10)
        
        # Installed fonts list
        installed_label = Gtk.Label(label=_("Installed GRUB fonts:"))
        installed_label.set_halign(Gtk.Align.START)
        fonts_box.pack_start(installed_label, False, False, 0)
        
        self.fonts_combo = Gtk.ComboBoxText()
        self._load_installed_fonts()
        fonts_box.pack_start(self.fonts_combo, False, False, 0)
        
        # Apply font button
        apply_font_btn = Gtk.Button(label=_("Apply selected font"))
        apply_font_btn.connect('clicked', self._on_apply_font)
        fonts_box.pack_start(apply_font_btn, False, False, 0)
        
        sub_notebook.append_page(fonts_box, Gtk.Label(label=_("Fonts")))
        
        controls_box.pack_start(sub_notebook, True, True, 0)
        
        self.content_box.pack_start(controls_box, True, True, 0)
        
        self.show_all()
    
    def _load_data(self):
        """Load current GRUB appearance configuration."""
        # Load available themes
        themes = self.grub_manager.get_available_themes()
        self.theme_combo.remove_all()
        for theme in themes:
            self.theme_combo.append_text(theme)
        
        # Select current theme
        current_theme = self.grub_manager.config.get('GRUB_THEME', '')
        if current_theme:
            # Extract theme name from path
            theme_name = current_theme.split('/')[-2] if '/' in current_theme else current_theme
            model = self.theme_combo.get_model()
            for i, row in enumerate(model):
                if row[0] == theme_name:
                    self.theme_combo.set_active(i)
                    break
        
        # Load background
        bg = self.grub_manager.config.get('GRUB_BACKGROUND', '')
        self.bg_entry.set_text(bg)
        
        # Load colors from config
        self._load_colors_from_config()
        
        # Update preview based on what's configured
        if current_theme:
            self._update_theme_preview(current_theme.split('/')[-2] if '/' in current_theme else '')
        elif bg:
            self._update_background_preview(bg)
        else:
            self.preview_image.set_from_icon_name('image-missing', Gtk.IconSize.DIALOG)
    
    def _grub_color_to_rgba(self, color_name):
        """Convert GRUB color name to RGBA."""
        colors = {
            'black': (0.0, 0.0, 0.0),
            'blue': (0.0, 0.0, 0.7),
            'green': (0.0, 0.7, 0.0),
            'cyan': (0.0, 0.7, 0.7),
            'red': (0.7, 0.0, 0.0),
            'magenta': (0.7, 0.0, 0.7),
            'brown': (0.6, 0.4, 0.2),
            'light-gray': (0.7, 0.7, 0.7),
            'dark-gray': (0.4, 0.4, 0.4),
            'light-blue': (0.4, 0.4, 1.0),
            'light-green': (0.4, 1.0, 0.4),
            'light-cyan': (0.4, 1.0, 1.0),
            'light-red': (1.0, 0.4, 0.4),
            'light-magenta': (1.0, 0.4, 1.0),
            'yellow': (1.0, 1.0, 0.0),
            'white': (1.0, 1.0, 1.0),
        }
        rgb = colors.get(color_name.lower(), (1.0, 1.0, 1.0))
        return Gdk.RGBA(rgb[0], rgb[1], rgb[2], 1.0)
    
    def _load_colors_from_config(self):
        """Load color settings from GRUB config into color buttons."""
        # Default: white text on black background
        default_normal = 'white/black'
        default_highlight = 'black/white'
        
        color_normal = self.grub_manager.config.get('GRUB_COLOR_NORMAL', default_normal)
        color_highlight = self.grub_manager.config.get('GRUB_COLOR_HIGHLIGHT', default_highlight)
        
        # Parse "text/background" format
        if '/' in color_normal:
            text, bg = color_normal.split('/')
            self.text_color_btn.set_rgba(self._grub_color_to_rgba(text))
            self.bg_color_btn.set_rgba(self._grub_color_to_rgba(bg))
        
        if '/' in color_highlight:
            hl_text, hl_bg = color_highlight.split('/')
            self.hl_color_btn.set_rgba(self._grub_color_to_rgba(hl_text))
            self.hl_bg_color_btn.set_rgba(self._grub_color_to_rgba(hl_bg))
    
    def _update_theme_preview(self, theme_name):
        """Update preview with theme image."""
        if not theme_name:
            return
        
        theme_dir = f"/boot/grub/themes/{theme_name}"
        
        # Try different preview/background files in order
        candidates = [
            f"{theme_dir}/preview.png",
            f"{theme_dir}/preview.jpg",
            f"{theme_dir}/background.png",
            f"{theme_dir}/background.jpg",
            f"{theme_dir}/background.jpeg",
        ]
        
        for image_path in candidates:
            try:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(image_path, 280, 180, True)
                self.preview_image.set_from_pixbuf(pixbuf)
                return
            except Exception:
                continue
        
        # No image found
        self.preview_image.set_from_icon_name('image-missing', Gtk.IconSize.DIALOG)
    
    def _update_background_preview(self, bg_path):
        """Update preview with background image."""
        if not bg_path:
            self.preview_image.set_from_icon_name('image-missing', Gtk.IconSize.DIALOG)
            return
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(bg_path, 280, 180, True)
            self.preview_image.set_from_pixbuf(pixbuf)
        except Exception:
            self.preview_image.set_from_icon_name('image-missing', Gtk.IconSize.DIALOG)
    
    def _on_theme_changed(self, combo):
        """Update preview when theme is selected."""
        theme_name = combo.get_active_text()
        if theme_name:
            self._update_theme_preview(theme_name)
    
    def _on_install_theme(self, button):
        """Install a new theme from archive."""
        dialog = Gtk.FileChooserDialog(
            title=_("Select theme archive"),
            parent=self.parent_window,
            action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK
        )
        
        filter_zip = Gtk.FileFilter()
        filter_zip.set_name(_("Theme archives"))
        filter_zip.add_pattern("*.tar.gz")
        filter_zip.add_pattern("*.zip")
        filter_zip.add_pattern("*.tar.xz")
        filter_zip.add_pattern("*.tar.bz2")
        dialog.add_filter(filter_zip)
        
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            theme_path = dialog.get_filename()
            dialog.destroy()
            self._install_theme_from_archive(theme_path)
        else:
            dialog.destroy()
    
    def _install_theme_from_archive(self, archive_path):
        """Extract and install theme from archive."""
        import subprocess
        import os
        import tempfile
        
        themes_dir = "/boot/grub/themes"
        
        try:
            # Create temp dir for extraction
            with tempfile.TemporaryDirectory() as tmpdir:
                # Extract based on file type
                if archive_path.endswith('.zip'):
                    cmd = ['unzip', '-q', archive_path, '-d', tmpdir]
                elif archive_path.endswith('.tar.gz') or archive_path.endswith('.tgz'):
                    cmd = ['tar', '-xzf', archive_path, '-C', tmpdir]
                elif archive_path.endswith('.tar.xz'):
                    cmd = ['tar', '-xJf', archive_path, '-C', tmpdir]
                elif archive_path.endswith('.tar.bz2'):
                    cmd = ['tar', '-xjf', archive_path, '-C', tmpdir]
                else:
                    self._show_error(_("Unsupported archive format"))
                    return
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    self._show_error(_("Failed to extract archive: {}").format(result.stderr))
                    return
                
                # Find theme.txt to determine theme folder
                theme_folder = None
                for root, dirs, files in os.walk(tmpdir):
                    if 'theme.txt' in files:
                        theme_folder = root
                        break
                
                if not theme_folder:
                    self._show_error(_("No theme.txt found in archive"))
                    return
                
                # Get theme name from folder
                theme_name = os.path.basename(theme_folder)
                if theme_name == '': # theme.txt is in root of extraction
                    theme_name = os.path.splitext(os.path.basename(archive_path))[0]
                    theme_name = theme_name.replace('.tar', '')
                
                dest_path = f"{themes_dir}/{theme_name}"
                
                # Copy to themes directory using pkexec
                copy_cmd = ['pkexec', 'cp', '-r', theme_folder, dest_path]
                result = subprocess.run(copy_cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    self._show_info(_("Theme '{}' installed successfully!").format(theme_name))
                    # Refresh theme list
                    self._load_data()
                else:
                    self._show_error(_("Failed to install theme: {}").format(result.stderr))
                    
        except Exception as e:
            self._show_error(_("Error installing theme: {}").format(str(e)))
    
    def _on_apply_theme(self, button):
        """Apply selected theme and clear background + color settings."""
        theme_name = self.theme_combo.get_active_text()
        if not theme_name:
            return
            
        # Confirm with user
        dialog = Gtk.MessageDialog(
            transient_for=self.parent_window,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=_("Apply Theme")
        )
        dialog.format_secondary_text(
            _("Applying theme '{}' will disable any custom background and colors. Continue?").format(theme_name)
        )
        response = dialog.run()
        dialog.destroy()
        
        if response != Gtk.ResponseType.YES:
            return
        
        # Update config: set theme, clear background AND colors (theme has its own)
        new_config = {
            'GRUB_THEME': f"/boot/grub/themes/{theme_name}/theme.txt",
            'GRUB_BACKGROUND': '',
            'GRUB_COLOR_NORMAL': '',
            'GRUB_COLOR_HIGHLIGHT': '',
        }
        
        if self.grub_manager.save_config(new_config):
            self.bg_entry.set_text('')
            self._ask_update_grub(_("Theme applied successfully!"))
    
    def _on_disable_theme(self, button):
        """Disable current theme and set default colors."""
        dialog = Gtk.MessageDialog(
            transient_for=self.parent_window,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=_("Disable Theme")
        )
        dialog.format_secondary_text(_("This will remove the theme and set default colors. Continue?"))
        response = dialog.run()
        dialog.destroy()
        
        if response != Gtk.ResponseType.YES:
            return
        
        # Remove theme but keep default colors so menu is readable
        new_config = {
            'GRUB_THEME': '',
            'GRUB_COLOR_NORMAL': 'white/black',
            'GRUB_COLOR_HIGHLIGHT': 'black/white',
        }
        if self.grub_manager.save_config(new_config):
            self.theme_combo.set_active(-1)
            self.preview_image.set_from_icon_name('image-missing', Gtk.IconSize.DIALOG)
            # Update color buttons to show defaults
            self._load_colors_from_config()
            self._ask_update_grub(_("Theme disabled."))
    
    def _ask_update_grub(self, message):
        """Ask user if they want to run update-grub."""
        dialog = Gtk.MessageDialog(
            transient_for=self.parent_window,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=message
        )
        dialog.format_secondary_text(_("Run update-grub now to apply changes?"))
        response = dialog.run()
        dialog.destroy()
        
        if response == Gtk.ResponseType.YES:
            if self.grub_manager.update_grub():
                info_dialog = Gtk.MessageDialog(
                    transient_for=self.parent_window,
                    flags=0,
                    message_type=Gtk.MessageType.INFO,
                    buttons=Gtk.ButtonsType.OK,
                    text=_("Success")
                )
                info_dialog.format_secondary_text(_("GRUB configuration updated successfully!"))
                info_dialog.run()
                info_dialog.destroy()
            else:
                err_dialog = Gtk.MessageDialog(
                    transient_for=self.parent_window,
                    flags=0,
                    message_type=Gtk.MessageType.ERROR,
                    buttons=Gtk.ButtonsType.OK,
                    text=_("Error")
                )
                err_dialog.format_secondary_text(_("Failed to update GRUB. Check logs for details."))
                err_dialog.run()
                err_dialog.destroy()
    
    def _show_error(self, message):
        """Show error dialog."""
        dialog = Gtk.MessageDialog(
            transient_for=self.parent_window,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=_("Error")
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()
    
    def _show_info(self, message):
        """Show info dialog."""
        dialog = Gtk.MessageDialog(
            transient_for=self.parent_window,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text=_("Information")
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()
    
    def _on_remove_theme(self, button):
        """Remove selected theme from system."""
        theme_name = self.theme_combo.get_active_text()
        if not theme_name:
            return
            
        dialog = Gtk.MessageDialog(
            transient_for=self.parent_window,
            flags=0,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.YES_NO,
            text=_("Remove Theme")
        )
        dialog.format_secondary_text(
            _("This will permanently delete theme '{}'. Are you sure?").format(theme_name)
        )
        response = dialog.run()
        dialog.destroy()
        
        if response != Gtk.ResponseType.YES:
            return
        
        import subprocess
        
        theme_path = f"/boot/grub/themes/{theme_name}"
        
        # Remove theme directory
        result = subprocess.run(['pkexec', 'rm', '-rf', theme_path], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            self._show_info(_("Theme '{}' removed successfully!").format(theme_name))
            # Clear theme config if it was the active one
            current_theme = self.grub_manager.config.get('GRUB_THEME', '')
            if theme_name in current_theme:
                self.grub_manager.save_config({
                    'GRUB_THEME': '',
                    'GRUB_COLOR_NORMAL': 'white/black',
                    'GRUB_COLOR_HIGHLIGHT': 'black/white',
                })
            # Refresh theme list
            self._load_data()
        else:
            self._show_error(_("Failed to remove theme: {}").format(result.stderr))
    
    def _on_bg_entry_changed(self, entry):
        """Update preview when background path changes."""
        bg_path = entry.get_text().strip()
        if bg_path:
            self._update_background_preview(bg_path)
    
    def _on_browse_background(self, button):
        """Browse for background image."""
        dialog = Gtk.FileChooserDialog(
            title=_("Select background image"),
            parent=self.parent_window,
            action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK
        )
        
        filter_images = Gtk.FileFilter()
        filter_images.set_name(_("Images"))
        filter_images.add_pattern("*.png")
        filter_images.add_pattern("*.jpg")
        filter_images.add_pattern("*.jpeg")
        dialog.add_filter(filter_images)
        
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.bg_entry.set_text(dialog.get_filename())
        dialog.destroy()
    
    def _on_remove_background(self, button):
        """Remove the current background setting."""
        dialog = Gtk.MessageDialog(
            transient_for=self.parent_window,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=_("Remove Background")
        )
        dialog.format_secondary_text(_("This will remove the background image from GRUB. Continue?"))
        response = dialog.run()
        dialog.destroy()
        
        if response != Gtk.ResponseType.YES:
            return
        
        # Clear background entry and preview
        self.bg_entry.set_text('')
        self.preview_image.set_from_icon_name('image-missing', Gtk.IconSize.DIALOG)
        
        if self.grub_manager.remove_config_key('GRUB_BACKGROUND'):
            self._ask_update_grub(_("Background removed successfully!"))
    
    def _on_apply_background(self, button):
        """Apply background settings and clear any theme."""
        bg_path = self.bg_entry.get_text().strip()
        
        if not bg_path:
            dialog = Gtk.MessageDialog(
                transient_for=self.parent_window,
                flags=0,
                message_type=Gtk.MessageType.WARNING,
                buttons=Gtk.ButtonsType.OK,
                text=_("No Background")
            )
            dialog.format_secondary_text(_("Please select a background image first."))
            dialog.run()
            dialog.destroy()
            return
        
        # Confirm with user
        dialog = Gtk.MessageDialog(
            transient_for=self.parent_window,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=_("Apply Background")
        )
        dialog.format_secondary_text(
            _("This will disable any theme and use the custom background with your color settings. Continue?")
        )
        response = dialog.run()
        dialog.destroy()
        
        if response != Gtk.ResponseType.YES:
            return
        
        # Get colors as GRUB format (e.g., "white/black")
        def rgba_to_grub_color(rgba):
            """Convert RGBA to closest GRUB color name."""
            # GRUB supports: black, blue, green, cyan, red, magenta, brown, light-gray
            # dark-gray, light-blue, light-green, light-cyan, light-red, light-magenta, yellow, white
            r, g, b = rgba.red, rgba.green, rgba.blue
            
            if r < 0.3 and g < 0.3 and b < 0.3:
                return "black"
            elif r > 0.7 and g > 0.7 and b > 0.7:
                return "white"
            elif r > 0.7 and g > 0.5 and b < 0.3:
                return "yellow"
            elif r > 0.6 and g < 0.4 and b < 0.4:
                return "light-red"
            elif r < 0.4 and g > 0.6 and b < 0.4:
                return "light-green"
            elif r < 0.4 and g < 0.4 and b > 0.6:
                return "light-blue"
            else:
                return "light-gray"
        
        text_color = rgba_to_grub_color(self.text_color_btn.get_rgba())
        bg_color = rgba_to_grub_color(self.bg_color_btn.get_rgba())
        hl_text = rgba_to_grub_color(self.hl_color_btn.get_rgba())
        hl_bg = rgba_to_grub_color(self.hl_bg_color_btn.get_rgba())
        
        new_config = {
            'GRUB_THEME': '',  # Clear theme
            'GRUB_BACKGROUND': bg_path,
            'GRUB_COLOR_NORMAL': f"{text_color}/{bg_color}",
            'GRUB_COLOR_HIGHLIGHT': f"{hl_text}/{hl_bg}",
        }
        
        if self.grub_manager.save_config(new_config):
            # Clear theme selection in UI
            self.theme_combo.set_active(-1)
            self._ask_update_grub(_("Background applied successfully!"))
    
    def get_config(self):
        """Return current configuration from UI."""
        config = {}
        
        theme_name = self.theme_combo.get_active_text()
        if theme_name:
            config['GRUB_THEME'] = f"/boot/grub/themes/{theme_name}/theme.txt"
        
        bg = self.bg_entry.get_text().strip()
        if bg:
            config['GRUB_BACKGROUND'] = bg
        
        return config
    
    # ==================== Font Converter Methods ====================
    
    def _load_installed_fonts(self):
        """Load list of installed GRUB fonts."""
        self.fonts_combo.remove_all()
        
        fonts_dir = "/boot/grub/fonts"
        try:
            import os
            if os.path.exists(fonts_dir):
                for f in sorted(os.listdir(fonts_dir)):
                    if f.endswith('.pf2'):
                        self.fonts_combo.append_text(f)
        except Exception:
            pass
        
        # Select first if available
        if self.fonts_combo.get_model().iter_n_children(None) > 0:
            self.fonts_combo.set_active(0)
    
    def _on_browse_font(self, button):
        """Browse for TTF/OTF font file."""
        dialog = Gtk.FileChooserDialog(
            title=_("Select font file"),
            parent=self.parent_window,
            action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK
        )
        
        filter_fonts = Gtk.FileFilter()
        filter_fonts.set_name(_("Font files"))
        filter_fonts.add_pattern("*.ttf")
        filter_fonts.add_pattern("*.TTF")
        filter_fonts.add_pattern("*.otf")
        filter_fonts.add_pattern("*.OTF")
        dialog.add_filter(filter_fonts)
        
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.font_entry.set_text(dialog.get_filename())
        dialog.destroy()
    
    def _on_convert_font(self, button):
        """Convert TTF/OTF to PF2 and install."""
        import subprocess
        import os
        
        font_path = self.font_entry.get_text().strip()
        if not font_path or not os.path.exists(font_path):
            dialog = Gtk.MessageDialog(
                transient_for=self.parent_window,
                flags=0,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text=_("Error")
            )
            dialog.format_secondary_text(_("Please select a valid font file."))
            dialog.run()
            dialog.destroy()
            return
        
        font_size = int(self.font_size_spin.get_value())
        font_name = os.path.splitext(os.path.basename(font_path))[0]
        output_name = f"{font_name}_{font_size}.pf2"
        output_path = f"/boot/grub/fonts/{output_name}"
        
        # Convert using grub-mkfont
        try:
            cmd = ['pkexec', 'grub-mkfont', '-s', str(font_size), '-o', output_path, font_path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                dialog = Gtk.MessageDialog(
                    transient_for=self.parent_window,
                    flags=0,
                    message_type=Gtk.MessageType.INFO,
                    buttons=Gtk.ButtonsType.OK,
                    text=_("Success")
                )
                dialog.format_secondary_text(_("Font converted and installed: {}").format(output_name))
                dialog.run()
                dialog.destroy()
                
                # Reload fonts list
                self._load_installed_fonts()
            else:
                dialog = Gtk.MessageDialog(
                    transient_for=self.parent_window,
                    flags=0,
                    message_type=Gtk.MessageType.ERROR,
                    buttons=Gtk.ButtonsType.OK,
                    text=_("Error")
                )
                dialog.format_secondary_text(_("Failed to convert font: {}").format(result.stderr))
                dialog.run()
                dialog.destroy()
                
        except Exception as e:
            dialog = Gtk.MessageDialog(
                transient_for=self.parent_window,
                flags=0,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text=_("Error")
            )
            dialog.format_secondary_text(str(e))
            dialog.run()
            dialog.destroy()
    
    def _on_apply_font(self, button):
        """Apply selected font to GRUB configuration."""
        font_name = self.fonts_combo.get_active_text()
        if font_name:
            # GRUB_FONT config
            font_path = f"/boot/grub/fonts/{font_name}"
            print(_("Would set GRUB_FONT={}").format(font_path))
            
            dialog = Gtk.MessageDialog(
                transient_for=self.parent_window,
                flags=0,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                text=_("Font Applied")
            )
            dialog.format_secondary_text(_("Font '{}' will be used after running update-grub.").format(font_name))
            dialog.run()
            dialog.destroy()