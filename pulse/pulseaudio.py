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
import dbus
import functools as ft

def dbus_connection():
    addr = dbus.SessionBus().get_object('org.PulseAudio1',
                                        '/org/pulseaudio/server_lookup1').Get(
                                              'org.PulseAudio.ServerLookup1',
                                              'Address',
                                              dbus_interface='org.freedesktop.DBus.Properties')

    conn = dbus.connection.Connection(addr)

    return conn

class Core(object):
    path = 'org.PulseAudio.Core1'
    props = ['Sinks', 'PlaybackStreams', 'InterfaceRevision', 'Name',
             'Version', 'IsLocal', 'Username', 'Hostname', 'DefaultChannels',
             'DefaultSampleFormat', 'DefaultSampleRate', 'Cards', 'Sources',
             'FallbackSource', 'RecordStreams', 'Samples', 'Modules',
             'Clients', 'MyClient', 'Extensions']

    signals = ['NewCard', 'CardRemoved', 'NewSink', 'SinkRemoved',
               'FallbackSinkUpdated', 'FallbackSinkUnset', 'NewSource',
               'SourceRemoved', 'FallbackSourceUpdated', 'FallbackSourceUnset',
               'NewPlaybackStream', 'PlaybackStreamRemoved', 'NewRecordStream',
               'RecordStreamRemoved', 'NewSample','SampleRemoved',
               'NewModule', 'ModuleRemoved', 'NewClient', 'ClientRemoved',
               'NewExtension', 'ExtensionRemoved'] 

    def __init__(self, conn):
        self.conn = conn
        self.core = conn.get_object(object_path='/org/pulseaudio/core1')
        self.get = ft.partial(self.core.Get, self.path)
        self.setter = ft.partial(self.core.Set, self.path)

    @property
    def sinks(self):
        return self.get('Sinks')

    @property
    def playback_streams(self):
        return self.get('PlaybackStreams')

    @property
    def interface_revision(self):
        return self.get('InterfaceRevision')

    @property
    def name(self):
        return self.get('Name')

    @property
    def version(self):
        return self.get('Version')

    @property
    def is_local(self):
        return self.get('IsLocal')

    @property
    def username(self):
        return self.get('Username')

    @property
    def hostname(self):
        return self.get('Hostname')

    @property
    def default_channels(self):
        return self.get('DefaultChannels')

    @property
    def default_sample_format(self):
        return self.get('DefaultSampleFormat')

    @property
    def default_sample_rate(self):
        return self.get('DefaultSampleRate')

    @property
    def cards(self):
        return self.get('Cards')

    @property
    def sources(self):
        return self.get('Sources')

    @property
    def fallback_source(self):
        return self.get('FallbackSource')

    @property
    def record_streams(self):
        return self.get('RecordStreams')

    @property
    def samples(self):
        return self.get('Samples')

    @property
    def modules(self):
        return self.get('Modules')

    @property
    def clients(self):
        return self.get('Clients')

    @property
    def my_client(self):
        return self.get('MyClient')

    @property
    def extensions(self):
        return self.get('Extensions')

    def get_card_by_name(self, name):
        return self.core.GetCardByName(name)

    def get_sink_by_name(self, name):
        return self.core.GetSinkByName(name)

    def get_source_by_name(self, name):
        return self.core.GetSourceByName(name)

    def get_sample_by_name(self, name):
        return self.core.GetSampleByName(name)

    def upload_sample(self, *args):
        return self.core.UploadSample(*args)

    def load_module(*args):
        return self.core.LoadModule(*args)

    def exit(self):
        return self.core.Exit()

    def listen_for_signal(self, *args):
        self.core.ListenForSignal(*args)

    def stop_listening_for_signal(self, signal):
        self.core.StopListeningForSignal(signal)

class MemoryStatistics(object):
    path = 'org.PulseAudio.Core1.Memstats'

    def __init__(self, conn):
        self.conn = conn
        self.bus = conn.get_object(object_path='/org/pulseaudio/core1/memstats')
        self.get = ft.partial(self.bus.Get, self.path)

    @property
    def current_memblocks(self):
        return self.get('CurrentMemblocks')

    @property
    def current_memblocks_size(self):
        return self.get('CurrentMemblocksSize')

    @property
    def accumulated_memblocks(self):
        return self.get('AccumulatedMemblocks')

    @property
    def accumulated_memblocks_size(self):
        return self.get('AccumulatedMemblocksSize')

    @property
    def sample_cache_size(self):
        return self.get('SampleCacheSize')
 
