from google.cloud import bigquery
import google.api_core.exceptions

# probably need a function to de-dup the table
# that would be called at the end of the day


class database():
    client = None
    dataset_ref = None
    table_ref = None
    table = None
    schema = None

    def __init__(self):
        self.client = bigquery.Client()
        self.dataset_ref = self.client.dataset('edgar')
        self.table_ref = self.dataset_ref.table('form4')

        self.schema = [
            bigquery.SchemaField('SecDocument', 'STRING'),
            bigquery.SchemaField('AcceptanceDatetime', 'DATETIME'),
            bigquery.SchemaField('IssuerTradingSymbol', 'STRING'),
            bigquery.SchemaField('RptOwnerCik', 'STRING'),
            bigquery.SchemaField('RptOwnerName', 'STRING'),
            bigquery.SchemaField('IsDirector', 'BOOLEAN'),
            bigquery.SchemaField('IsOfficer', 'BOOLEAN'),
            bigquery.SchemaField('IsTenPercentOwner', 'BOOLEAN'),
            bigquery.SchemaField('IsOther', 'BOOLEAN'),
            bigquery.SchemaField('TransactionDate', 'DATE'),
            bigquery.SchemaField('TransactionShares', 'FLOAT'),
            bigquery.SchemaField('TransactionPricePerShare', 'FLOAT'),
            bigquery.SchemaField('TransactionAcquired', 'BOOLEAN'),
            bigquery.SchemaField('SharesOwned', 'FLOAT')
        ]

        self.table = bigquery.Table(self.table_ref, schema=self.schema)

        # Create the table or pass if it already exists
        try:
            self.table = self.client.create_table(self.table)
        except google.api_core.exceptions.Conflict:
            pass

        assert self.table.table_id == 'form4'
        self.table = self.client.get_table(self.table_ref)

    def formatRow(self, transaction):
        year = transaction['acceptanceDatetime'][0:4]
        month = transaction['acceptanceDatetime'][4:6]
        day = transaction['acceptanceDatetime'][6:8]
        hour = transaction['acceptanceDatetime'][8:10]
        minute = transaction['acceptanceDatetime'][10:12]
        second = transaction['acceptanceDatetime'][12:14]
        acceptanceDatetime = year + '-' + month + '-' + \
            day + 'T' + hour + ':' + minute + ':' + second

        year = transaction['transactionDate'][0:4]
        month = transaction['transactionDate'][5:7]
        day = transaction['transactionDate'][8:10]
        transactionDate = year + '-' + month + '-' + day

        if(transaction['transactionAcquiredDisposedCode'] == 'A'):
            transactionAcquired = True
        else:
            transactionAcquired = False

        row = (
            transaction['secDocument'],
            acceptanceDatetime,
            transaction['issuerTradingSymbol'],
            transaction['rptOwnerCik'],
            transaction['rptOwnerName'],
            transaction['isDirector'],
            transaction['isOfficer'],
            transaction['isTenPercentOwner'],
            transaction['isOther'],
            transactionDate,
            transaction['transactionShares'],
            transaction['transactionPricePerShare'],
            transactionAcquired,
            transaction['sharesOwned']
        )
        return row

    def insert(self, transactions):
        rows = []
        for transaction in transactions:
            row = self.formatRow(transaction)
            rows.append(row)

        if len(rows) > 0:
            errors = self.client.insert_rows(self.table, rows)
            assert errors == []
