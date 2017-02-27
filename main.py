import os

import subprocess

os.environ['KIVY_METRICS_FONTSCALE'] = '1.8'

import kivy
kivy.require('1.9.0')

from os import listdir, path

from kivy.app import App
from kivy.config import Config
from kivy.core.window import Window
from kivy.adapters.listadapter import ListAdapter
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.listview import ListItemButton, ListView
from kivy.uix.boxlayout import BoxLayout

Config.set('graphics', 'width', '2048')
Config.set('graphics', 'height', '1024')
Config.set('kivy', option='desktop', value=1)


class CollectorScreenManager(ScreenManager):
    screen_import_browser = ObjectProperty(None)
    screen_import_music = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(CollectorScreenManager, self).__init__(**kwargs)
        self._keyboard_init()

    def change_screen(self, where_to):
        self.current = where_to
        self._keyboard_init()

    def _keyboard_init(self):
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if self.current == 'screen_import_browser':
            self._keybind_file_browser(self.screen_import_browser.filebrowser, keycode)

    def _keybind_file_browser(self, filebrowser, keycode):
        selected_index = filebrowser.file_list_adapter.selection[0].index

        try:
            if keycode[0] == 273:
                index = selected_index - 1
                if not filebrowser.file_list_adapter.get_view(index).is_selected:
                    filebrowser.file_list_adapter.get_view(index).trigger_action(duration=0)
            elif keycode[0] == 274:
                index = selected_index + 1
                if not filebrowser.file_list_adapter.get_view(index).is_selected:
                    filebrowser.file_list_adapter.get_view(index).trigger_action(duration=0)
            elif keycode[0] == 105:
                self.current = 'screen_import_music'
            elif keycode[0] == 13:
                folder = filebrowser.file_list_adapter.selection[0]
                filebrowser._load_direactory(folder.text)

        except AttributeError as e:
            pass

class CollectorApp(App):
    def build(self):
        Window.size = (2400, 1000)
        manager = CollectorScreenManager()
        return manager


class CollectorLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(CollectorLayout, self).__init__(**kwargs)


class ScreenImportBrowser(Screen):
    def __init__(self, **kwargs):
        super(ScreenImportBrowser, self).__init__(**kwargs)

        self.filebrowser = ObjectProperty(None)


class ScreenImportMusic(Screen):
    pass

class FileBrowserView(GridLayout):
    '''Implementation of a list view with a kv template used for the list
    item class.
    '''
    def __init__(self, **kwargs):
        kwargs['cols'] = 1
        super(FileBrowserView, self).__init__(**kwargs)


        self.browsing_directory = path.expanduser("~")

        self.file_list_adapter = ListAdapter(
            data=[],
            cls=ListItemButton,
            allow_empty_selection=False
        )
        self._load_direactory()

        list_view = ListView(adapter=self.file_list_adapter)
        self.add_widget(list_view)



    def _load_direactory(self, next_step=''):
        browse_next = os.path.abspath(os.path.join(self.browsing_directory, next_step))

        if os.path.isdir(browse_next):
            items = listdir(browse_next)
            items = [item for item in items if item[0] != "."]
            self.browsing_directory = browse_next
            self.file_list_adapter.data = [".."] + sorted(items, key=lambda s: s.lower())
        elif os.path.isfile(browse_next):
            # TODO This is too specific for linux, add other OS support
            subprocess.call(['xdg-open', browse_next])


if __name__ == '__main__':
    CollectorApp().run()
