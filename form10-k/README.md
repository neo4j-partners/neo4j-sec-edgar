# form-10-k
This program uses company names from the form13 parsed and formatted file (outputed above) to search for and download 10K files.  It will then parse out relevant 10K item text and save to json files, one json file per company. See __10K Notes__ below for more details on the reasoning behind parsing and item selection.

```python filing10k-download-parse-format.py```

```
optional arguments:
  -i,  --input-file, Formatted Form13 csv file to pull company names from (default: data/form13.csv)
  -o, --output-directory, Local path to write formatted text to (default: data/form10k-clean)
  -t , --temp-directory, Directory to temporarily store raw SEC 10K files (default: data/temp-10k)
  -u, --user-agent, Email address to use for user agent in SEC EDGAR calls (default: sales@neo4j.com)
  -s, --start-date, Start date in the format yyyy-mm-dd (default: 2022-01-01)
  -e, --end-date, End date in the format yyyy-mm-dd (default: 2023-01-01)

```

Once that is done, go ahead and zip the files:

```
cd data
zip -r form10k-clean.zip form10k-clean/
cd ..
```

## Notes

A [10K](https://www.investor.gov/introduction-investing/investing-basics/glossary/form-10-k) is a comprehensive report filed annually by a publicly traded company about its financial performance and is required by the U.S. Securities and Exchange Commission (SEC). The report contains a comprehensive overview of the company's business and financial condition and includes audited financial statements. While 10Ks contain images and table figures, they primarily consist of free-form text which is what we are interested in extracting here.

Raw 10K reports are structured in iXBRL, or Inline eXtensible Business Reporting Language, which is extremely verbose, containing more markup than actual text content, [here is an example from APPLE](https://www.sec.gov/Archives/edgar/data/320193/000032019322000108/0000320193-22-000108.txt).

This makes raw 10K files very large, unwieldy, and inefficient for direct application of LLM or text embedding services. For this reason, the program contained here, `filing10k-download-parse-format.py`, applies regex and NLP to parse out as much iXBRL and unnecessary content as possible to make 10K text useful.

In addition, `filing10k-download-parse-format.py` also extracts only a subset of items from the 10K that we feel are most relevant for initial exploration and experimentation.  These are sections that discuss the overall business outlook and risk factors, specifically:

* __Item 1 – Business__
This describes the business of the company: who and what the company does, what subsidiaries it owns, and what markets it operates in. It may also include recent events, competition, regulations, and labor issues. (Some industries are heavily regulated, have complex labor requirements, which have significant effects on the business.) Other topics in this section may include special operating costs, seasonal factors, or insurance matters.
* __Item 1A – Risk Factors__
Here, the company lays out anything that could go wrong, likely external effects, possible future failures to meet obligations, and other risks disclosed to adequately warn investors and potential investors.
* __Item 7 – Management's Discussion and Analysis of Financial Condition and Results of Operations__
Here, management discusses the operations of the company in detail by usually comparing the current period versus the prior period. These comparisons provide a reader an overview of the operational issues of what causes such increases or decreases in the business.
* __Item 7A – Quantitative and Qualitative Disclosures about Market Risks__