class Card(object):
    path = 'org.PulseAudio.Core1.Card'
    
    signals = ['ActiveProfileUpdated', 'NewProfile',
               'ProfileRemoved', 'PropertyListUpdated']

    def __init__(self, conn, card):
        self.conn = conn
        self.bus = conn.get_object(object_path=card)
        self.get = ft.partial(self.bus.Get, self.path)

    @property
    def index(self):
        return self.get('Index')

    @property
    def name(self):
        return self.get('Name')

    @property
    def driver(self):
        return self.get('Driver')

    @property
    def owner_module(self):
        return self.get('OwnerModule')

    @property
    def sinks(self):
        return self.get('Sinks')

    @property
    def sources(self):
        return self.get('Sources')

    @property
    def profiles(self):
        return self.get('Profiles')

    @property
    def active_profile(self):
        return self.get('ActiveProfile')

    @property
    def property_list(self):
        return self.get('PropertyList')

    def get_profile_by_name(self, name):
        return self.bus.GetProfileByName(name)

class CardProfile(object):
    path = 'org.PulseAudio.Core1.CardProfile'

    def __init__(self, conn, profile):
        self.conn = conn
        self.bus = conn.get_object(object_path=profile)
        self.get = ft.partial(self.bus.Get, self.path) 

    @property
    def index(self):
        return self.get('Index')

    @property
    def name(self):
        return self.get('Name')

    @property
    def description(self):
        return self.get('Description')

    @property
    def sinks(self):
        return self.get('Sinks')

    @property
    def sources(self):
        return self.get('Sources')

    @property
    def priority(self):
        return self.get('Priority')


class Device(object):
    path = 'org.PulseAudio.Core1.Device'

    signals = ['VolumeUpdated', 'MuteUpdated', 'StateUpdated',
               'ActivePortUpdated', 'PropertyListUpdated']

    def __init__(self, conn, device):
        self.conn = conn
        self.bus = conn.get_object(object_path=device)
        self.get = ft.partial(self.bus.Get, self.path)

    @property
    def index(self):
        return self.get('Index')

    @property
    def name(self):
        return self.get('Name')

    @property
    def driver(self):
        return self.get('Driver')

    @property
    def owner_module(self):
        return self.get('OwnerModule')

    @property
    def card(self):
        return self.get('Card')

    @property
    def sample_format(self):
        return self.get('SampleFormat')

    @property
    def sample_rate(self):
        return self.get('SampleRate')

    @property
    def channels(self):
        return self.get('Channels')

    @property
    def volume(self):
        return self.get('Volume')

    @volume.setter
    def volume(self, volume):
        self.bus.Set(self.path, 'Volume', volume, dbus_interface='org.freedesktop.DBus.Properties')

    @property
    def has_flat_volume(self):
        return self.get('HasFlatVolume')

    @property
    def has_convertible_to_decibel_volume(self):
        return self.get('HasConvertibleToDecibelVolume')

    @property
    def base_volume(self):
        return self.get('BaseVolume')

    @property
    def volume_steps(self):
        return self.get('VolumeSteps')

    @property
    def mute(self):
        return self.get('Mute')

    @mute.setter
    def mute(self, mute):
        self.bus.Set(self.path, 'Mute', mute, dbus_interface='org.freedesktop.DBus.Properties')

    @property
    def has_hardware_volume(self):
        return self.get('HasHardwareVolume')

    @property
    def hasHardware_mute(self):
        return self.get('HasHardwareMute')

    @property
    def configured_latency(self):
        return self.get('ConfiguredLatency')

    @property
    def has_dynamic_latency(self):
        return self.get('HasDynamicLatency')

    @property
    def latency(self):
        return self.get('Latency')

    @property
    def is_hardware_device(self):
        return self.get('IsHardwareDevice')

    @property
    def is_network_device(self):
        return self.get('IsNetworkDevice')

    @property
    def state(self):
        return self.get('State')

    @property
    def ports(self):
        return self.get('Ports')

    @property
    def active_port(self):
        return self.get('ActivePort')

    @property
    def property_list(self):
        return self.get('PropertyList')

    def suspend(self, suspend):
        self.bus.Suspend(suspend)

    def get_port_by_name(self, name):
        return self.bus.GetPortByName(name)


class Sink(Device):
    path = 'org.PulseAudio.Core1.Sink'

    @property
    def monitor_source(self):
        return self.get('MonitorSource')


class Source(Device):
    path = 'org.PulseAudio.Core1.Source'

    @property
    def monitor_of_sink(self):
        return self.get('MonitorOfSink')


class DevicePort(object):
    path = 'org.PulseAudio.Core1.DevicePort'

    def __init__(self, conn, port):
        self.conn = conn
        self.bus = conn.get_object(object_path=port)
        self.get = ft.partial(self.bus.Get, self.path)

    @property
    def index(self):
        return self.get('Index')

    @property
    def name(self):
        return self.get('Name')

    @property
    def description(self):
        return self.get('Description')

    @property
    def priority(self):
        return self.get('Priority')


