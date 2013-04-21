#!/usr/bin/python
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
import pulse.pulseaudio as pa
import dbus
from itertools import cycle


class Stream(object):

    def __init__(self, stream_type):
        self.conn = pa.dbus_connection()
        self.core = pa.Core(self.conn)
        self.stream_type = stream_type

    def playing(self):
        self.streams = [pa.Stream(self.conn, stream)
                    for stream in getattr(self.core, self.stream_type)]

        return [(''.join(str(byte) for byte in stream.property_list['application.name'])[:-1],
            ''.join(str(byte) for byte in stream.property_list['application.process.id'])[:-1],
            round(stream.volume[0]*100.0/65536.0),
            round(stream.volume[1]*100.0/65536.0),
            stream.mute) for stream in self.streams]

    def _get_app_stream(self, pid):
        for stream in self.streams:
            app_pid = ''.join(str(byte) for byte in stream.property_list['application.process.id'])[:-1]
            if app_pid == pid:
                return stream

        return None

    def _set_volume(self, stream, volume):
        stream.volume = [dbus.UInt32(volume[0]), dbus.UInt32(volume[1])]

    def increase_volume(self, pid):
        stream = self._get_app_stream(pid)
        rate = 65536.0/100.0
        if stream:
            volume = stream.volume
            left = volume[0] + rate if volume[0] + rate < 98304 else 98304
            right = volume[1] + rate if volume[1] + rate < 98304 else 98304
            self._set_volume(stream, [left, right])

    def increase_left_volume(self, pid):
        stream = self._get_app_stream(pid)
        rate = 65536.0/100.0
        if stream:
            volume = stream.volume
            left = volume[0] + rate if volume[0] + rate < 98304 else 98304
            right = volume[1]
            self._set_volume(stream, [left, right])

    def increase_right_volume(self, pid):
        stream = self._get_app_stream(pid)
        rate = 65536.0/100.0
        if stream:
            volume = stream.volume
            left = volume[0]
            right = volume[1] + rate if volume[1] + rate < 98304 else 98304
            self._set_volume(stream, [left, right])

    def decrease_volume(self, pid):
        stream = self._get_app_stream(pid)
        rate = 65536.0/100.0
        if stream:
            volume = stream.volume
            left = volume[0] - rate if volume[0] - rate > 0 else 0
            right = volume[1] - rate if volume[1] - rate > 0 else 0
            self._set_volume(stream, [left, right])

    def decrease_left_volume(self, pid):
        stream = self._get_app_stream(pid)
        rate = 65536.0/100.0
        if stream:
            volume = stream.volume
            left = volume[0] - rate if volume[0] - rate > 0 else 0
            right = volume[1]
            self._set_volume(stream, [left, right])

    def decrease_right_volume(self, pid):
        stream = self._get_app_stream(pid)
        rate = 65536.0/100.0
        if stream:
            volume = stream.volume
            left = volume[0]
            right = volume[1] - rate if volume[1] - rate > 0 else 0
            self._set_volume(stream, [left, right])

    def mute(self, pid):
        stream = self._get_app_stream(pid)
        stream.mute = not stream.mute

    def properties(self, pid):
        stream = self._get_app_stream(pid)

        return sorted(['%s: %s' % (key, ''.join(str(byte) for byte in value)[:-1])
                for key, value in stream.property_list.items()])

    def info(self, pid):
        stream = self._get_app_stream(pid)
        return ('Index: %s' % stream.index,
                'Driver: %s' % stream.driver,
                'Owner Module: %s' % stream.owner_module,
                'Client: %s' % stream.client,
                'Device: %s' % stream.device,
                'Sample Format: %s' % stream.sample_format,
                'Sample Rate: %s' % stream.sample_rate,
                'Channels: %s' % ','.join(str(channel) for channel in stream.channels),
                'Volume Writable: %s' % stream.volume_writable,
                'Buffer Latency: %s' % stream.buffer_latency,
                'Device Latency: %s' % stream.device_latency,
                'Resample Method: %s' % stream.resample_method)


