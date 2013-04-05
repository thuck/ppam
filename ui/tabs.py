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
from itertools import cycle
import curses
from curses import KEY_UP, KEY_DOWN
import dbus

class TabPlaybackStream(object):
    def __init__(self, win, footer, conf):
        self.win = win
        self.height, self.width = self.win.getmaxyx()
        self.name = 'Playback'
        self.conf = conf
        self.help = ["+/- to Increase and decrease volume",
                     ",/. to Increase and decrease right volume",
                     "</> to Increase and decrease left volume",
                     "m to Mute"]
        self.conn = pa.dbus_connection()
        self.core = pa.Core(self.conn)
        self.selected_item = 0
        self.max_item = 0

    def update(self, char):
        if char == KEY_UP and self.selected_item > 0:
            self.selected_item -= 1

        elif char == KEY_DOWN and self.selected_item < self.max_item:
            self.selected_item += 1

        elif char in (ord('+'), ord('-')):
            current_volume = self.streams[self.selected_item].volume

            if char == ord('+'):
                new_left = current_volume[0] + 65536/100
                new_right = current_volume[1] + 65536/100
                if new_left > 98304:
                    new_left = 98304

                if new_right > 98304:
                    new_right = 98304

            else:
                new_left = current_volume[0] - 65536/100
                new_right = current_volume[1] - 65536/100

                if new_left < 0:
                    new_left = 0

                if new_right < 0:
                    new_right = 0


            self.streams[self.selected_item].volume = [dbus.UInt32(new_left), dbus.UInt32(new_right)]

        elif char in (ord('m'),):
            self.streams[self.selected_item].mute = not self.streams[self.selected_item].mute

        elif char in (ord('>'), ord('.')):
            current_volume = self.streams[self.selected_item].volume
            new_left = current_volume[0]
            new_right = current_volume[1]

            if char == ord('>'):
                new_left += 65536/100

            else:
                new_right += 65536/100

            if new_left > 98304:
                new_left = 98304

            if new_right > 98304:
                new_right = 98304

            self.streams[self.selected_item].volume = [dbus.UInt32(new_left), dbus.UInt32(new_right)]

        elif char in (ord('<'), ord(',')):
            current_volume = self.streams[self.selected_item].volume
            new_left = current_volume[0]
            new_right = current_volume[1]

            if char == ord('<'):
                new_left -= 65536/100

            else:
                new_right -= 65536/100

            if new_left < 0:
                new_left = 0

            if new_right < 0:
                new_right = 0

            self.streams[self.selected_item].volume = [dbus.UInt32(new_left), dbus.UInt32(new_right)]

        if self.selected_item > self.max_item:
            self.selected_item = self.max_item


    def draw(self):
        self.streams = [pa.Stream(self.conn, stream) for stream in self.core.playback_streams]
        self.win.erase()
        self.win.box()
        line_number = 0

        for line_number, stream in enumerate(self.streams):
            app_name = ''.join(str(byte) for byte in stream.property_list['application.name'])[:-1]
            app_pid = ''.join(str(byte) for byte in stream.property_list['application.process.id'])[:-1]
            volume_left = int(stream.volume[0]*100/65536)
            volume_right = int(stream.volume[1]*100/65536)
            line = '[%s] L:%s%% R:%s%% (%s)' % (app_name, volume_left, volume_right, app_pid)

            if stream.mute:
                line = '%s [M]' % (line)

            if self.selected_item == line_number:
                self.win.addstr(line_number + 1, 1, line, curses.color_pair(1))
        
            else:
                self.win.addstr(line_number + 1, 1, line)

        self.max_item = line_number

        self.win.refresh()
    
class TabOutputDevices(object):
    def __init__(self, win, footer, conf):
        self.win = win
        self.height, self.width = self.win.getmaxyx()
        self.name = 'Output Devices'
        self.conf = conf
        self.help = ["Output Devices"]
        self.conn = pa.dbus_connection()
        self.core = pa.Core(self.conn)
        self.selected_item = 0
        self.max_item = 0
        self.footer = footer

    def update(self, char):

        if char == ord('i'):
            self.draw_info()
