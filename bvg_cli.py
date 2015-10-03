import sys
import requests

from lxml import html


BVG_URL = 'http://mobil.bvg.de/Fahrinfo/bin/stboard.bin/dox?'


def get_argument(argument_name, default=''):
    ''' Return value for given argument; default if argument not specified. '''

    argument = default
    argument_name = '--' + argument_name
    if argument_name in sys.argv:
        pos = sys.argv.index(argument_name)
        if len(sys.argv) >= pos + 2:
            argument = sys.argv[pos + 1]
    return argument


def create_products_filter(select='', ignore=''):
    ''' Returns a bit-mask to select or ignore certain types of transport.

    Types can be separated by comma (e.g. 'U,S') or without (e.g. 'US'). If at least one
    type is selected not specified types are ignored, otherwiese not specified types are
    selected. Selected outvotes ingored if a type is in both.

    bit-masks: 11111101 = Regional, 11111011 = Fern, 11101111 = Bus, 11011111 = Tram,
    10111111 = UBahn, 01111111 = SBahn

    ::

        >>> create_products_filter()
        '11111111'
        >>> create_products_filter(select='U,S,R')
        '11000100'
        >>> create_products_filter(ignore='U,S')
        '00111111'
        >>> create_products_filter(select='US', ignore='SBT')
        '11000000'
    '''

    def value(type):
        if type not in select and type in ignore:
            return '0'
        if type in select:
            return '1'
        return '1' if not select else '0'
    return ''.join(value(t) for t in 'SUTBIR__')


def request_station_ids(station_name):
    ''' Requests the station ids for the provided station name.

    The function has two different outcomes dependend on how distinctive
    the station name is. A list of possibel stations or the one station.

    Return a tuple (data, ok). Data holdes the <stations> with their name
    and id. The status flag can be True or False if there are network problems.
    '''

    r = requests.get(BVG_URL, data={'input': station_name})

    # network
    if r.status_code != 200:
        return None, False

    if '--verbose' in sys.argv:
        print('info: response for', r.request.url)

    tree = html.fromstring(r.content)

    data = []

    # possibel stations
    if tree.cssselect('span.error'):
        for station in tree.cssselect('span.select a'):
            station_name = station.text.strip()
            # TODO: clean up direct list access
            station_id = station.get("href").split('&')[1].split('=')[1]
            data.append((station_name, station_id))
        return data, True

    # one station
    # TODO: clean up direct list access
    station_name = tree.cssselect('span.desc strong')[0].text
    station_id = tree.cssselect('p.links a')[0].get('href').split('&')[1].split('=')[1]
    return ((station_name, station_id),), True


def request_departures(station_id, limit, products_filter=''):
    ''' Requests the departure times for the provided station id.

    Return a tuple (data, ok). Data holdes the <departures> with time, line and
    destination. The status flag can be True or False if there are network problems.
    '''

    payload = {'input': station_id, 'maxJourneys': limit, 'start': 'yes'}

    if products_filter:
        payload['productsFilter'] = products_filter

    r = requests.get(BVG_URL, params=payload)

    # network
    if r.status_code != 200:
        return None, False

    if '--verbose' in sys.argv:
        print('info: response for', r.request.url)

    tree = html.fromstring(r.content)

    data = []
    for row in tree.cssselect('tbody tr'):
        cells = tuple(e for e in row.text_content().split('\n') if e)
        data.append(cells)
    return data, True


def show_usage():
    print('usage: bvg_cli.py --station NAME [--limit N]\n\n'
          'A command line tool for the public transport of Berlin.\n\n'
          'arguments:\n'
          '--station NAME       name of your departure station\n\n'
          'optional arguments:\n'
          '--limit N            limit the number of responses (default 10)\n\n'
          '--select types       select types of transport (e.g. U,T)\n'
          '--ignore types       ignore types of transport (e.g. R,I,B)\n'
          '                     types: U - underground (U-Bahn)\n'
          '                            S - suburban railway (S-Bahn)\n'
          '                            T - tram\n'
          '                            B - bus\n'
          '                            R - regional railway\n'
          '                            I - long-distance railway\n\n'
          '--verbose            print info messages (debug)')


if __name__ == '__main__':
    ''' Rudimentary CLI capabilities ...'''

    # TODO: investigate cli packages
    if len(sys.argv) < 3 or sys.argv[1] != '--station':
        show_usage()
        sys.exit(1)

    limit_arg = get_argument('limit', '10')
    select_arg = get_argument('select')
    ignore_arg = get_argument('ignore')

    if '--verbose' in sys.argv:
        print('info: limit_arg', limit_arg, 'select_arg', select_arg,
              'ignore_arg', ignore_arg)

    stations, ok = request_station_ids(sys.argv[2])

    if not ok:
        print('Check your network. BVG website migth also be down.')
        sys.exit(1)

    station_id = 0

    if len(stations) > 1:
        for i, (name, _) in enumerate(stations, start=1):
            print('[{}] {}'.format(i, name))

        while 'do-loop':
            user_response = input('\nWhich station [1-{}] did you mean? '.format(
                len(stations)))
            if user_response.isdigit and 0 < int(user_response) <= len(stations):
                station_id = int(user_response) - 1
                break

    station_name, station_id = stations[station_id]
    products_filter = create_products_filter(select_arg, ignore_arg)
    departures, ok = request_departures(station_id, limit_arg, products_filter)

    if not ok:
        print('Check your network. BVG website migth also be down.')

    print('\n# Next departures at', station_name)
    print('{:8}{:10}{}'.format('Time', 'Line', 'Destination'))
    print('-' * 50)
    for info in departures:
        print('{:8}{:10}{}'.format(*info))
