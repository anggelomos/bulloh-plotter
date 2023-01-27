import datetime
from typing import Union, List

from data.constants.expected_time_metrics import get_expected_time_headers
from data.constants.habits import get_habit_headers
from data.constants.habits_time import get_habit_time_headers
from data.constants.row_identifier import get_row_identifiers
from data.constants.time_metrics import get_time_headers
from numpy import int64


class GeneralUtilities:

    @staticmethod
    def get_all_headers() -> List[str]:
        return get_row_identifiers() + get_time_headers() \
               + get_habit_headers() + get_habit_time_headers() + get_expected_time_headers()

    @staticmethod
    def round_number(number, amount_of_digits: int = 0, round_zero: bool = True) -> Union[float, int]:
        rounded_number = round(number, amount_of_digits)
        if rounded_number == 0 and round_zero:
            return 0
        if amount_of_digits == 0:
            return int(rounded_number)
        if isinstance(rounded_number, int64):
            return int(rounded_number)
        return rounded_number

    @staticmethod
    def adapt_keys(dictionary: dict, old_char: str = " ", new_char: str = "-") -> dict:
        return dict(map(lambda x: (x[0].replace(old_char, new_char), x[1]), dictionary.items()))
