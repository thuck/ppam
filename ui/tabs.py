###############################################################################
#PPAM is a pulseaudio interface.
#Copyright (C) 2013  Denis Doria (Thuck)
#
#This program is free software; you can redistribute it and/or
#modify it under the terms of the GNU General Public License
#as published by the Free Software Foundation; version 2
#of the License.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
###############################################################################
import dbus
import curses
from curses import KEY_UP, KEY_DOWN, KEY_ENTER
from itertools import cycle
from functools import partial
from ui.basic import draw_info_window
from ui.basic import draw_help_window
from pulse import pulseaudio as pa
from pulse import components as co


class GenericStream(object):
    def __init__(self, win, footer, stream_type, name, conf = None):
        self.win = win
        self.height, self.width = self.win.getmaxyx()
        self.name = name
        self.conf = conf
        self.help = ["+/- to Increase and decrease volume",
                     ",/. to Increase and decrease right volume",
                     "</> to Increase and decrease left volume",
                     "m to Mute"]
        self.selected_item = 0
        self.max_item = 0
        self.playback = getattr(co, stream_type)()
        self.streams = []
        self.type_of_info = None
        self.info_window_data = None

    def resize_window(self, win):
        self.win = win
        self.height, self.width = self.win.getmaxyx()

    def _update_info_window(self, pid):
        if self.type_of_info == 'p':
            self.info_window_data = self.playback.properties(pid)

        elif self.type_of_info == 'i':
            self.info_window_data = self.playback.info(pid)

        elif self.type_of_info == 'h':
            self.info_window_data = self.help

    def update(self, char):
        if self.selected_item > self.max_item:
                self.selected_item = self.max_item

        if char in (ord('h'), ):
            self.type_of_info = 'h'
            self.info_window_data = self.help

        elif char in (ord('c'), ):
            self.type_of_info = None
            self.info_window_data = None

        elif self.streams:
            pid = self.streams[self.selected_item][1]
            self._update_info_window(pid)
            if char in (ord('+'), ):
                self.playback.increase_volume(pid)

            elif char in (ord('-'), ):
                    self.playback.decrease_volume(pid)

            elif char in (ord('m'),):
                self.playback.mute(pid)

            elif char in (ord('>'), ord('.')):
                self.playback.increase_left_volume(pid)

            elif char in (ord('.'), ):
                self.playback.increase_right_volume(pid)

            elif char in (ord('<'), ):
                self.playback.decrease_left_volume(pid)

            elif char in (ord(','), ):
                self.playback.decrease_right_volume(pid)

            elif char in (ord('p'), ):
                self.type_of_info = 'p'
                self.info_window_data = self.playback.properties(pid)

            elif char in (ord('i'), ):
                self.type_of_info = 'i'
                self.info_window_data = self.playback.info(pid)

            elif char == KEY_UP and self.selected_item > 0:
                self.selected_item -= 1

            elif char == KEY_DOWN and self.selected_item < self.max_item:
                self.selected_item += 1

    def draw(self):
        self.streams = self.playback.playing()
        line_number = 0

        self.win.erase()
        self.win.box()

        for line_number, stream in enumerate(self.streams):
            (app_name,
            app_pid,
            volume_left,
            volume_right,
            mute) = stream
            line = '[%s] L:%i%% R:%i%% (%s)' % (app_name, volume_left, volume_right, app_pid)

            if mute:
                line = '%s [M]' % (line)

            if self.selected_item == line_number:
                self.win.addstr(line_number + 1, 1, line, curses.color_pair(1))
        
            else:
                self.win.addstr(line_number + 1, 1, line)

        self.max_item = line_number

        if self.info_window_data:
            draw_info_window(self.win, self.info_window_data)

        self.win.refresh()


class TabPlayback(GenericStream):
    def __init__(self, win, footer, conf = None):
        GenericStream.__init__(self, win, footer, 'Playback', 'Playback', conf)

class TabRecord(GenericStream):
    def __init__(self, win, footer, conf = None):
        GenericStream.__init__(self, win, footer, 'Record', 'Record', conf)

    
