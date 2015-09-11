import sys
import requests

from lxml import html


BVG_URL = 'http://mobil.bvg.de/Fahrinfo/bin/stboard.bin/dox?'


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
    return (station_name, station_id), True


def request_departures(station_id, limit):
    print(limit)
    ''' Requests the departure times for the provided station id.

    Return a tuple (data, ok). Data holdes the <departures> with time, line and
    destination. The status flag can be True or False if there are network problems.
    '''
    payload = {'input': station_id, 'maxJourneys': limit, 'start': 'yes'}
    r = requests.get(BVG_URL, params=payload)

    # network
    if r.status_code != 200:
        return None, False

    tree = html.fromstring(r.content)

    data = []
    for row in tree.cssselect('tbody tr'):
        cells = tuple(e for e in row.text_content().split('\n') if e)
        data.append(cells)
    return data, True


def show_usage():
    print('bvg_cli.py --station NAME [--limit N]')


if __name__ == '__main__':
    ''' Rudimentary CLI capabilities ...'''

    if len(sys.argv) < 3 or sys.argv[1] != '--station':
        show_usage()
        sys.exit(1)

    limit = '10'

    if len(sys.argv) >= 5 and sys.argv[3] == '--limit':
        limit = sys.argv[4]

    stations, ok = request_station_ids(sys.argv[2])

    if not ok:
        print('Check your network. BVG website migth also be down.')
        sys.exit(1)

    station_id = 0

    if len(stations) > 1:
        for i, (name, _) in enumerate(stations, start=1):
            print('[{}] {}'.format(i, name))

        while 'do-loop':
            user_response = input('Which station [1-{}] did you mean? '.format(
                len(stations)))
            if user_response.isdigit and 0 < int(user_response) <= len(stations):
                station_id = int(user_response) - 1
                break

    station_name, station_id = stations[station_id]
    departures, ok = request_departures(station_id, limit)

    if not ok:
        print('Check your network. BVG website migth also be down.')

    print('\n# Next departures at', station_name)
    print('{:8}{:10}{}'.format('Time', 'Line', 'Destination'))
    print('-' * 50)
    for info in departures:
        print('{:8}{:10}{}'.format(*info))
