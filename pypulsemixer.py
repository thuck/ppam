from pulse import pulseaudio as pa

if __name__ == '__main__':
    conn = pa.dbus_connection()
    core = pa.Core(conn)

    cards = [pa.Card(conn, card) for card in core.cards]

    card_profiles = [pa.CardProfile(conn, card_profile) for card in cards
                                    for card_profile in card.profiles]

    sinks = [pa.Device(conn, sink) for sink in core.sinks]

    sources = [pa.Device(conn, source) for source in core.sources]

    sink_ports = [pa.DevicePort(conn, sink_port) for sink in sinks 
                                        for sink_port in sink.ports]

    source_ports = [pa.DevicePort(conn, source_port) for source in sources
                                        for source_port in source.ports]

    streams = [pa.Stream(conn, stream) for stream in core.playback_streams]

    samples = [pa.Sample(conn, sample) for sample in core.samples]

    modules = [pa.Module(conn, module) for module in core.modules]

    clients = [pa.Client(conn, client) for client in core.clients]

#    for i in sinks[0].property_list.keys():
#        print str(i)+': '+str(''.join(str(byte) for byte in sinks[0].property_list[i]))
#    print sources[0].name[:-1]
#    print [sink_port for sink in sinks for sink_port in sink.ports]
    for i in modules:
        print i.name

#    print '---------------------------------------------'
#    print [int(x) for x in  streams[0].volume]
#
#    for i in [x.name for x in card_profiles]:
#        print i
#
#    print '---------------------------------------------------'
#
#    for i in [x.name for x in sink_ports]:
#        print i
#
#    print '---------------------------------------------------'
#
#    for i in [x.name for x in source_ports]:
#        print i
#
#    print '---------------------------------------------------'
#    for i in [Device(conn, sink) for sink in core.sinks]:
#        print ''.join(str(byte) for byte in i.property_list['device.profile.name'])[:-1]
#        print i.active_port
