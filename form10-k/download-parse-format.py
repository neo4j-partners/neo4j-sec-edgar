import argparse
import json
from typing import Dict, List
import datetime
import os
import re
import pandas as pd
from bs4 import BeautifulSoup
from secedgar import filings, FilingType


def main() -> int:
    args = parse_args()
    start_date = datetime.datetime.strptime(args.start_date, '%Y-%m-%d').date()
    end_date = datetime.datetime.strptime(args.end_date, '%Y-%m-%d').date()
    temp_dir = args.temp_directory
    output_dir = args.output_directory
    user_agent = args.user_agent

    print('Pulling company list...')
    company_list = create_company_list(args.input_file)

    print(f'Found {len(company_list):,} companies to pull filings for')
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    count = 0
    total = len(company_list)
    print(f'=== Downloading {total:,} 10K filings ===')
    for company_name in company_list:
        count += 1
        print(f'--- Downloading {count:,} of {total:,} 10K filings for {company_name}')
        try:
            raw_files_dir = download_filing(company_name, temp_dir, user_agent, start_date, end_date)
            filing_list = os.listdir(raw_files_dir)

            parse_exception_flag = False
            for filing in filing_list:
                raw_file_path = os.path.join(raw_files_dir, filing)
                output_file_path = os.path.join(output_dir, filing)
                try:
                    load_parse_save(raw_file_path, output_file_path, company_name)
                    os.remove(raw_file_path)
                except Exception as e:
                    parse_exception_flag = True
                    print(e)
            if not parse_exception_flag:
                os.rmdir(raw_files_dir)
        except Exception as e:
            print(e)
    return 0


def parse_args():
    parser = argparse.ArgumentParser(
        description='download 10k filings and pull text from sections 1,1A, 7, and 7A from 10-ks and save as json',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-t', '--temp-directory', required=False, default='data/temp-10k',
                        help='Directory to temporarily store raw SEC 10K files')
    parser.add_argument('-o', '--output-directory', required=False, default='data/form10k-clean',
                        help='Local path to write formatted text to')
    parser.add_argument('-u', '--user-agent', default='sales@neo4j.com',
                        help='Email address to use for user agent in SEC EDGAR calls')
    parser.add_argument('-s', '--start-date', default='2022-01-01', help='Start date in the format yyyy-mm-dd')
    parser.add_argument('-e', '--end-date', default='2023-01-01', help='End date in the format yyyy-mm-dd')
    parser.add_argument('-i', '--input-file', required=False, default='data/form13.csv',
                        help='Formatted Form13 csv file to pull company names from')
    args = parser.parse_args()
    return args


def download_filing(company_name: str, temp_dir: str, user_agent: str, start_date, end_date):
    filings_obj = filings(cik_lookup=company_name,
                          filing_type=FilingType.FILING_10K,
                          user_agent=user_agent,
                          end_date=end_date,
                          start_date=start_date)
    filings_obj.save(temp_dir, dir_pattern='{cik}')

    return os.path.join(temp_dir, company_name)


def create_company_list(formatted_data_path: str) -> List[str]:
    return pd.read_csv(formatted_data_path, usecols=['companyName']).companyName.unique().tolist()


def extract_10_k(txt: str) -> str:
    # Regex to find <DOCUMENT> tags
    doc_start_pattern = re.compile(r'<DOCUMENT>')
    doc_end_pattern = re.compile(r'</DOCUMENT>')
    # Regex to find <TYPE> tag proceeding any characters, terminating at new line
    type_pattern = re.compile(r'<TYPE>[^\n]+')
    # Create 3 lists with the span idices for each regex

    # There are many <Document> Tags in this text file, each as specific exhibit like 10-K, EX-10.17 etc
    # First filter will give us document tag start <end> and document tag end's <start>
    # We will use this to later grab content in between these tags
    doc_start_is = [x.end() for x in doc_start_pattern.finditer(txt)]
    doc_end_is = [x.start() for x in doc_end_pattern.finditer(txt)]

    # Type filter is interesting, it looks for <TYPE> with Not flag as new line, ie terminare there, with + sign
    # to look for any char afterwards until new line \n. This will give us <TYPE> followed Section Name like '10-K'
    # Once we have have this, it returns String Array, below line will with find content after <TYPE> ie, '10-K'
    # as section names
    doc_types = [x[len('<TYPE>'):] for x in type_pattern.findall(txt)]
    # Create a loop to go through each section type and save only the 10-K section in the dictionary
    # there is just one 10-K section
    for doc_type, doc_start, doc_end in zip(doc_types, doc_start_is, doc_end_is):
        if doc_type == '10-K':
            return txt[doc_start:doc_end]


# Extract text using position dataframe and beautiful soup
def beautify_text(txt: str) -> str:
    stg_txt = BeautifulSoup(txt, 'lxml')
    return stg_txt.get_text('\n')


def extract_text(row: pd.Series, txt: str):
    section_txt = txt[row.start:row.sectionEnd].replace('Error! Bookmark not defined.', '')
    return beautify_text(section_txt)


def extract_section_text(doc: str) -> Dict[str, str]:
    # Write the regex
    regex = re.compile(r'(>(Item|ITEM)(\s|&#160;|&nbsp;)(1A|1B|1\.|7A|7|8)\.{0,1})|(ITEM\s(1A|1B|1\.|7A|7|8))')
    # Use finditer to math the regex
    matches = regex.finditer(doc)
    # Write a for loop to print the matches
    # Create the dataframe
    item_df = pd.DataFrame([(x.group(), x.start(), x.end()) for x in matches])
    item_df.columns = ['item', 'start', 'end']
    item_df['item'] = item_df.item.str.lower()

    item_df.replace('&#160;', ' ', regex=True, inplace=True)
    item_df.replace('&nbsp;', ' ', regex=True, inplace=True)
    item_df.replace(' ', '', regex=True, inplace=True)
    item_df.replace('\.', '', regex=True, inplace=True)
    item_df.replace('>', '', regex=True, inplace=True)

    all_pos_df = item_df.sort_values('start', ascending=True).drop_duplicates(subset=['item'], keep='last').set_index(
        'item')
    # Add section end using start of next section
    all_pos_df['sectionEnd'] = all_pos_df.start.iloc[1:].tolist() + [len(doc)]
    # filter to just the sections we care about
    pos_df = all_pos_df.loc[['item1', 'item1a', 'item7', 'item7a'], :]
    res = dict()
    for i, row in pos_df.iterrows():
        res[i] = extract_text(row, doc)
    return res


def load_parse_save(input_file_path: str, output_file_path: str, company_name: str):
    with open(input_file_path, 'r') as file:
        raw_txt = file.read()
    print('Extracting 10-K')
    doc = extract_10_k(raw_txt)
    print('Parsing relevant sections')
    cleaned_json_txt = extract_section_text(doc)
    cleaned_json_txt['companyName'] = company_name
    print('Writing clean text to json')
    with open(output_file_path, 'w') as json_file:
        json.dump(cleaned_json_txt, json_file, indent=4)


if __name__ == "__main__":
    raise SystemExit(main())
