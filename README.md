# SSM file converter service

This service helps convert files to different formats.

Currently supported:

| Input formats               |
|-----------------------------|
| [JCAMP-DX][jcamp]           |
| [RRUFF][rruff]              |


| Output formats              |
|-----------------------------|
| [SciData JSON-LD][scidata]  |
| SSM JSON (interal use only) |

Internally, this service primarily uses [SciDataLib][scidatalib] for conversions.

# Quickstart

Start up the service:

```
make docker-run
```


Submit the JCAMP-DX test data to the API and convert to SciData JSON-LD format:
```
curl -X POST -F "file=@tests/data/jcamp/raman_soddyite.jdx" http://localhost:8000/convert/jsonld
```

Submit the RRUFF test data to the API and convert to SSM JSON format:
```
curl -X POST -F "file=@tests/data/rruff/raman_soddyite.rruff" http://localhost:8000/convert/json
```

[jcamp]: http://stuchalk.github.io/scidata/
[rruff]: https://rruff.info/
[scidata]: http://stuchalk.github.io/scidata/
[scidatalib]: https://github.com/ChalkLab/SciDataLib
