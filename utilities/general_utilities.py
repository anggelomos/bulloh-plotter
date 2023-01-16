import datetime
from typing import Union, List

from data.constants.expected_time_metrics import get_expected_time_headers
from data.constants.habits import get_habit_headers
from data.constants.habits_time import get_habit_time_headers
from data.constants.row_identifier import get_row_identifiers
from data.constants.time_metrics import get_time_headers


class GeneralUtilities:

    @staticmethod
    def get_all_headers() -> List[str]:
        return get_row_identifiers() + get_time_headers() \
               + get_habit_headers() + get_habit_time_headers() + get_expected_time_headers()
