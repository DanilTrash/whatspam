import pandas as pd


class Database:
    url = ('https://docs.google.com/spreadsheets/d/12U5G94RRohSdDujUKU70LrS3iCKOOe5rRKfVIGmVaf0/'
           'export?format=csv&id=12U5G94RRohSdDujUKU70LrS3iCKOOe5rRKfVIGmVaf0&gid=0')

    def __init__(self):
        self.admins = pd.read_csv(Database.url)['admin'].dropna().tolist()
        self.profile_ids = pd.read_csv(Database.url)['profile_id'].dropna().tolist()
        self.messages = pd.read_csv(Database.url)['message'].tolist()
        self.targets = pd.read_csv(Database.url)['targets'].dropna().tolist()
