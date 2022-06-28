from pandas import read_csv
from module.config import Config


class DataBase:
    db_id = Config.db_id

    def get_frane(self, page, dtype):
        url = (f'https://docs.google.com/spreadsheets/d/{self.db_id}/'
               f'export?format=csv&id={self.db_id}&gid={page}')
        return read_csv(url, dtype=dtype)


class UserFromDB(DataBase):
    page_id: str
    name: str
    message: str
    targets: tuple
    timer: int
    timer_btw_targets: int
    telegram: str

    def __init__(self, page: str):
        self.page_id = page
        self.__frame = self.get_frane(page, {
            'name': str,
            'message': str,
            'telegram': str,
            'targets': str,
            'timer': str,
            'timer_btw_targets': str,
        })

    @property
    def name(self) -> str:
        return str(self.__frame['name'][0])

    @property
    def message(self) -> str:
        return str(self.__frame['message'][0])

    @property
    def targets(self) -> tuple:
        return tuple(self.__frame['targets'].dropna())

    @property
    def timer(self) -> int:
        return int(self.__frame['timer'][0])

    @property
    def timer_btw_targets(self) -> int:
        return int(self.__frame['timer_btw_targets'][0])

    @property
    def telegram(self) -> str:
        return str(self.__frame['telegram'][0])


class ConfigFromDB(DataBase):
    join_links: tuple
    api_id: int
    api_hash: str
    user_session: str

    def __init__(self, page: str):
        self.__frame = self.get_frane(page, dtype={
            'join_links': str,
            'api_id': str,
            'api_hash': str,
            'user_session': str
        })

    @property
    def join_links(self) -> tuple:
        return tuple(self.__frame['join_links'].dropna())

    @property
    def api_id(self) -> int:
        return int(self.__frame['api_id'][0])

    @property
    def api_hash(self) -> str:
        return str(self.__frame['api_hash'][0])

    @property
    def user_session(self) -> str:
        return str(self.__frame['user_session'][0])
