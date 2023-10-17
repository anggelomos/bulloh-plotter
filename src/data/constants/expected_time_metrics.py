from typing import List

expected_time_metrics = {
    "expected work time": 6,
    "expected focus time": 4,
    "expected leisure time": 2,
}


def get_expected_time_headers() -> List[str]:
    return [identifier for identifier in expected_time_metrics.keys()]
