# SSM file converter service

This service helps convert and merge files to different formats.


# Converter

Endpoint: `/convert`

Currently supported:

| Input formats                | Output formats              | Example                                                                                                               |
|------------------------------|-----------------------------|-----------------------------------------------------------------------------------------------------------------------|
| [JCAMP-DX][jcamp]            | [SciData JSON-LD][scidata]  | `curl -X POST -F "upload_file=@tests/data/jcamp/raman_soddyite.jdx" http://localhost:8000/convert/jsonld`             |
| [RRUFF][rruff]               | [SciData JSON-LD][scidata]  | `curl -X POST -F "upload_file=@tests/data/rruff/raman_soddyite.rruff" http://localhost:8000/convert/jsonld`           |
| [SciData JSON-LD][scidata]   | [SciData JSON-LD][scidata]  | `curl -X POST -F "upload_file=@tests/data/scidata-jsonld/raman_soddyite.jsonld" http://localhost:8000/convert/jsonld` |
| SSM JSON (internal use only) | [SciData JSON-LD][scidata]  | `curl -X POST -F "upload_file=@tests/data/ssm-json/raman_soddyite.json" http://localhost:8000/convert/jsonld`         |
| [JCAMP-DX][jcamp]            | SSM JSON (internal use only) | `curl -X POST -F "upload_file=@tests/data/jcamp/raman_soddyite.jdx" http://localhost:8000/convert/json`               |
| [RRUFF][rruff]               | SSM JSON (internal use only) | `curl -X POST -F "upload_file=@tests/data/rruff/raman_soddyite.rruff" http://localhost:8000/convert/json`             |
| [SciData JSON-LD][scidata]   | SSM JSON (internal use only) | `curl -X POST -F "upload_file=@tests/data/scidata-jsonld/raman_soddyite.jsonld" http://localhost:8000/convert/json` |


Internally, this service primarily uses [SciDataLib][scidatalib] for conversions.

# Merger

Endpoint: `/merge`

Currently supported:

| Original input format        | Change set input format     | Output merged format       |
|------------------------------|-----------------------------|----------------------------|
| [SciData JSON-LD][scidata]  | SSM JSON (internal use only) | [SciData JSON-LD][scidata] |

Example:
```
curl -F "upload_files=@tests/data/scidata-jsonld/raman_soddyite.jsonld" -F "upload_files=@tests/data/ssm-json/raman_soddyite.json" http://localhost:8000/merge/jsonld
```

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
