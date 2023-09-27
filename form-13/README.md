# form-13
To start the Form-13 downloader run this:

```python form13-download.py```

```
optional arguments:
-s, --start-date, Start date in the format yyyy-mm-dd (default: 2022-01-01)
-e, --end-date, End date in the format yyyy-mm-dd (default: 2023-08-01)
-o, --output-directory, Local directory to write forms to (default: data/form13-raw/)
```

## Parse & Format Form13
Once you have all the raw forms downloaded, this file will parse and format them into a csv file.

```python form13-parse-and-format.py -p 4```

```
optional arguments:
-i, --input-directory, Directory containing raw EDGAR files (default: data/form13-raw/)
-o, --output-file, Local path + file name to write formatted csv too (default: data/form13.csv)
-p, --top-periods, Only include data from `n` most recent report quarters (default: None)
```