class Stream(object):
    path = 'org.PulseAudio.Core1.Stream'

    signals = ['DeviceUpdated', 'SampleRateUpdated', 'VolumeUpdated',
               'MuteUpdated', 'PropertyListUpdated', 'StreamEvent']

    def __init__(self, conn, stream):
        self.conn = conn
        self.bus = conn.get_object(object_path=stream)
        self.get = ft.partial(self.bus.Get, self.path)

    @property
    def index(self):
        return self.get('Index')

    @property
    def driver(self):
        return self.get('Driver')

    @property
    def owner_module(self):
        return self.get('OwnerModule')

    @property
    def client(self):
        return self.get('Client')

    @property
    def device(self):
        return self.get('Device')

    @property
    def sample_format(self):
        return self.get('SampleFormat')

    @property
    def sample_rate(self):
        return self.get('SampleRate')

    @property
    def channels(self):
        return self.get('Channels')

    @property
    def volume(self):
        return self.get('Volume')

    @volume.setter
    def volume(self, volume):
        self.bus.Set(self.path, 'Volume', volume, dbus_interface='org.freedesktop.DBus.Properties')

    @property
    def volume_writable(self):
        return self.get('VolumeWritable')

    @property
    def mute(self):
        return self.get('Mute')

    @mute.setter
    def mute(self, mute):
        self.bus.Set(self.path, 'Mute', mute, dbus_interface='org.freedesktop.DBus.Properties')

    @property
    def buffer_latency(self):
        return self.get('BufferLatency')

    @property
    def device_latency(self):
        return self.get('DeviceLatency')

    @property
    def resample_method(self):
        return self.get('ResampleMethod')

    @property
    def property_list(self):
        return self.get('PropertyList')

    def move(self, device):
        self.bus.Move(device)

    def kill(self):
        self.bus.Kill()


class Sample(object):
    path = 'org.PulseAudio.Core1.Sample'

    signals = ['PropertyListUpdated']

    def __init__(self, conn, sample):
        self.conn = conn
        self.bus = conn.get_object(object_path=sample)
        self.get = ft.partial(self.bus.Get, self.path)

    @property
    def Index(self):
        return self.get('Index')

    @property
    def Name(self):
        return self.get('Name')

    @property
    def SampleFormat(self):
        return self.get('SampleFormat')

    @property
    def SampleRate(self):
        return self.get('SampleRate')

    @property
    def Channels(self):
        return self.get('Channels')

    @property
    def DefaultVolume(self):
        return self.get('DefaultVolume')

    @property
    def Duration(self):
        return self.get('Duration')

    @property
    def Bytes(self):
        return self.get('Bytes')

    @property
    def PropertyList(self):
        return self.get('PropertyList')

    def play(self, volume, property_list):
        self.bus.Play(volume, property_list)

    def play_to_sink(self, sink, volume, property_list):
        self.bus.PlayToSink(sink, volume, property_list)

    def remove(self):
        self.bus.Remove()


class Module(object):
    path = 'org.PulseAudio.Core1.Module'

    signals = ['PropertyListUpdated']

    def __init__(self, conn, module):
        self.conn = conn
        self.bus = conn.get_object(object_path=module)
        self.get = ft.partial(self.bus.Get, self.path)

    @property
    def Index(self):
        return self.get('Index')

    @property
    def Name(self):
        return self.get('Name')

    @property
    def Arguments(self):
        return self.get('Arguments')

    @property
    def UsageCounter(self):
        return self.get('UsageCounter')

    @property
    def PropertyList(self):
        return self.get('PropertyList')

    def unload(self):
        self.bus.Unload()


class Client(object):
    path = 'org.PulseAudio.Core1.Client'

    signals = ['PropertyListUpdated', 'ClientEvent']

    def __init__(self, conn, module):
        self.conn = conn
        self.bus = conn.get_object(object_path=module)
        self.get = ft.partial(self.bus.Get, self.path)

    @property
    def index(self):
        return self.get('Index')

    @property
    def driver(self):
        return self.get('Driver')

    @property
    def owner_module(self):
        return self.get('OwnerModule')

    @property
    def playback_streams(self):
        return self.get('PlaybackStreams')

    @property
    def record_streams(self):
        return self.get('RecordStreams')

    @property
    def property_list(self):
        return self.get('PropertyList')

    def kill(self):
        self.bus.Kill()

    def update_properties(self):
        self.bus.UpdateProperties()

    def remove_properties(self):
        self.bus.RemoveProperties()


if __name__ == '__main__':
    #this will be used for the tests
    conn = dbus_connection()
    core = Core(conn)
    print core.sinks, core.interface_revision

