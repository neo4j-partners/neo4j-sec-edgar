import argparse
import os
import numpy as np
import pandas as pd
from pandas import Timestamp, DataFrame, Series


def main() -> int:
    args = parse_args()
    filings_df = pd.read_csv(args.input_file)
    target_df = make_target_df(filings_df)
    #TODO: split into test, valid, train sets
    output_dir = args.output_directory
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    target_df.to_csv(os.path.join(output_dir, 'baseline.csv'), index=False)
    return 0


def parse_args():
    parser = argparse.ArgumentParser(
        description='Create datasets from formatted SEC filings to train a ML model to predict new stock '
                    'purchases',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-i', '--input-file', required=False, default='data/form13.csv',
                        help='Formatted From13 csv file')
    parser.add_argument('-o', '--output-directory', required=False, default='data/form13-ml/',
                        help='Local directory to write ML data too')
    args = parser.parse_args()
    return args


def get_prediction_candidates(filing_manager: str, current_period: Timestamp,
                              all_issuers_df: DataFrame, filings_df: DataFrame) -> Series:
    current_holdings = filings_df.loc[(filings_df.managerName == filing_manager) & (
            filings_df.reportCalendarOrQuarter == current_period), 'cusip'].unique()
    return all_issuers_df[~all_issuers_df.isin(current_holdings)]


def make_prediction_targets(filing_manager: str, predict_period: Timestamp, candidates: Series,
                            filings_df: DataFrame) -> DataFrame:
    future_holdings_df = filings_df.loc[
        (filings_df.managerName == filing_manager) & (filings_df.reportCalendarOrQuarter == predict_period),
        ['cusip']].drop_duplicates()
    future_holdings_df['newBuy'] = future_holdings_df.cusip.isin(candidates).astype(int)
    return future_holdings_df


def make_target_pairs(filing_manager: str, current_period: Timestamp, predict_period: Timestamp,
                      all_issuers_df: DataFrame, filings_df: DataFrame) -> DataFrame:
    pred_candidates = get_prediction_candidates(filing_manager, current_period, all_issuers_df, filings_df)
    pred_target_df = make_prediction_targets(filing_manager, predict_period, pred_candidates, filings_df)
    pred_target_df['managerName'] = filing_manager
    pred_target_df['reportCalendarOrQuarter'] = predict_period
    return pred_target_df

#TODO: Rule out new buys for managers that did not exist in past perionds
def make_target_df(filings_df: DataFrame) -> DataFrame:
    periods = np.sort(filings_df.reportCalendarOrQuarter.unique())
    filing_managers = filings_df.managerName.unique()
    all_issuers_df = filings_df.cusip.drop_duplicates()
    target_dfs = []
    for p in range(len(periods)-1):
        for filing_manager in filing_managers:
            print(filing_manager)
            target_dfs.append(make_target_pairs(filing_manager, periods[p], periods[p+1], all_issuers_df, filings_df))
    return pd.concat(target_dfs, ignore_index=True)


if __name__ == "__main__":
    raise SystemExit(main())
