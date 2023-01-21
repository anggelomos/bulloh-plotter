import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Tuple

import pendulum
import plotly.express as px

from controllers.notion_controller import NotionController
from data.constants.expected_time_metrics import get_expected_time_headers
from data.constants.habits import get_habit_headers
from data.constants.habits_time import get_habit_time_headers
from data.constants.plot_settings.time_chart_settings import TimeChartSettings
from data.constants.time_metrics import get_time_headers, TimeMetrics as TM
from pandas import DataFrame
from utilities.general_utilities import GeneralUtilities as GU


class PlotterController:

    def __init__(self, notion: NotionController):
        self.notion = notion
        self.today_date = pendulum.now()
        self._date_format = "%Y-%m-%d"
        self._plot_list = []

    @property
    def plot_list(self):
        return self._plot_list

    def _time_chart_plotter(self, start_date: str, end_date: str, time_setting: TimeChartSettings) -> str:
        logging.info(f"Plotting {time_setting.value} time chart from {start_date} to {end_date}")
        df = self.notion.get_data_between_dates(start_date, end_date)

        if time_setting == TimeChartSettings.WEEK:
            df["date"] = df["date"].apply(lambda date: datetime.strptime(date, self._date_format).strftime("%A"))

        data_range = [0, 12]
        line_headers = get_time_headers() + get_expected_time_headers()
        line_colors = ["#00b4d8", "#fb5607", "#ef233c", "#5a189a"] * 2
        fig = px.line(df, x="date", y=line_headers,
                      markers=True,
                      range_y=data_range,
                      color_discrete_sequence=line_colors,
                      title=f"{time_setting.value.capitalize()}'s time")

        fig.update_layout(yaxis_title=None, xaxis_title=None)

        initial_range = len(get_time_headers())
        for line_index in range(initial_range, initial_range + len(get_time_headers())):
            fig.data[line_index].line.dash = "dash"
            fig.data[line_index].marker.opacity = 0

        title_index = f"{time_setting.value}_{df.iloc[0][f'{time_setting.value} #']}"
        chart_title = f"charts/{title_index}_time_chart.html"

        fig.write_html(chart_title)
        self._plot_list.append(chart_title)
        return chart_title

    def plot_time_chart(self, time_setting: TimeChartSettings) -> str:
        start_date = self.today_date.start_of(time_setting.value).strftime(self._date_format)
        end_date = self.today_date.end_of(time_setting.value).strftime(self._date_format)
        return self._time_chart_plotter(start_date, end_date, time_setting)

    @staticmethod
    def _get_habits_chart_time_data(df: DataFrame) -> Tuple[dict, int]:
        time_metrics = {}
        time_points = 0
        for metric in get_time_headers():
            amount_hours = GU.round_number(df[metric].sum())
            time_metrics[metric] = amount_hours

            if metric == TM.FOCUS_TIME.value:
                amount_hours *= 2

            time_points += GU.round_number(amount_hours)

        return time_metrics, time_points

    @staticmethod
    def _get_habits_general_data(df: DataFrame) -> Tuple[dict, dict, int]:
        habit_checks = {}
        habit_percentages = {}
        habit_points = 0
        for habit in get_habit_headers():
            habit_checks_amount = int(df[habit].sum())
            habit_checks[habit] = habit_checks_amount
            habit_points = habit_checks_amount
            habit_percentage = GU.round_number(df[habit].value_counts(normalize=True).get(True, 0) * 100)
            habit_percentages[habit] = f"{habit_percentage}%"

        return habit_checks, habit_percentages, habit_points

    @staticmethod
    def _get_habits_time_data(df: DataFrame) -> dict:
        habit_times = {habit: 0 for habit in get_habit_headers()}
        for habit in get_habit_time_headers():
            habit_clean = habit.replace(" time", "")
            if habit_clean in habit_times:
                habit_times[habit_clean] = GU.round_number(df[habit].sum(), 1)
            else:
                habit_keys = [header for header in get_habit_headers() if habit_clean in header]
                for habit_key in habit_keys:
                    habit_times[habit_key] = GU.round_number(df[habit].sum(), 1)

        return habit_times

    def _habits_chart_plotter(self, start_date: str, end_date: str, time_setting: TimeChartSettings) -> str:
        logging.info(f"Plotting {time_setting.value} habits chart from {start_date} to {end_date}")
        df = self.notion.get_data_between_dates(start_date, end_date)

        title_index = f"{time_setting.value}_{df.iloc[0][f'{time_setting.value} #']}"
        chart_title = f"charts/{title_index}_habits_chart.html"
        shutil.copyfile(f"templates/{time_setting.value}_habits_template.html", chart_title)

        expected_points = {TimeChartSettings.WEEK: 150, TimeChartSettings.MONTH: 600}
        time_metrics, time_points = self._get_habits_chart_time_data(df)
        habit_checks, habit_percentages, habit_points = self._get_habits_general_data(df)
        habit_times = self._get_habits_time_data(df)

        overall_points = time_points + habit_points
        time_metrics["overall points"] = f"{GU.round_number(overall_points/expected_points[time_setting]*100)}%"

        file = Path(chart_title)
        text = file.read_text("utf-8").replace("//timeValues", json.dumps(GU.adapt_keys(time_metrics)))
        text = text.replace("//habitTimeValues", json.dumps(GU.adapt_keys(habit_times)))

        if time_setting == TimeChartSettings.MONTH:
            text = text.replace("//habitCheckValues", json.dumps(GU.adapt_keys(habit_checks)))
            text = text.replace("//habitPercentageValues", json.dumps(GU.adapt_keys(habit_percentages)))

        file.write_text(text, "utf-8")
        self._plot_list.append(chart_title)
        return chart_title

    def plot_habits_chart(self, time_setting: TimeChartSettings) -> str:
        start_date = self.today_date.start_of(time_setting.value).strftime(self._date_format)
        end_date = self.today_date.end_of(time_setting.value).strftime(self._date_format)
        return self._habits_chart_plotter(start_date, end_date, time_setting)
