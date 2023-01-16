from enum import Enum
from typing import List


class TimeMetrics(Enum):

    WORK_TIME = "work time"
    FOCUS_TIME = "focus time"
    LEISURE_TIME = "leisure time"
    SLEEP_TIME = "sleep time"


def get_time_headers() -> List[str]:
    return [identifier.value for identifier in TimeMetrics]
