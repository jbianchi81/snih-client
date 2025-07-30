# SNIH api client
## Installation
```bash
pip install -r requirements.txt
```
## Run from command line :
```text
$ python snih-client.py --help
usage: snih-client.py [-h] [-f {csv,json}] [-s SITE] [-v VARIABLE] [-b BEGIN_DATE] [-e END_DATE]
                      {sites,variables,observations,present-values,last-records} output_path

Download and save SNIH metadata/data

positional arguments:
  {sites,variables,observations,present-values,last-records}
                        Metadata/data list to retrieve
  output_path           Path to the output file (e.g., /path/to/file.csv)

options:
  -h, --help            show this help message and exit
  -f {csv,json}, --format {csv,json}
                        Output format: 'csv' (default) or 'json'
  -s SITE, --site SITE  site ID (required for present-values, last-records)
  -v VARIABLE, --variable VARIABLE
                        variable ID (required for last-records)
  -b BEGIN_DATE, --begin_date BEGIN_DATE
                        begin date (required for last-records)
  -e END_DATE, --end_date END_DATE
                        end date (required for last-records)
```
### Examples
```bash
# retrieve sites
python snih-client.py sites sample_data/sites.csv -f csv
python snih-client.py sites sample_data/sites.json -f json
# retrieve variables
python snih-client.py variables sample_data/variables.csv -f csv
python snih-client.py variables sample_data/variables.json -f json
# retrieve observations (which variables at which sites)
python snih-client.py observations sample_data/observations.json -f json
python snih-client.py observations sample_data/observations.csv -f csv
# retrieve present values (of each variable at one site)
python snih-client.py present-values sample_data/present_values.json -f json -s 14413
python snih-client.py present-values sample_data/present_values.csv -f csv -s 14413
# retrieve last records (of one variable at one site)
python snih-client.py last-records sample_data/last_records.json -f json -s 14413 -v 20 -b 2025-06-01 -e 2025-07-29
python snih-client.py last-records sample_data/last_records.csv -f csv -s 14413 -v 20 -b 2025-06-01 -e 2025-07-29
# retrieve historical records (of one variable at one site)
python snih-client.py historical sample_data/historical.json -f json -s 14064 -v 101 -b 2015-04-29 -e 2025-07-29
python snih-client.py historical sample_data/historical.csv -f csv -s 14064 -v 101 -b 2015-04-29 -e 2025-07-29
``` 