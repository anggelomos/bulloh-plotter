from typing import List

from src.data.constants.expected_time_metrics import get_expected_time_headers
from src.data.constants.habits import get_habit_headers
from src.data.constants.habits_time import get_habit_time_headers
from src.data.constants.row_identifier import get_row_identifiers
from src.data.constants.time_metrics import get_time_headers


class GeneralUtilities:

    @staticmethod
    def get_all_headers() -> List[str]:
        return get_row_identifiers() + get_time_headers() \
               + get_habit_headers() + get_habit_time_headers() + get_expected_time_headers()

    @staticmethod
    def adapt_keys(dictionary: dict, old_char: str = " ", new_char: str = "-") -> dict:
        return dict(map(lambda x: (x[0].replace(old_char, new_char), x[1]), dictionary.items()))
