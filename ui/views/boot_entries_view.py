"""
Boot Entries View for Soplos Grub Editor.
Replicates legacy v1.x functionality with modern Soplos styling.
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Pango

from core.i18n_manager import _


class BootEntriesView(Gtk.Box):
    """Boot entries management tab - matches legacy GRUB Editor functionality."""
    
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
        self._load_entries()
        
    def _create_ui(self):
        """Create the UI matching legacy layout."""
        # Scrolled window for the list
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_vexpand(True)
        
        # TreeView for boot entries
        # Columns: #, Name, Type, Path, Enabled
        self.store = Gtk.ListStore(int, str, str, str, bool)
        self.tree = Gtk.TreeView(model=self.store)
        self.tree.set_headers_visible(True)
        self.tree.get_style_context().add_class('soplos-card')
        
        # Column: #
        renderer_num = Gtk.CellRendererText()
        col_num = Gtk.TreeViewColumn("#", renderer_num, text=0)
        col_num.set_min_width(30)
        self.tree.append_column(col_num)
        
        # Column: Name
        renderer_name = Gtk.CellRendererText()
        renderer_name.set_property("ellipsize", Pango.EllipsizeMode.END)
        col_name = Gtk.TreeViewColumn(_("Name:"), renderer_name, text=1)
        col_name.set_min_width(300)
        col_name.set_expand(True)
        self.tree.append_column(col_name)
        
        # Column: Type
        renderer_type = Gtk.CellRendererText()
        col_type = Gtk.TreeViewColumn(_("Type:"), renderer_type, text=2)
        col_type.set_min_width(80)
        self.tree.append_column(col_type)
        
        # Column: Path
        renderer_path = Gtk.CellRendererText()
        renderer_path.set_property("ellipsize", Pango.EllipsizeMode.MIDDLE)
        col_path = Gtk.TreeViewColumn(_("Path"), renderer_path, text=3)
        col_path.set_min_width(150)
        self.tree.append_column(col_path)
        
        # Column: Enabled (checkbox)
        renderer_enabled = Gtk.CellRendererToggle()
        renderer_enabled.connect("toggled", self._on_entry_toggled)
        col_enabled = Gtk.TreeViewColumn(_("Enabled"), renderer_enabled, active=4)
        col_enabled.set_min_width(80)
        self.tree.append_column(col_enabled)
        
        scrolled.add(self.tree)
        self.pack_start(scrolled, True, True, 0)
        
        # Button bar
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        
        add_btn = Gtk.Button(label=_("Add entry"))
        add_btn.get_style_context().add_class('suggested-action')
        add_btn.connect('clicked', self._on_add_entry)
        button_box.pack_start(add_btn, False, False, 0)
        
        remove_btn = Gtk.Button(label=_("Remove entry"))
        remove_btn.get_style_context().add_class('destructive-action')
        remove_btn.connect('clicked', self._on_remove_entry)
        button_box.pack_start(remove_btn, False, False, 0)
        
        self.pack_start(button_box, False, False, 0)
        
        self.show_all()
    
    def _load_entries(self):
        """Load boot entries from GRUB configuration."""
        self.store.clear()
        
        # Parse grub.cfg for menu entries
        entries = self.grub_manager.get_menu_entries()
        
        for i, entry in enumerate(entries):
            self.store.append([
                i,
                entry.get('name', f'Entry {i}'),
                entry.get('type', 'system'),
                entry.get('path', ''),
                entry.get('enabled', True)
            ])
    
    def _on_entry_toggled(self, renderer, path):
        """Toggle entry enabled state."""
        self.store[path][4] = not self.store[path][4]
    
    def _on_add_entry(self, button):
        """Add a new boot entry."""
        dialog = Gtk.MessageDialog(
            transient_for=self.parent_window,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text=_("Add Entry")
        )
        dialog.format_secondary_text(_("Custom entry dialog - TODO"))
        dialog.run()
        dialog.destroy()
    
    def _on_remove_entry(self, button):
        """Remove selected boot entry."""
        selection = self.tree.get_selection()
        model, treeiter = selection.get_selected()
        if treeiter:
            entry_name = model[treeiter][1]
            dialog = Gtk.MessageDialog(
                transient_for=self.parent_window,
                flags=0,
                message_type=Gtk.MessageType.QUESTION,
                buttons=Gtk.ButtonsType.YES_NO,
                text=_("Remove Entry")
            )
            dialog.format_secondary_text(_("Remove entry '{}'?").format(entry_name))
            response = dialog.run()
            dialog.destroy()
            
            if response == Gtk.ResponseType.YES:
                model.remove(treeiter)
