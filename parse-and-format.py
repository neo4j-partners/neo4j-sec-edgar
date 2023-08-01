import argparse

import pandas as pd
import os
import re
import xmltodict

FILING_MANAGER_COL = 'managerName'
REPORT_PERIOD_COL = 'reportCalendarOrQuarter'
CUSIP_COL = 'cusip'
COMPANY_NAME_COL = 'issuerName'
FILING_ID_COL = 'filingId'
VALUE_COL = 'value'
SHARES_COL = 'shares'


def main() -> int:
    args = parse_args()
    filings_df = parse_from_dir(args.input_directory)
    stg_df = aggregate_data(filings_df)
    if args.top_periods is not None:
        stg_df = filter_data(stg_df, args.top_periods)
    stg_df.to_csv(args.output_file, index=False)
    return 0


def parse_args():
    parser = argparse.ArgumentParser(description='format raw form13s from EDGAR SEC into a csv for graph loading',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-i', '--input-directory', required=False, default='data/form13-raw/',
                        help='Directory containing raw EDGAR files')
    parser.add_argument('-o', '--output-file', required=False, default='data/form13.csv',
                        help='Local path + file name to write formatted csv too')
    parser.add_argument('-p', '--top-periods', required=False, type=int,
                        help='Only include data from `n` most recent report quarters')
    args = parser.parse_args()
    return args


def parse(raw_contents: str) -> pd.DataFrame:
    # hacky way to trim namespace.  Should probably come back and parse properly later
    # trim literals
    contents = raw_contents
    for x in 'ns', 'eis', 'N1', 'n1':
        contents = contents.replace('<' + x + ':', '<')
        contents = contents.replace('</' + x + ':', '</')
    # trim ns patterns
    ns_pattern = r'ns\d+'
    contents = re.sub('<' + ns_pattern + ':', '<', contents)
    contents = re.sub('</' + ns_pattern + ':', '</', contents)

    contents = contents.split('<XML>')
    edgar_submission = contents[1]
    edgar_submission = edgar_submission.split('</XML>')[0]
    edgar_submission = edgar_submission.split('\n', 1)[1]
    edgar_submission = xmltodict.xmltodict(edgar_submission)

    report_calendar_or_quarter = edgar_submission['formData'][0]['coverPage'][0]['reportCalendarOrQuarter'][0]
    filing_manager = edgar_submission['formData'][0]['coverPage'][0]['filingManager'][0]['name'][0]

    if len(contents) < 3:
        print('Empty informationTable.')
        return []

    information_table = contents[2]
    information_table = information_table.split('</XML>')[0]
    information_table = information_table.split('\n', 1)[1]
    information_table = information_table.replace('" http', '"http', 1)  # deal with bad XML from BNY Mellon
    information_table = information_table.replace(' ">', '">', 1)  # deal with bad XML from TCW
    try:
        information_table = xmltodict.xmltodict(information_table)
    except:
        print('Error parsing information table.')
        file = open('informationTable.xml', "w")
        file.write(information_table)
        exit()

    filings = []
    for infoTable in information_table['infoTable']:
        # Only want stock holdings, not options
        if infoTable['shrsOrPrnAmt'][0]['sshPrnamtType'][0] != 'SH':
            pass
        # Only want holdings over $10m
        elif (float(infoTable['value'][0]) * 1000) < 10000000:
            pass
        # Only want common stock
        elif infoTable['titleOfClass'][0] != 'COM':
            pass
        else:
            filing = {FILING_MANAGER_COL: filing_manager, REPORT_PERIOD_COL: report_calendar_or_quarter,
                      COMPANY_NAME_COL: infoTable['nameOfIssuer'][0], CUSIP_COL: infoTable['cusip'][0],
                      VALUE_COL: infoTable['value'][0].replace(' ', '') + '000',
                      SHARES_COL: infoTable['shrsOrPrnAmt'][0]['sshPrnamt'][0]}
            filings.append(filing)
    return pd.DataFrame(filings)


def parse_from_dir(directory_path: str) -> pd.DataFrame:
    filings_dfs = []
    for file_name in os.listdir(directory_path):
        if file_name.endswith('.txt'):
            file_path = os.path.join(directory_path, file_name)
            with open(file_path, 'r') as file:
                contents = file.read()
                tmp_filings_df = parse(contents)
                tmp_filings_df[FILING_ID_COL] = file_name
                filings_dfs.append(tmp_filings_df)
    filing_df = pd.concat(filings_dfs, ignore_index=True)
    filing_df.reportCalendarOrQuarter = pd.to_datetime(filing_df.reportCalendarOrQuarter).dt.date
    filing_df.value = filing_df.value.astype(float)
    filing_df.shares = filing_df.shares.astype(int)
    return filing_df


# This data contains duplicates where an asset is reported more than once for the same filing manager within the same
# report calendar/quarter.
# See for example https://www.sec.gov/Archives/edgar/data/1962636/000139834423009400/0001398344-23-009400.txt
# for our intents and purposes we will sum over values and shares to aggregate the duplicates out
def aggregate_data(filings_df: pd.DataFrame) -> pd.DataFrame:
    return filings_df.groupby([FILING_MANAGER_COL, REPORT_PERIOD_COL, CUSIP_COL]) \
        .agg({VALUE_COL: sum, SHARES_COL: sum, FILING_ID_COL: max, COMPANY_NAME_COL: 'first'}) \
        .reset_index()


def filter_data(filings_df: pd.DataFrame, top_n_periods: int) -> pd.DataFrame:
    periods_df = filings_df[[REPORT_PERIOD_COL, VALUE_COL]] \
        .groupby(REPORT_PERIOD_COL).count().reset_index().sort_values(REPORT_PERIOD_COL)
    num_periods = min(periods_df.shape[0], top_n_periods)
    top_periods = periods_df.reportCalendarOrQuarter[-num_periods:].tolist()
    return filings_df[filings_df.reportCalendarOrQuarter.isin(top_periods)]


if __name__ == "__main__":
    raise SystemExit(main())
