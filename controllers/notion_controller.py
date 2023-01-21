from datetime import datetime
from typing import Union, List

import requests
import pandas as pd
from data.constants.expected_time_metrics import get_expected_time_headers, expected_time_metrics

from data.payloads.notion_payloads import NotionPayloads as payloads
from pandas import DataFrame
from utilities.general_utilities import GeneralUtilities


class NotionController:
    base_url = "https://api.notion.com/v1"
    stats_table_id = "baa09f8600924192b1e9ceef4cfa70ce"

    def __init__(self, auth_secret: str, notion_version: str):
        self._default_headers = payloads.get_headers(notion_version, auth_secret)

    def query_table(self, table_id: str, query: str) -> List[dict]:
        response = requests.post(url=self.base_url + "/databases/" + table_id + "/query",
                                 data=query,
                                 headers=self._default_headers)

        return response.json()["results"]

    @staticmethod
    def _parse_prop(prop: dict) -> Union[str, bool, float]:
        if "checkbox" in prop:
            return prop["checkbox"]
        elif "number" in prop:
            if not prop["number"]:
                return 0
            return prop["number"]
        elif "date" in prop:
            return prop["date"]["start"]
        elif "formula" in prop:
            if "boolean" in prop["formula"]:
                return prop["formula"]["boolean"]
            elif "number" in prop["formula"]:
                return prop["formula"]["number"]
        else:
            raise ValueError("Unknown property type")

    def parse_rows(self, rows: Union[List[dict], dict], as_dict: bool = False) -> Union[list, dict]:
        headers = GeneralUtilities.get_all_headers()

        if isinstance(rows, dict):
            rows = [rows]

        rows_parsed = []
        for row in rows:
            row_data = []
            for header in headers:
                if header in get_expected_time_headers():
                    row_data.append(expected_time_metrics[header])
                else:
                    row_data.append(self._parse_prop(row["properties"][header]))

            if as_dict:
                rows_parsed.append(dict(zip(headers, row_data)))
            else:
                rows_parsed.append(row_data)

        return rows_parsed

    def get_data_between_dates(self, start_date: datetime.date, end_date: datetime.date) -> DataFrame:
        raw_data = self.query_table(self.stats_table_id, payloads.get_data_between_dates(start_date, end_date))
        return pd.DataFrame(self.parse_rows(raw_data), columns=GeneralUtilities.get_all_headers())
