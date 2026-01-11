"""
Main application class for Soplos Grub Editor.
Handles application lifecycle, initialization, and coordination between modules.
"""

import sys
import os
import signal
from pathlib import Path

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, Gio

from .environment import get_environment_detector
from .theme_manager import get_theme_manager, initialize_theming
from .i18n_manager import get_i18n_manager, initialize_i18n, _
from .grub_manager import get_grub_manager
from utils.logger import log_info, log_error, log_warning

# Constants (Move to a config file ideally, but here for now)
APP_ID = "org.soplos.grubeditor"
APP_NAME = "Soplos GRUB Editor"
APP_VERSION = "2.0.0"


class SoplosGrubEditorApplication(Gtk.Application):
    """
    Main application class for Soplos Grub Editor.
    Manages the application lifecycle and coordinates between all components.
    """
    
    def __init__(self):
        """Initialize the application."""
        super().__init__(
            application_id=APP_ID,
            flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE
        )
        
        # Application state
        self.main_window = None
        self.environment_detector = None
        self.theme_manager = None
        self.i18n_manager = None
        self.grub_manager = None
        
        # Application paths
        self.app_path = Path(__file__).parent.parent
        self.assets_path = self.app_path / 'assets'
        self.locale_path = self.app_path / 'locale'
        
        # Connect signals
        self.connect('startup', self.on_startup)
        self.connect('activate', self.on_activate)
        self.connect('command-line', self.on_command_line)
        self.connect('shutdown', self.on_shutdown)
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)
        
    def on_shutdown(self, app):
        """Called when the application shuts down."""
        log_info(_("Shutting down Soplos Grub Editor..."))
        self._cleanup_garbage()

    def _cleanup_garbage(self):
        """Remove __pycache__ and other temporary files."""
        try:
            import shutil
            root_path = self.app_path
            
            # Clean __pycache__
            for root, dirs, files in os.walk(root_path):
                if '__pycache__' in dirs:
                    pycache_path = os.path.join(root, '__pycache__')
                    try:
                        shutil.rmtree(pycache_path, ignore_errors=True)
                    except Exception:
                        pass
        except Exception as e:
            log_warning(_("Cleanup warning: {err}").format(err=e))
    
    def on_startup(self, app):
        """Called when the application starts up."""
        log_info(_("Starting {name} v{ver}...").format(name=APP_NAME, ver=APP_VERSION))
        
        # Initialize core systems
        self._initialize_environment()
        self._initialize_internationalization()
        self._initialize_theming()
        self._initialize_grub_manager()
        self._setup_application_properties()
        
        log_info(_("Application initialization completed"))
    
    def on_activate(self, app):
        """Called when the application is activated."""
        if self.main_window is None:
            self._create_main_window()
        
        # Present the window
        if self.main_window:
            self.main_window.present()
    
    def on_command_line(self, app, command_line):
        """Handle command line arguments."""
        args = command_line.get_arguments()
        # Simple handling for now
        self.activate()
        return 0
    
    def _initialize_environment(self):
        """Initialize environment detection."""
        try:
            self.environment_detector = get_environment_detector()
            # Load any parent-provided hints first, then configure environment
            # variables (so Gtk.Settings sees the right backend), then detect.
            self.environment_detector.load_parent_hints()
            self.environment_detector.configure_environment_variables()
            env_info = self.environment_detector.detect_all()

            log_info(_("Desktop Environment: {env}").format(env=env_info['desktop_environment']))
            
        except Exception as e:
            log_error(_("Error initializing environment detection: {err}").format(err=e))
    
    def _initialize_internationalization(self):
        """Initialize the internationalization system."""
        try:
            current_lang = initialize_i18n(str(self.locale_path))
            self.i18n_manager = get_i18n_manager()
            log_info(_("Language initialized: {lang}").format(lang=current_lang))
            
            # Set up gettext
            import gettext
            gettext.bindtextdomain('soplos-grub-editor', str(self.locale_path))
            gettext.textdomain('soplos-grub-editor')
            
        except Exception as e:
            log_error(_("Error initializing internationalization: {err}").format(err=e))
    
    def _initialize_theming(self):
        """Initialize the theming system."""
        try:
            loaded_theme = initialize_theming(str(self.assets_path))
            self.theme_manager = get_theme_manager()
            log_info(_("Theme loaded: {theme}").format(theme=loaded_theme))
        except Exception as e:
            log_error(_("Error initializing theming: {err}").format(err=e))

    def _initialize_grub_manager(self):
        """Initialize the GRUB manager."""
        try:
            self.grub_manager = get_grub_manager()
            # Pre-load config to check for errors/access
            self.grub_manager.read_config()
            log_info(_("GRUB Manager initialized"))
        except Exception as e:
            log_error(_("Error initializing GRUB Manager: {err}").format(err=e))
    
    def _setup_application_properties(self):
        """Setup application-wide properties."""
        GLib.set_prgname(APP_ID)
        GLib.set_application_name(_(APP_NAME))
        
        # Set WM_CLASS
        if hasattr(Gdk, 'set_program_class'):
            Gdk.set_program_class(APP_ID)
        
        # Set default window icon if available
        icon_path = self.assets_path / 'icons' / 'org.soplos.grubeditor.png'
        if icon_path.exists():
            try:
                Gtk.Window.set_default_icon_from_file(str(icon_path))
            except Exception as e:
                log_warning(_("Error setting application icon: {err}").format(err=e))

        # Setup application menu for GNOME integration (if appropriate)
        try:
            if self.environment_detector and getattr(self.environment_detector.desktop_environment, 'value', str(self.environment_detector.desktop_environment)).lower() == 'gnome':
                self._setup_application_menu()
        except Exception:
            pass
    
    def _create_main_window(self):
        """Create the main application window."""
        try:
            # Import here to avoid circular imports
            # Note: ui.main_window will be implemented in the next steps
            from ui.main_window import MainWindow
            
            self.main_window = MainWindow(
                application=self,
                environment_detector=self.environment_detector,
                theme_manager=self.theme_manager,
                i18n_manager=self.i18n_manager,
                grub_manager=self.grub_manager
            )
            
            # Connect window destroy signal
            self.main_window.connect('destroy', self._on_window_destroy)
            
        except Exception as e:
            log_error(_("Error creating main window: {err}").format(err=e))
            import traceback
            traceback.print_exc()
            self.quit()

    def _setup_application_menu(self):
        """Setup application menu for GNOME integration."""
        try:
            if self.environment_detector and getattr(self.environment_detector.desktop_environment, 'value', str(self.environment_detector.desktop_environment)).lower() == 'gnome':
                menu = Gio.Menu()

                # About action
                about_action = Gio.SimpleAction.new('about', None)
                about_action.connect('activate', lambda a, b: None)
                self.add_action(about_action)
                menu.append(_('About'), 'app.about')

                # Quit action
                quit_action = Gio.SimpleAction.new('quit', None)
                quit_action.connect('activate', lambda a, b: self.quit())
                self.add_action(quit_action)
                menu.append(_('Quit'), 'app.quit')

                self.set_app_menu(menu)
        except Exception as e:
            log_warning(_("Error setting up application menu: {err}").format(err=e))
    
    def _on_window_destroy(self, window):
        """Handle main window destruction."""
        self.main_window = None
        self.quit()
    
    def _handle_signal(self, signum, frame):
        """Handle system signals for graceful shutdown."""
        log_info(_("Received signal {num}, shutting down...").format(num=signum))
        GLib.idle_add(self.quit)


def run_application(argv: list = None) -> int:
    """Run the application."""
    if argv is None:
        argv = sys.argv
    
    app = SoplosGrubEditorApplication()
    
    try:
        return app.run(argv)
    except KeyboardInterrupt:
        return 0
    except Exception as e:
        log_error(_("Application error: {err}").format(err=e))
        return 1