class GenericDevice(object):
    def __init__(self, win, footer, device_type, name, conf = None):
        self.win = win
        self.height, self.width = self.win.getmaxyx()
        self.name = name
        self.conf = conf
        self.help = ["+/- to Increase and decrease volume",
                     ",/. to Increase and decrease right volume",
                     "</> to Increase and decrease left volume",
                     "m to Mute"]
        self.selected_item = 0
        self.max_item = 0
        self.device = getattr(co, device_type)()
        self.devices = []
        self.type_of_info = None
        self.info_window_data = None

    def resize_window(self, win):
        self.win = win
        self.height, self.width = self.win.getmaxyx()

    def _update_info_window(self, info):
        if self.type_of_info == 'p':
            self.info_window_data = self.device.properties(info)

        elif self.type_of_info == 'i':
            self.info_window_data = self.device.info(info)

        elif self.type_of_info == 'h':
            self.info_window_data = self.help

    def update(self, char):
        if self.selected_item > self.max_item:
                self.selected_item = self.max_item

        if char in (ord('h'), ):
            self.type_of_info = 'h'
            self.info_window_data = self.help

        elif char in (ord('c'), ):
            self.type_of_info = None
            self.info_window_data = None

        elif self.devices:
            name = self.devices[self.selected_item][0]
            self._update_info_window(name)
            
            if char in (ord('+'), ):
                self.device.increase_volume(name)

            elif char in (ord('-'), ):
                    self.device.decrease_volume(name)

            elif char in (ord('m'),):
                self.device.mute(name)

            elif char in (ord('>'), ord('.')):
                self.device.increase_left_volume(name)

            elif char in (ord('.'), ):
                self.device.increase_right_volume(name)

            elif char in (ord('<'), ):
                self.device.decrease_left_volume(name)

            elif char in (ord(','), ):
                self.device.decrease_right_volume(name)

            elif char in (ord('p'), ):
                self.type_of_info = 'p'
                self.info_window_data = self.device.properties(name)

            elif char in (ord('i'), ):
                self.type_of_info = 'i'
                self.info_window_data = self.device.info(name)

            elif char in (ord('l'), ):
                self.device.change_port_next(name)

            elif char in (ord('k'), ):
                self.device.change_port_previous(name)

            elif char == KEY_UP and self.selected_item > 0:
                self.selected_item -= 1

            elif char == KEY_DOWN and self.selected_item < self.max_item:
                self.selected_item += 1


    def draw(self):
        self.devices = self.device.get_devices()
        line_number = 0

        self.win.erase()
        self.win.box()

        for line_number, device in enumerate(self.devices):
            (device_name,
            volume_left,
            volume_right,
            mute,
            port) = device
            line = '[%s] L:%i%% R:%i%%' % (device_name.split('.')[-1].capitalize(), volume_left, volume_right)

            if port:
                str_port = ''
                for i in port:
                    if i[0] == True:
                        str_port = '%s (%s)' % (str_port, i[1].split('-')[-1].capitalize())

                    else:
                        str_port = '%s %s' % (str_port, i[1].split('-')[-1].capitalize())

                line = '%s [%s]' % (line, str_port.strip())

            if mute:
                line = '%s [M]' % (line)

            if self.selected_item == line_number:
                self.win.addstr(line_number + 1, 1, line, curses.color_pair(1))
        
            else:
                self.win.addstr(line_number + 1, 1, line)

        self.max_item = line_number

        if self.info_window_data:
            draw_info_window(self.win, self.info_window_data)

        self.win.refresh()


class TabOutputDevices(GenericDevice):
    def __init__(self, win, footer, conf = None):
        GenericDevice.__init__(self, win, footer, 'OutputDevices', 'Output Devices', conf = None)

class TabInputDevices(GenericDevice):
    def __init__(self, win, footer, conf = None):
        GenericDevice.__init__(self, win, footer, 'InputDevices', 'Input Devices', conf = None)

class TabCards(object):
    def __init__(self, win, footer, conf = None):
        self.win = win
        self.height, self.width = self.win.getmaxyx()
        self.name = 'Cards'
        self.conf = conf
        self.help = ["Nothing here"]
        self.conn = pa.dbus_connection()
        self.core = pa.Core(self.conn)
        self.card = co.Cards()
        self.cards = []
        self.selected_item = 0
        self.max_item = 0
        self.type_of_info = None
        self.info_window_data = None

    def resize_window(self, win):
        self.win = win
        self.height, self.width = self.win.getmaxyx()

    def _update_info_window(self, info):
            if self.type_of_info == 'p':
                self.info_window_data = self.card.properties(info)

            elif self.type_of_info == 'i':
                self.info_window_data = self.card.info(info)

            elif self.type_of_info == 'h':
                self.info_window_data = self.help

    def update(self, char):
        if self.selected_item > self.max_item:
            self.selected_item = self.max_item

        if char in (ord('h'), ):
            self.type_of_info = 'h'
            self.info_window_data = self.help

        elif char in (ord('c'), ):
            self.type_of_info = None
            self.info_window_data = None

        elif self.cards:

            info = self.cards[self.selected_item]
            self._update_info_window(info)
    
            if char == ord('a'):
                #testing code - Doesn't work
            #    self.cards[0].active_profile = self.profiles[self.selected_item].profile_name
                pass
    
            elif char in (ord('p'), ):
                self.type_of_info = 'p'
                self.info_window_data = self.card.properties(info)
    
            elif char in (ord('i'), ):
                self.type_of_info = 'i'
                self.info_window_data = self.card.info(info)

            elif char == KEY_UP and self.selected_item > 0:
                self.selected_item -= 1

            elif char == KEY_DOWN and self.selected_item < self.max_item:
                self.selected_item += 1

    def draw(self):
        self.cards = self.card.get_cards()
        line_number = 0

        self.win.erase()
        self.win.box()

        for line_number, card in enumerate(self.cards):
            (card_name,
            profile_name,
            active) = card
            line = '[%s] %s' % (card_name, profile_name.replace('output', 'Out').replace('input', 'In').replace('+', ' '))

            if active:
                line = '%s [A]' % (line)

            if self.selected_item == line_number:
                self.win.addstr(line_number + 1, 1, line, curses.color_pair(1))

            else:
                self.win.addstr(line_number + 1, 1, line)

        self.max_item = line_number

        if self.info_window_data:
            draw_info_window(self.win, self.info_window_data)

        self.win.refresh()


