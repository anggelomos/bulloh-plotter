import datetime
import json
from typing import Union


class NotionPayloads:

    @staticmethod
    def get_headers(notion_version: str, auth_secret: str) -> dict:
        return {
                "content-type": "application/json",
                "Notion-Version": f"{notion_version}",
                "Authorization": f"Bearer {auth_secret}"
                }

    @staticmethod
    def get_data_between_dates(initial_date: Union[str, datetime.date], today_date: Union[str, datetime.date]) -> str:
        if isinstance(initial_date, datetime.date):
            initial_date = initial_date.strftime("%Y-%m-%d")

        if isinstance(today_date, datetime.date):
            today_date = today_date.strftime("%Y-%m-%d")

        filters = []
        if initial_date:
            filters.append({"property": "date","date": {"on_or_after": initial_date}})

        filters.append({"property": "date", "date": {"on_or_before": today_date}})

        return json.dumps({"sorts": [{"property": "day #", "direction": "ascending"}], "filter": {"and": filters}})

    @classmethod
    def get_date_rows(cls, date: str) -> str:
        return json.dumps({"filter": {"and": [{"property": "date", "date": {"equals": date}}]}})
