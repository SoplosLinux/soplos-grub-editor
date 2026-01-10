"""
Main Application Window for Soplos Grub Editor.
Handles the main UI layout and interaction using Notebook Tabs.
Strict Soplos Welcome style: Header + Content (Tabs) + Footer.
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, Pango

from core.i18n_manager import _

# App constants
APP_NAME = "Soplos GRUB Editor"
APP_VERSION = "2.0.0"
DEFAULT_WINDOW_WIDTH = 900
DEFAULT_WINDOW_HEIGHT = 500

from ui.views.general_view import GeneralView
from ui.views.boot_entries_view import BootEntriesView
from ui.views.appearance_view import AppearanceView


class MainWindow(Gtk.ApplicationWindow):
    """Main application window for Soplos Grub Editor."""
    
    def __init__(self, application, environment_detector, theme_manager, i18n_manager, grub_manager):
        """Initialize the main window."""
        super().__init__(application=application)
        
        # Store manager references
        self.application = application
        self.environment_detector = environment_detector
        self.theme_manager = theme_manager
        self.i18n_manager = i18n_manager
        self.grub_manager = grub_manager
        
        # Window properties
        self.set_title(_(APP_NAME))
        self.set_default_size(DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)
        self.set_position(Gtk.WindowPosition.CENTER)
        
        # Apply CSS classes (matching Welcome apps)
        self.get_style_context().add_class('soplos-window')
        try:
            self.get_style_context().add_class('soplos-welcome-window')
            self.set_name('main-window')
        except Exception:
            pass
        
        # Create header bar (before UI setup)
        self._create_header_bar_with_fallback()
        
        # Setup main UI
        self._setup_ui()
        
        # Show everything
        self.show_all()
        
        # Set default tab and update system info
        GLib.idle_add(lambda: self.notebook.set_current_page(0))
        self._update_system_info()
        
        # Connect signals
        self.connect('delete-event', self._on_delete_event)
        self.connect('key-press-event', self._on_key_press)
        
        print("Main window created successfully")

    def _create_header_bar_with_fallback(self):
        """Create HeaderBar exactly like Welcome Live - CLEAN without custom buttons.
        
        Matches the behavior used by Soplos Welcome Live: create a minimal CSD
        HeaderBar on GNOME-like environments and use native decorations on
        XFCE/KDE/Plasma.
        """
        desktop_env = 'unknown'
        try:
            if self.environment_detector:
                desktop_env = getattr(
                    self.environment_detector.desktop_environment, 
                    'value', 
                    str(self.environment_detector.desktop_environment)
                ).lower()
        except Exception:
            pass

        print(f"[DEBUG] Desktop detected: {desktop_env}")

        # If XFCE/KDE, use native decorations (SSD)
        if desktop_env in ['xfce', 'kde', 'plasma']:
            print("Using native window decorations (SSD) for compatibility")
            return

        # If GNOME or others, use CSD (CLEAN - no custom buttons like Welcome Live)
        print("Creating Client-Side Decorations (CSD)")
        header = Gtk.HeaderBar()
        header.set_show_close_button(True)
        header.set_title(_(APP_NAME))
        
        try:
            header.set_has_subtitle(True)
            header.set_subtitle(f"v{APP_VERSION}")
        except Exception:
            pass

        # Force layout to match Welcome Live exactly
        header.set_decoration_layout("menu:minimize,maximize,close")
        header.get_style_context().add_class('titlebar')
        
        # NO custom buttons - keep it clean like Welcome Live
        # If you need language/theme controls, add them to the UI content instead
        
        # Set as titlebar (NO header.show_all())
        self.set_titlebar(header)
        self.header = header

    def _setup_ui(self):
        """Initializes the main UI, matching the Welcome layout."""
        # Main vertical container
        main_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(main_vbox)

        # --- TAB CONTENT (Notebook) ---
        self.notebook = Gtk.Notebook()
        self.notebook.set_scrollable(True)
        self.notebook.set_tab_pos(Gtk.PositionType.TOP)
        self.notebook.set_show_tabs(True)
        self.notebook.set_show_border(False)
        
        try:
            self.notebook.get_style_context().add_class('soplos-notebook')
        except Exception:
            pass
        
        try:
            self._apply_notebook_custom_css()
        except Exception:
            pass
        
        # Pack notebook (main content area)
        main_vbox.pack_start(self.notebook, True, True, 0)

        # Create all tabs (matching legacy GRUB Editor)
        # Tab 1: General Configuration
        self.general_view = GeneralView(self)
        self._add_tab(self.general_view, _("General Configuration"), "preferences-system")

        # Tab 2: Boot Entries
        self.boot_entries_view = BootEntriesView(self)
        self._add_tab(self.boot_entries_view, _("Boot Entries"), "system-run")

        # Tab 3: Appearance
        self.appearance_view = AppearanceView(self)
        self._add_tab(self.appearance_view, _("Appearance"), "preferences-desktop-theme")

        # --- HIDDEN PROGRESS BAR (Bottom, Welcome Live style) ---
        self.progress_revealer = Gtk.Revealer()
        self.progress_revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_UP)

        progress_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        progress_box.set_margin_start(20)
        progress_box.set_margin_end(20)
        progress_box.set_margin_bottom(10)

        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_show_text(True)
        progress_box.pack_start(self.progress_bar, False, False, 0)

        self.progress_label = Gtk.Label(label=_("Ready"))
        progress_box.pack_start(self.progress_label, False, False, 0)

        self.progress_revealer.add(progress_box)
        self.progress_revealer.set_reveal_child(False)
        
        # Pack progress at the end (bottom of window, before status bar)
        main_vbox.pack_end(self.progress_revealer, False, True, 0)

        # --- FOOTER (Status Bar) ---
        self._create_status_bar(main_vbox)

    def _add_tab(self, content_widget, title, icon_name):
        """Helper to add tabs with icons."""
        label_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.MENU)
        label = Gtk.Label(label=title)
        
        label_box.pack_start(icon, False, False, 0)
        label_box.pack_start(label, False, False, 0)
        label_box.show_all()
        
        self.notebook.append_page(content_widget, label_box)

    def _apply_notebook_custom_css(self):
        """Apply custom CSS to make the notebook tab bar thicker (copied from Soplos Welcome)."""
        css_provider = Gtk.CssProvider()
        css_data = """
        notebook > header {
            min-height: 20px;
            padding: 0px 0;
        }
        
        notebook > header > tabs > tab {
            min-height: 20px;
            padding: 8px 12px;
        }
        
        notebook > header > tabs > tab label {
            padding: 4px 8px;
        }
        """
        try:
            css_provider.load_from_data(css_data.encode('utf-8'))
            screen = Gdk.Screen.get_default()
            style_context = Gtk.StyleContext()
            style_context.add_provider_for_screen(
                screen,
                css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )
        except Exception as e:
            print(f"Error applying notebook CSS: {e}")

    def _create_status_bar(self, main_vbox):
        """Create footer status bar."""
        status_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        status_box.set_margin_start(15)
        status_box.set_margin_end(15)
        status_box.set_margin_top(8)
        status_box.set_margin_bottom(8)
        
        # Left: System Info
        self.system_label = Gtk.Label()
        self.system_label.set_halign(Gtk.Align.START)
        self.system_label.get_style_context().add_class('dim-label')
        status_box.pack_start(self.system_label, False, False, 0)
        
        # Right: App Version (only version, no name)
        version_text = f"v{APP_VERSION}"
        version_label = Gtk.Label(label=version_text)
        version_label.set_halign(Gtk.Align.END)
        version_label.get_style_context().add_class('dim-label')
        status_box.pack_end(version_label, False, False, 0)
        
        # Pack at the very end (after progress revealer)
        main_vbox.pack_end(status_box, False, False, 0)

    def _update_system_info(self):
        """Detect and display system info."""
        env_info = self.environment_detector.detect_all()
        desktop = env_info['desktop_environment']
        protocol = env_info['display_protocol']
        
        desktop_name = self._translate_desktop_name(desktop)
        protocol_name = self._translate_protocol_name(protocol)
        
        self.system_label.set_text(_("Running on {} ({})").format(desktop_name, protocol_name))

    def _translate_desktop_name(self, desktop_env):
        """Translate desktop environment name."""
        desktop_map = {
            'gnome': _("GNOME"),
            'kde': _("KDE Plasma"),
            'plasma': _("KDE Plasma"),
            'xfce': _("XFCE"),
            'unknown': _("Unknown")
        }
        return desktop_map.get(desktop_env.lower(), _("Unknown"))
    
    def _translate_protocol_name(self, protocol):
        """Translate display protocol name."""
        protocol_map = {
            'x11': _("X11"),
            'wayland': _("Wayland"),
            'unknown': _("Unknown")
        }
        return protocol_map.get(protocol.lower(), _("Unknown"))

    def show_progress(self, message, fraction=None):
        """
        Show progress bar with message.
        
        Args:
            message: Progress message to display
            fraction: Progress fraction (0.0-1.0), None for pulse mode
        """
        self.progress_label.set_text(message)
        
        if fraction is not None:
            self.progress_bar.set_fraction(fraction)
            self.progress_bar.set_text(f"{int(fraction * 100)}%")
        else:
            self.progress_bar.pulse()
            self.progress_bar.set_text(_("Working..."))
        
        self.progress_revealer.set_reveal_child(True)
        
        # Process pending events to update UI
        while Gtk.events_pending():
            Gtk.main_iteration()

    def hide_progress(self):
        """Hide progress bar."""
        self.progress_revealer.set_reveal_child(False)
        self.progress_label.set_text(_("Ready"))
        self.progress_bar.set_fraction(0.0)
        self.progress_bar.set_text("")

    # ==================== Event Handlers ====================

    def _on_delete_event(self, widget, event):
        """Handle window close event."""
        print("Main window closing...")
        return False  # Allow window to close

    def _on_key_press(self, widget, event):
        """Handle key press events."""
        keyval = event.keyval
        state = event.state
        
        # Check for Ctrl+Q to quit
        if state & Gdk.ModifierType.CONTROL_MASK:
            if keyval == Gdk.KEY_q:
                self.close()
                return True
            
            # Ctrl+Tab to switch tabs
            elif keyval == Gdk.KEY_Tab:
                current_page = self.notebook.get_current_page()
                total_pages = self.notebook.get_n_pages()
                next_page = (current_page + 1) % total_pages
                self.notebook.set_current_page(next_page)
                return True
        
        return False