class Playback(Stream):
    def __init__(self):
        Stream.__init__(self, 'playback_streams')


class Record(Stream):
    def __init__(self):
        Stream.__init__(self, 'record_streams')


class Device(object):

    def __init__(self, device_type):
        self.conn = pa.dbus_connection()
        self.core = pa.Core(self.conn)
        self.device_type = device_type
        self.devices = []
        self.ports = {}

    def change_port_next(self, name):
        device = self._get_device(name)
        cports = cycle(self.ports[device.name])
        if self.ports[device.name]:
            while device.active_port != cports.next().port_name:
                pass

            device.active_port = cports.next().port_name

    def change_port_previous(self, name):
        device = self._get_device(name)
        cports = cycle(self.ports[device.name][::-1])
        if self.ports[device.name]:
            while device.active_port != cports.next().port_name:
                pass

            device.active_port = cports.next().port_name

    def get_devices(self):
        name = 'Unknown'
        if self.device_type == 'sink':
            self.devices = [pa.Device(self.conn, device)
                    for device in self.core.sinks]

        elif self.device_type == 'source':
            self.devices = [pa.Device(self.conn, device)
                    for device in self.core.sources]

        info = []  # this is terrible variable name
        for device in self.devices:
            name = device.name
            ports = [pa.DevicePort(self.conn, port) for port in device.ports]
            self.ports[name] = ports

            tmp_port = []
            for port in ports:
                if port.port_name == device.active_port:
                    tmp_port.append((True, port.name))

                else:
                    tmp_port.append((False, port.name))

            if len(device.volume) > 1:
                pack = (name, round(device.volume[0]*100.0/65536.0),
                        round(device.volume[1]*100.0/65536.0),
                        device.mute, tmp_port)

            else:
                pack = (name, round(device.volume[0]*100.0/65536.0),
                        device.mute, tmp_port)

            info.append(pack)

        return info

    def _get_device(self, name):
        for device in self.devices:
            if device.name == name:
                return device

        return None

    def _set_volume(self, device, volume):
        if len(volume) == 2:
            device.volume = [dbus.UInt32(volume[0]), dbus.UInt32(volume[1])]

        else:
            device.volume = [dbus.UInt32(volume[0])]

    def increase_volume(self, name):
        device = self._get_device(name)
        rate = 65536.0/100.0
        if device:
            volume = device.volume
            left = volume[0] + rate if volume[0] + rate < 98304 else 98304
            if len(device.volume) > 1:
                right = volume[1] + rate if volume[1] + rate < 98304 else 98304
                self._set_volume(device, [left, right])

            else:
                self._set_volume(device, [left])

    def increase_left_volume(self, name):
        device = self._get_device(name)
        rate = 65536.0/100.0
        if stream and len(device.volume) > 1:
            volume = device.volume
            left = volume[0] + rate if volume[0] + rate < 98304 else 98304
            right = volume[1]
            self._set_volume(device, [left, right])

    def increase_right_volume(self, name):
        device = self._get_device(name)
        rate = 65536.0/100.0
        if device and len(device.volume) > 1:
            volume = device.volume
            left = volume[0]
            right = volume[1] + rate if volume[1] + rate < 98304 else 98304
            self._set_volume(device, [left, right])

    def decrease_volume(self, name):
        device = self._get_device(name)
        rate = 65536.0/100.0
        if device:
            volume = device.volume
            left = volume[0] - rate if volume[0] - rate > 0 else 0
            if len(device.volume) > 1:
                right = volume[1] - rate if volume[1] - rate > 0 else 0
                self._set_volume(device, [left, right])

            else:
                self._set_volume(device, [left])

    def decrease_left_volume(self, name):
        device = self._get_device(name)
        rate = 65536.0/100.0
        if device and len(device.volume) > 1:
            volume = device.volume
            left = volume[0] - rate if volume[0] - rate > 0 else 0
            right = volume[1]
            self._set_volume(device, [left, right])

    def decrease_right_volume(self, name):
        device = self._get_device(name)
        rate = 65536.0/100.0
        if device and len(device.volume) > 1:
            volume = device.volume
            left = volume[0]
            right = volume[1] - rate if volume[1] - rate > 0 else 0
            self._set_volume(device, [left, right])

    def mute(self, name):
        device = self._get_device(name)
        device.mute = not device.mute

    def properties(self, name):
        device = self._get_device(name)

        return sorted(['%s: %s' % (key, ''.join(str(byte) for byte in value)[:-1])
                for key, value in device.property_list.items()])

    def info(self, name):
        device = self._get_device(name)
        return ('Index: %s' % device.index,
                'Name: %s' % device.name,
                'Driver: %s' % device.driver,
                'Owner Module: %s' % device.owner_module,
                'Card: %s' % device.card,
                'Sample Format: %s' % device.sample_format,
                'Sample Rate: %s' % device.sample_rate,
                'Channels: %s' % ','.join(str(channel) for channel in device.channels),
#                'Has Flat Volume: %s' % device.has_flat_volume,
#                'Has Convertible To Decibel Volume: %s' % device.has_convertible_to_decibel_volume,
                'Base Volume: %s' % device.base_volume,
                'Volume Steps: %s' % device.volume_steps,
#                'Has Hardware Volume: %s' % device.has_hardware_volume,
#                'Has Hardware Mute: %s' % device.has_hardware_mute,
                'Configured Latency: %s' % device.configured_latency,
#                'Has Dynamic Latency: %s' % device.has_dynamic_latency,
                'Latency: %s' % device.latency,
#                'Is Hardware Device: %s' % device.is_hardware_device,
#                'Is Network Device: %s' % device.is_network_device,
                'State: %s' % device.state)