#            return

        if char == KEY_UP and self.selected_item > 0:
            self.selected_item -= 1

        elif char == KEY_DOWN and self.selected_item < self.max_item:
            self.selected_item += 1

        elif char in (ord('+'), ord('-')):
            current_volume = self.devices[self.selected_item].volume

            if char == ord('+'):
                new_left = current_volume[0] + 65536/100
                new_right = current_volume[1] + 65536/100
                if new_left > 98304:
                    new_left = 98304

                if new_right > 98304:
                    new_right = 98304

            else:
                new_left = current_volume[0] - 65536/100
                new_right = current_volume[1] - 65536/100

                if new_left < 0:
                    new_left = 0

                if new_right < 0:
                    new_right = 0


            self.devices[self.selected_item].volume = [dbus.UInt32(new_left), dbus.UInt32(new_right)]

        elif char in (ord('m'),):
            self.devices[self.selected_item].mute = not self.devices[self.selected_item].mute

        elif char in (ord('>'), ord('.')):
            current_volume = self.devices[self.selected_item].volume
            new_left = current_volume[0]
            new_right = current_volume[1]

            if char == ord('>'):
                new_left += 65536/100

            else:
                new_right += 65536/100

            if new_left > 98304:
                new_left = 98304

            if new_right > 98304:
                new_right = 98304

            self.devices[self.selected_item].volume = [dbus.UInt32(new_left), dbus.UInt32(new_right)]

        elif char in (ord('<'), ord(',')):
            current_volume = self.devices[self.selected_item].volume
            new_left = current_volume[0]
            new_right = current_volume[1]

            if char == ord('<'):
                new_left -= 65536/100

            else:
                new_right -= 65536/100

            if new_left < 0:
                new_left = 0

            if new_right < 0:
                new_right = 0

            self.devices[self.selected_item].volume = [dbus.UInt32(new_left), dbus.UInt32(new_right)]

        if self.selected_item > self.max_item:
            self.selected_item = self.max_item

    def draw_info(self):
        self.win.box()
        #This will create a centralize window
        box = self.win.derwin(self.height/2, self.width/2, self.height/4, self.width/4)
        hb_height, hb_width = box.getmaxyx()
        box.erase()
        box.hline(hb_height - 3, 1, curses.ACS_HLINE, hb_width - 2)
        message = "Press any key to continue"
        box.addstr(hb_height - 2, hb_width/2 - len(message)/2, message )
        box.box()

        device = self.devices[self.selected_item]

        box.addstr(1, 1, "Index: %s" % (device.index))
        box.addstr(2, 1, "Name: %s" % (device.name))
        box.addstr(3, 1, "OwnerModule: %s" % (device.owner_module))
        box.addstr(4, 1, "Card: %s" % (device.card))
        box.addstr(5, 1, "SampleFormat: %s" % (device.sample_format))
        box.addstr(6, 1, "Channels: %s" % (','.join([str(x) for x in device.channels])))
        box.addstr(7, 1, "BaseVolume: %s" % (device.base_volume))
        box.addstr(8, 1, "VolumeSteps: %s" % (device.volume_steps))
        box.addstr(9, 1, "ConfiguredLatency: %s" % (device.configured_latency))
        box.addstr(10, 1, "Latency: %s" % (device.latency))
        box.addstr(11, 1, "State: %s" % (device.state))
        box.addstr(12, 1, "Ports: %s" % (','.join([str(x) for x in device.ports])))

        self.win.refresh()

        box.timeout(500)
        while True:

            c = box.getch()

            if c == curses.KEY_RESIZE:
                error = ERROR(self.win, self.footer)
                error.draw("I cannot handle resize...")

                sys.exit(1)
            elif  c != -1:
                break


    def draw(self):
        self.devices = [pa.Device(self.conn, device) for device in self.core.sinks]
        self.win.erase()
        self.win.box()
        line_number = 0

        for line_number, device in enumerate(self.devices):
            app_name = ''.join(str(byte) for byte in device.property_list['device.profile.name'])[:-1]
            volume_left = int(device.volume[0]*100/65536)
            volume_right = int(device.volume[1]*100/65536)
            line = '[%s] L:%s%% R:%s%%' % (app_name, volume_left, volume_right)

            if device.mute:
                line = '%s [M]' % (line)

            if self.selected_item == line_number:
                self.win.addstr(line_number + 1, 1, line, curses.color_pair(1))

            else:
                self.win.addstr(line_number + 1, 1, line)

        self.max_item = line_number

        self.win.refresh()
