import pandas as pd


class Database:
    url = ('https://docs.google.com/spreadsheets/d/12U5G94RRohSdDujUKU70LrS3iCKOOe5rRKfVIGmVaf0/'
           'export?format=csv&id=12U5G94RRohSdDujUKU70LrS3iCKOOe5rRKfVIGmVaf0&gid=0')

    def __init__(self):
        df = pd.read_csv(Database.url)
        self.admins = df['admin'].tolist()
        self.profile_ids = df['profile_id'].tolist()
        self.messages = df['message'].tolist()
        self.targets = df['targets'].tolist()
        self.telegrams = df['telegram'].dropna().tolist()
