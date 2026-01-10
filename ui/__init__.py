"""
User interface module for Soplos Grub Editor.
Contains all GTK-based UI components, windows, tabs, widgets, and dialogs.
"""

from core.application import APP_VERSION

# UI module information
__version__ = APP_VERSION
__author__ = "Sergi Perich"

# UI Constants
DEFAULT_WINDOW_WIDTH = 1000
DEFAULT_WINDOW_HEIGHT = 700
MIN_WINDOW_WIDTH = 800
MIN_WINDOW_HEIGHT = 600

# CSS Classes
CSS_CLASSES = {
    'window': 'soplos-window', # repo-selector uses soplos-window, welcome uses soplos-welcome-window. Sticking to generic or standard.
    'content': 'soplos-content',
    'tab': 'soplos-tab',
    'card': 'soplos-card',
    'button_install': 'soplos-button-install',
    'button_uninstall': 'soplos-button-uninstall',
    'button_primary': 'soplos-button-primary',
    'status_label': 'soplos-status-label',
    'progress_bar': 'soplos-progress-bar',
    'icon_large': 'soplos-icon-large',
    'icon_medium': 'soplos-icon-medium',
    'icon_small': 'soplos-icon-small',
    'separator': 'soplos-separator',
    'welcome_title': 'soplos-welcome-title',
    'welcome_subtitle': 'soplos-welcome-subtitle',
    'software_grid': 'soplos-software-grid',
    'software_item': 'soplos-software-item',
    'hardware_info': 'soplos-hardware-info'
}
