import httpretty

from bvg_cli import BVG_URL
from bvg_cli import request_departures, request_station_ids, create_products_filter

from html_dumps import DEPARTURE_HTML, STATION_HTML

from requests.exceptions import Timeout


def mock_timeout_callback(request, uri, headers):
    raise Timeout('Request timed out.')


@httpretty.activate
def test_request_station_server_error():
    httpretty.register_uri(httpretty.GET, BVG_URL, status=500)
    _, ok = request_station_ids('any station')
    assert ok is False


@httpretty.activate
def test_request_station_timeout():
    httpretty.register_uri(httpretty.GET, BVG_URL, body=mock_timeout_callback)
    _, ok = request_station_ids('any station')
    assert ok is False


@httpretty.activate
def test_request_departures_server_error():
    httpretty.register_uri(httpretty.GET, BVG_URL, status=500)
    _, ok = request_departures('any id', limit=10)
    assert ok is False


@httpretty.activate
def test_request_departures_timeout():
    httpretty.register_uri(httpretty.GET, BVG_URL, body=mock_timeout_callback)
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


@httpretty.activate
def test_parameter_products_filter():
    httpretty.register_uri(httpretty.GET, BVG_URL, body=DEPARTURE_HTML)
    products_filter = create_products_filter(select='US')
    _, ok = request_departures('any id', 2, products_filter)
    request = httpretty.last_request()
    assert hasattr(request, 'querystring')
    assert 'productsFilter' in request.querystring
    assert '11000000' in request.querystring['productsFilter']


def test_base_products_filter():
    assert create_products_filter() == '11111111'


def test_select_products_filter():
    assert create_products_filter(select='USR') == '11000100'


def test_ignore_products_filter():
    assert create_products_filter(ignore='US') == '00111111'


def test_overvote_ignore_products_filter():
    assert create_products_filter(select='US', ignore='SBT') == '11000000'


def test_comma_products_filter():
    assert create_products_filter(select='T,B,I') == '00111000'
