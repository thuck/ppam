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
from pulse import pulseaudio as pa
from pulse import components as co
from itertools import cycle
from functools import partial
import curses
from curses import KEY_UP, KEY_DOWN, KEY_ENTER
import dbus
from basic import draw_info_window

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
        self.info_window = False

    def resize_window(self, win):
        self.win = win
        self.height, self.width = self.win.getmaxyx()

    def update(self, char):
        if char == KEY_UP and self.selected_item > 0:
            self.selected_item -= 1

        elif char == KEY_DOWN and self.selected_item < self.max_item:
            self.selected_item += 1

        if self.streams:
            pid = self.streams[self.selected_item][1]
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
                self.info_window = not self.info_window
                self.info_window_data = partial(self.playback.properties, pid)

            elif char in (ord('i'), ):
                self.info_window = not self.info_window
                self.info_window_data = partial(self.playback.info, pid)

            if self.selected_item > self.max_item:
                self.selected_item = self.max_item


    def draw(self):
        self.streams = self.playback.playing()
        line_number = 0
        if self.info_window:
            info_data = self.info_window_data()

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

        self.win.refresh()

        if self.info_window:
            draw_info_window(self.win, info_data)


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
        self.info_window = False

    def resize_window(self, win):
        self.win = win
        self.height, self.width = self.win.getmaxyx()

    def update(self, char):
        if char == KEY_UP and self.selected_item > 0:
            self.selected_item -= 1

        elif char == KEY_DOWN and self.selected_item < self.max_item:
            self.selected_item += 1

        if self.devices:
            name = self.devices[self.selected_item][0]
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
                self.info_window = not self.info_window
                self.info_window_data = partial(self.device.properties, name)

            elif char in (ord('i'), ):
                self.info_window = not self.info_window
                self.info_window_data = partial(self.device.info, name)

            elif char in (ord('l'), ):
                self.device.change_port_next(name)

            elif char in (ord('k'), ):
                self.device.change_port_previous(name)

            if self.selected_item > self.max_item:
                self.selected_item = self.max_item


    def draw(self):
        self.devices = self.device.get_devices()
        line_number = 0
        if self.info_window:
            info_data = self.info_window_data()

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

        self.win.refresh()

        if self.info_window:
            draw_info_window(self.win, info_data)


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
        self.help = ["Cards"]
        self.conn = pa.dbus_connection()
        self.core = pa.Core(self.conn)
        self.selected_item = 1
        self.max_item = 1
        self.footer = footer

    def resize_window(self, win, footer):
        self.win = win
        self.height, self.width = self.win.getmaxyx()

    def update(self, char):

        if char == KEY_UP and self.selected_item > 1:
            self.selected_item -= 1

        elif char == KEY_DOWN and self.selected_item < self.max_item:
            self.selected_item += 1

        elif char == ord('a'):
            #testing code - Doesn't work
            self.cards[0].active_profile = self.profiles[self.selected_item].profile_name

        if self.selected_item > self.max_item:
            self.selected_item = self.max_item

    def draw(self):
        self.cards = [pa.Card(self.conn, card) for card in self.core.cards]
        self.win.erase()
        self.win.box()
        header_number = 0
        line_number = 0

        for card in self.cards:
            self.profiles = [pa.CardProfile(self.conn, profile) for profile in card.profiles]
            active_profile = card.active_profile
            header_number += 1
            self.win.addstr(header_number, 1, card.name)
            for profile in self.profiles:
                line_number += 1
                name = '%s %s ' % (profile.name, '[A]') if profile.profile_name == card.active_profile else profile.name
                self.win.addstr(header_number+line_number, 4, name)

                if self.selected_item == line_number:
                    self.win.addstr(header_number+line_number, 4, name, curses.color_pair(1))

                else:
                    self.win.addstr(header_number+line_number, 4, name)
                
        self.max_item = line_number

        self.win.refresh()


