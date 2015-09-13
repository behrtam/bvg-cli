import httpretty

from bvg_cli import BVG_URL
from bvg_cli import request_departures, request_station_ids

from html_dumps import DEPARTURE_HTML, STATION_HTML


@httpretty.activate
def test_request_station_server_error():
    httpretty.register_uri(httpretty.GET, BVG_URL, status=500)
    _, ok = request_station_ids('any station')
    assert ok is False


@httpretty.activate
def test_request_departures_server_error():
    httpretty.register_uri(httpretty.GET, BVG_URL, status=500)
    _, ok = request_departures('any id', limit=10)
    assert ok is False


@httpretty.activate
def test_parameter_station_name():
    httpretty.register_uri(httpretty.GET, BVG_URL, status=201)
    _, ok = request_station_ids('anystation')
    request = httpretty.last_request()
    assert b'input=anystation' in request.body


@httpretty.activate
def test_station_name():
    httpretty.register_uri(httpretty.GET, BVG_URL, body=STATION_HTML)
    stations, ok = request_station_ids('Weber')
    assert ok is True
    assert len(stations) == 8
    assert len(stations[0]) == 2


@httpretty.activate
def test_parameter_limit():
    httpretty.register_uri(httpretty.GET, BVG_URL, body=DEPARTURE_HTML)
    _, ok = request_departures('any id', limit=2)
    request = httpretty.last_request()
    assert hasattr(request, 'querystring')
    assert 'maxJourneys' in request.querystring
    assert '2' in request.querystring['maxJourneys']


@httpretty.activate
def test_limit():
    httpretty.register_uri(httpretty.GET, BVG_URL, body=DEPARTURE_HTML)
    departures, ok = request_departures('9120025', limit=2)
    assert ok is True
    assert len(departures) == 2
