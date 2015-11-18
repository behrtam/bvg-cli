# bvg-cli
`bvg-cli` is a simple *command line tool* for the public transport of Berlin. It provides a simple way to get the latest departure times for the stations of subway, bus, tram and urban rail system.

![demo usage gif](https://raw.githubusercontent.com/behrtam/bvg-cli/master/demo_usage.gif)

It is written in Python and makes use of some excellent packages provided by its awesome community.

## Features
* limit the number of departure times
* filter the types of transport (select/ignore)

## Installation
Quick and dirty way to install the cli until there is `pip` or `brew` support.
```
$ wget -qO- https://raw.githubusercontent.com/behrtam/bvg-cli/master/install.sh | sh
```

## Usage
```
$ bvg_cli --station NAME [--limit N] [--select types] [--ignore types]
```

### Examples
```
$ bvg_cli --station Alexanderplatz
```

This request will only show departures for underground (U-Bahn) and suburban railway (S-Bahn).
```
$ bvg_cli --station Alexanderplatz --select S,U
```
This request will show the next 5 departures skipping buses and regional railways.
```
$ bvg_cli --station Alexanderplatz --ignore B,R --limit 5
```
