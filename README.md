# bvg-cli
`bvg-cli` is a simple *command line tool* for the public transport of Berlin. It provides a simple way to get the latest departure times for the stations of subway, bus, tram and urban rail system.
It is written in Python and makes use of some excellent packages provided by its awesome community.

## Features
* limit the number of departure times
* filter the types of transport (select/ignore)

## Usage
```
$ ./bvg_cli.py --station NAME [--limit N] [--select types] [--ignore types]
```

### Examples
```
$ ./bvg_cli.py --station Alexanderplatz
```

This request will only show departures for underground (U-Bahn) and suburban railway (S-Bahn).
```
$ ./bvg_cli.py --station Alexanderplatz --select S,U
```
This request will show the next 5 departures skipping buses and regional railways.
```
$ ./bvg_cli.py --station Alexanderplatz --ignore B,R --limit 5
```