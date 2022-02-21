from pandas import read_csv


class Database:
    user: str
    profile_id: str
    telegram: str
    message: str
    targets: str
    timer_btw_targets: str
    timer: str
    join_links: str
    api_id: str
    api_hash: str
    user_session: str

    def __init__(self, page):
        self.url = (f'https://docs.google.com/spreadsheets/d/12U5G94RRohSdDujUKU70LrS3iCKOOe5rRKfVIGmVaf0/'
                    f'export?format=csv&id=12U5G94RRohSdDujUKU70LrS3iCKOOe5rRKfVIGmVaf0&gid={page}')
        self.frame = read_csv(self.url, dtype={
            'user': str,
            'profile_id': str,
            'telegram': str,
            'message': str,
            'targets': str,
            'timer_btw_targets': str,
            'timer': str,
            'join_links': str,
            'api_id': str,
            'api_hash': str,
            'user_session': str,
        })

    def __getattr__(self, item):
        value = tuple(self.frame[item].dropna())
        if len(value) == 1:
            return value[0]
        elif len(value) > 1:
            return value
        else:
            return None