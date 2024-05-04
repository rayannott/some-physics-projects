from datetime import datetime
import re
import pathlib
from dataclasses import dataclass, field

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np


SHOWS_RE = re.compile(r'^on (?P<date>\d+\.\d+\.\d+) at (?P<time>\d+:\d+:\d+) shows (?P<show_time>\d+:\d+:\d+(\.\d+)?).*')
RESET_RE = re.compile(r'^on (?P<date>\d+\.\d+\.\d+) reset to (?P<time>\d+:\d+).*')


@dataclass
class Report:
    time: datetime
    shows: datetime
    is_reset: bool
    err: float = field(init=False)

    def __post_init__(self):
        self.err = (self.shows - self.time).total_seconds()

    def __repr__(self):
        return f'{self.time} -> {self.shows:%H:%M:%S.%f} ' + (f'(dev={self.err:+.2f})' if not self.is_reset else '[RESET]')
    
    @staticmethod
    def from_line(line: str) -> 'Report':
        if (match:=SHOWS_RE.match(line)):
            time = datetime.strptime(match['date'] + ' ' + match['time'], '%d.%m.%y %H:%M:%S')
            for fmt in ['%H:%M:%S', '%H:%M:%S.%f']:
                try:
                    shows = datetime.strptime(match['date'] + ' ' + match['show_time'], '%d.%m.%y ' + fmt)
                except ValueError:
                    pass
                else:
                    return Report(time, shows, False)
        if (match:=RESET_RE.match(line)):
            time = datetime.strptime(match['date'] + ' ' + match['time'], '%d.%m.%y %H:%M')
            return Report(time, time, True)
        raise ValueError(f'Invalid line: {line}')

    def __sub__(self, other: 'Report') -> float:
        return (self.shows - self.time).total_seconds() / (self.time - other.time).total_seconds() * 86400


def get_dev_xy(subreport: list[Report]) -> tuple[list[datetime], list[float]]:
    times = [r.time for r in subreport[1:]]
    devs = [r - subreport[0] for r in subreport[1:]]
    return times, devs


def get_fig(subreports: list[list[Report]]) -> go.Figure:
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    # split the reports on the resets and...
    # ... show the errors plot per report group
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
            mode='markers', 
            name='errors',
        ),
        secondary_y=False
    )

    # ... show the best fit lines per group
    x_best_lines = []; y_best_lines = []
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
            text=f'{params[0]*86400:+.2f} s/day',
            showarrow=True,
            xanchor="right"
        )
        x_best_lines.append(None); y_best_lines.append(None)
    fig.add_trace(
        go.Scatter(
            x=x_best_lines,
            y=y_best_lines,
            name='best lines',
            mode='lines', 
            marker=dict(color='orange'),
            line=dict(width=0.7, dash='dot'),
        ), 
        secondary_y=False
    )

    # ... show the deviation (in seconds per day) over time
    times_all, devs_all = [], []
    for subrep in subreports:
        if len(subrep) == 1:
            continue
        times, devs = get_dev_xy(subrep)
        times_all.extend(times)
        devs_all.extend(devs)
        times_all.append(None); devs_all.append(None)
    fig.add_trace(
        go.Scatter(
            x=times_all, 
            y=devs_all, 
            name='deviation',
            mode='lines+markers', 
            marker=dict(color='white'),
            line=dict(width=1.5, dash='dash'),
            line_shape='spline',
            connectgaps=False
        ), 
        secondary_y=True
    )

    fig.update_layout(template='plotly_dark', title='Errors and deviations over time', xaxis_title='Time')
    fig.update_layout(legend=dict(y=1.1, orientation='h'))
    fig.update_yaxes(title_text='Accumulated error (s)', secondary_y=False)
    fig.update_yaxes(title_text='Deviation (s/day)', secondary_y=True, showgrid=False)
    return fig