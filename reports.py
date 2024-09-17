from datetime import datetime
import re
from dataclasses import dataclass

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np


SHOWS_RE = re.compile(
    r"^on (?P<date>\d+\.\d+\.\d+) at (?P<time>\d+:\d+:\d+) shows (?P<show_time>\d+:\d+:\d+(\.\d+)?).*"
)
RESET_RE = re.compile(r"^on (?P<date>\d+\.\d+\.\d+) reset to (?P<time>\d+:\d+).*")


@dataclass
class Report:
    time: datetime
    shows: datetime
    is_reset: bool
    
    @property
    def err(self) -> float:
        return (self.shows - self.time).total_seconds()

    def __repr__(self):
        return f"{self.time} -> {self.shows:%H:%M:%S.%f} " + (
            f"(dev={self.err:+.2f})" if not self.is_reset else "[RESET]"
        )

    @classmethod
    def from_line(cls, line: str) -> "Report":
        """
        Generate a Report object from a line of the report file.

        Examples:
        "on 01.01.21 at 12:30:00 shows 12:30:15" would result in a Report object
        "on 01.01.21 reset to 12:30" would result in a Report object with is_reset=True
        """
        if match := SHOWS_RE.match(line):
            time = datetime.strptime(
                match["date"] + " " + match["time"], "%d.%m.%y %H:%M:%S"
            )
            for fmt in ["%H:%M:%S", "%H:%M:%S.%f"]:
                try:
                    shows = datetime.strptime(
                        match["date"] + " " + match["show_time"], "%d.%m.%y " + fmt
                    )
                except ValueError:
                    pass
                else:
                    return cls(time, shows, False)
        if match := RESET_RE.match(line):
            time = datetime.strptime(
                match["date"] + " " + match["time"], "%d.%m.%y %H:%M"
            )
            return cls(time, time, True)
        raise ValueError(f"Invalid line: {line}")

    def __sub__(self, other: "Report") -> float:
        """
        Calculates the average deviation in seconds per day between two reports.
        """
        return (
            self.err
            / (self.time - other.time).total_seconds()
            * 86400
        )


def get_dev_xy(subreport: list[Report]) -> tuple[list[datetime], list[float]]:
    times = [r.time for r in subreport[1:]]
    devs = [r - subreport[0] for r in subreport[1:]]
    return times, devs


def get_figs(subreports: list[list[Report]], with_immediate_deviation: bool = True) -> tuple[go.Figure, go.Figure]:
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    x = []
    y = []
    for subrep in subreports:
        if len(subrep) == 1:
            continue
        x.extend([r.time for r in subrep])
        y.extend([r.err for r in subrep])
    fig.add_trace(
        go.Scatter(
            x=x,
            y=y,
            mode="markers",
            name="errors",
        ),
        secondary_y=False,
    )

    # ... show the best fit lines per group
    x_best_lines: list[datetime | None] = []
    y_best_lines: list[float | None] = []

    x_daily_devs: list[datetime] = []
    y_daily_devs: list[float] = []

    for subrep in subreports:
        if len(subrep) == 1:
            continue
        x_unix = [r.time.timestamp() for r in subrep]
        y_errs = [r.err for r in subrep]
        params = np.polyfit(x_unix, y_errs, 1)
        fit_values = np.polyval(params, x_unix)
        x_best_lines.extend(r.time for r in subrep)
        y_best_lines.extend(fit_values)
        fig.add_annotation(
            x=x_best_lines[-1],
            y=y_best_lines[-1],
            text=f"{params[0]*86400:+.2f} s/day",
            showarrow=True,
            xanchor="right",
        )
        x_daily_devs.append(subrep[-1].time)
        y_daily_devs.append(params[0] * 86400)
        x_best_lines.append(None)
        y_best_lines.append(None)
    fig.add_trace(
        go.Scatter(
            x=x_best_lines,
            y=y_best_lines,
            name="best lines",
            mode="lines",
            marker=dict(color="orange"),
            line=dict(width=0.7, dash="dot"),
        ),
        secondary_y=False,
    )

    # ... show the deviation (in seconds per day) over time
    times_all, devs_all = [], []
    for subrep in subreports:
        if len(subrep) == 1:
            continue
        times, devs = get_dev_xy(subrep)
        times_all.extend(times)
        devs_all.extend(devs)
        times_all.append(None)
        devs_all.append(None)
    if with_immediate_deviation:
        fig.add_trace(
            go.Scatter(
                x=times_all,
                y=devs_all,
                name="deviation",
                mode="lines+markers",
                marker=dict(color="white"),
                line=dict(width=1.5, dash="dash"),
                line_shape="spline",
                connectgaps=False,
            ),
            secondary_y=True,
        )

    fig.update_layout(
        template="plotly_dark",
        title="Errors and deviations over time",
        xaxis_title="Time",
    )
    fig.update_layout(legend=dict(y=1.1, orientation="h"))
    fig.update_yaxes(title_text="Accumulated error (s)", secondary_y=False)
    fig.update_yaxes(title_text="Deviation (s/day)", secondary_y=True, showgrid=False)

    fig_dev = go.Figure()
    fig_dev.add_trace(
        go.Scatter(
            x=x_daily_devs,
            y=y_daily_devs,
            mode="lines+markers",
            marker=dict(size=10),
            line=dict(width=1.5, dash="dash"),
            line_shape="spline",
            name="daily deviations",
        )
    )
    fig_dev.update_layout(
        template="plotly_dark",
        title="Daily deviations",
        xaxis_title="Time",
        yaxis_title="Deviation (s/day)",
    )

    return fig, fig_dev


def date_of_deviation(
    subreports: list[list[Report]],
    deviation_sec: float,
    force_choose_full_subreport: bool = False,
) -> datetime:
    start_date = subreports[-1][0].time.timestamp()
    if not force_choose_full_subreport and len(subreports[-1]) > 1:
        subreport = subreports[-1]
    else:
        subreport = subreports[-2]
        print("Using the second last subreport to calculate the deviation.")
    x_unix = [r.time.timestamp() for r in subreport]
    y_errs = [r.err for r in subreport]
    params = np.polyfit(x_unix, y_errs, 1)
    return datetime.fromtimestamp(start_date + (deviation_sec / params[0]))
