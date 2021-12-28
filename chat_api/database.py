import pandas as pd


class Database:
    def __init__(self, page):
        url = ('https://docs.google.com/spreadsheets/d/12U5G94RRohSdDujUKU70LrS3iCKOOe5rRKfVIGmVaf0/'
               f'export?format=csv&id=12U5G94RRohSdDujUKU70LrS3iCKOOe5rRKfVIGmVaf0&gid={page}')
        self.dataframe = pd.read_csv(url, dtype={'targets': str, 'user': str})

    def __call__(self, arg):
        return self.dataframe[arg].dropna().tolist()


if __name__ == '__main__':
    data = Database(29833681)
    for n in data('targets'):
        print(n)