class OutputDevices(Device):
    def __init__(self):
        Device.__init__(self, 'sink')


class InputDevices(Device):
    def __init__(self):
        Device.__init__(self, 'source')


class Cards(object):
    def __init__(self):
        self.conn = pa.dbus_connection()
        self.core = pa.Core(self.conn)
        self.cards = []
        self.dbus_cards = []
        self.profiles = {}
        self.info_data = None

    def _get_card(self, card_name):
        for card in self.cards:
            if card.name == card_name:
                return card

        return None

    def _get_profile(self, card_name, profile_name):
        for profile in self.profiles[card_name]:
            if profile.name == profile_name:
                return profile

        return None

    def _get_cards(self):
        info = []
        self.cards = [pa.Card(self.conn, card) for card in self.core.cards]
        for card in self.cards:
            profiles = [pa.CardProfile(self.conn, profile)
                                              for profile in card.profiles]
            self.profiles[card.name] = profiles

            for profile in profiles:
                active = True if profile.profile_name == card.active_profile else False
                info.append((card.name, profile.name, active))

        return info

    def get_cards(self):
        current_cards = [card for card in self.core.cards]

        if not self.dbus_cards == current_cards:
            self.dbus_cards = current_cards
            self.info_data = self._get_cards()

        return self.info_data

    def info(self, info):
        card = self._get_card(info[0])
        profile = self._get_profile(info[0], info[1])
        return ('Card Info',
                'Index: %s' % (card.index),
                'Driver: %s' % (card.driver),
                'Sinks: %s' % (','.join(sink for sink in card.sinks)),
                '',
                'Profile Info',
                'Index: %s' % (profile.index),
                'Description: %s' % (profile.description),
                'Sinks: %s' % (profile.sinks),
                'Priority: %s' % (profile.priority))

    def properties(self, info):
        card = self._get_card(info[0])
        profile = self._get_profile(info[0], info[1])

        return sorted(['%s: %s' % (key, ''.join(str(byte) for byte in value)[:-1])
                for key, value in card.property_list.items()])
