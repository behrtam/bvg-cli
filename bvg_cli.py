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

    r = requests.get(BVG_URL, data={'input' : station_name})

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
            data.append((station_name,station_id))
        return data, True

    # one station
    # TODO: clean up direct list access
    station_name = tree.cssselect('span.desc strong')[0].text
    station_id = tree.cssselect('p.links a')[0].get('href').split('&')[1].split('=')[1]
    return (station_name, station_id), True
