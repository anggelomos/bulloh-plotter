from enum import Enum
from typing import List

from data.constants.habits import Habits


class HabitsTime(Enum):

    PROJECT_TIME = "project time"
    READ_TIME = "read time"
    PLAN_TIME = "plan time"
    MEDITATE_TIME = "meditate time"
    EXERCISE_TIME = "exercise time"
    JOURNALING_TIME = "journaling time"
    LEARN_LANGUAGE_TIME = "learn language time"


irregular_habits_time_parser = {
    HabitsTime.PLAN_TIME.value: Habits.PLAN_DAY.value,
    HabitsTime.PROJECT_TIME.value: Habits.WORK_ON_RESOLUTIONS.value
}


def get_habit_time_headers() -> List[str]:
    return [identifier.value for identifier in HabitsTime]
