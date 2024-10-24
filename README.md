isimip-logs
===========

Setup
-----

```
pip install -r requirements.py
```

Usage
-----

```bash
# fetches citations for all DOI from data.isimip.org
./fetch_citations.py  

# fetches citations for all DOI from data.isimip.org including old version
./fetch_citations.py -a

# fetches citations for selected DOI from data.isimip.org
./fetch_citations.py https://doi.org/10.5880/PIK.2019.023 https://doi.org/10.48364/ISIMIP.342217 
```
