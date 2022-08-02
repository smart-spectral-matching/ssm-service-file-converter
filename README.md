# SSM file converter service

This service helps convert files to different formats.

Currently supported:

| Input formats               | Output formats              | Example                                                                                                               |
|-----------------------------|-----------------------------|-----------------------------------------------------------------------------------------------------------------------|
| [JCAMP-DX][jcamp]           | [SciData JSON-LD][scidata]  | `curl -X POST -F "upload_file=@tests/data/jcamp/raman_soddyite.jdx" http://localhost:8000/convert/jsonld`             |
| [RRUFF][rruff]              | [SciData JSON-LD][scidata]  | `curl -X POST -F "upload_file=@tests/data/rruff/raman_soddyite.rruff" http://localhost:8000/convert/jsonld`           |
| [SciData JSON-LD][scidata]  | [SciData JSON-LD][scidata]  | `curl -X POST -F "upload_file=@tests/data/scidata-jsonld/raman_soddyite.jsonld" http://localhost:8000/convert/jsonld` |
| [JCAMP-DX][jcamp]           | SSM JSON (interal use only) | `curl -X POST -F "upload_file=@tests/data/jcamp/raman_soddyite.jdx" http://localhost:8000/convert/json`               |
| [RRUFF][rruff]              | SSM JSON (interal use only) | `curl -X POST -F "upload_file=@tests/data/rruff/raman_soddyite.rruff" http://localhost:8000/convert/json`             |
| [SciData JSON-LD][scidata]  | SSM JSON (interal use only) | `curl -X POST -F "upload_file=@tests/data/scidata-jsonld/raman_soddyite.jsonld" http://localhost:8000/convert/json` |


Internally, this service primarily uses [SciDataLib][scidatalib] for conversions.

# Quickstart

Start up the service:

```
make docker-run
```

Then, you can use the example commands in the table above to test.

[jcamp]: http://stuchalk.github.io/scidata/
[rruff]: https://rruff.info/
[scidata]: http://stuchalk.github.io/scidata/
[scidatalib]: https://github.com/ChalkLab/SciDataLib
