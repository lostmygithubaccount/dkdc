# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as dhc
import plotly.graph_objs as go

import pandas as pd

LOG_FILE = 'C:/users/aksha/downloads/azureml.log'

with open(LOG_FILE, 'rt') as log_file:
    log_data = pd.DataFrame({
        'time': log_file.readlines()
    })

log_data[['time', 'source', 'level', 'message']] = log_data['time'].str.split('|', n=4, expand=True)
log_data['source'] = log_data['source'].astype('category')
log_data['level'] = log_data['level'].astype('category')
log_data['time'] = pd.to_datetime(log_data['time'])  # TIMEZONEEEEEEEE!!!!!!!!!!!!! :(
log_data.set_index('time', inplace=True)
# print(log_data.index)
start_time = log_data.index.min().timestamp()
end_time = log_data.index.max().timestamp()
all_levels = log_data['level'].cat.categories.tolist()
all_sources = log_data['source'].cat.categories.tolist()

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

app.layout = dhc.Div(children=[
    dhc.H1(
        children='Hello Dash',
        style={
            'textAlign': 'center'
        }
    ),

    dhc.Div(dcc.RangeSlider(
        id='log-time-range',
        min=start_time,
        max=end_time,
        step=1,  # 10 seconds
        value=[start_time, end_time],
        marks={
            ts.timestamp(): str(ts) for ts in pd.cut(log_data.index, bins=10).categories.mid
        },
        allowCross=False
    ), style={'margin-top': 20}),

    dhc.Div(dcc.Dropdown(
        id='event-sources',
        options=[
            {'label': source, 'value': source} for source in sorted(all_sources)
        ],
        value=all_sources,
        multi=True
    ), style={'margin-top': 20}),

    dhc.Div(dcc.Dropdown(
        id='event-levels',
        options=[
            {'label': level, 'value': level} for level in all_levels
        ],
        value=all_levels,
        multi=True
    ), style={'margin-top': 20}),

    dcc.Graph(
        id='event-timeline-data'
    ),
])


@app.callback(
    dash.dependencies.Output('event-timeline-data', 'figure'),
    [
        dash.dependencies.Input('log-time-range', 'value'),
        dash.dependencies.Input('event-sources', 'value'),
        dash.dependencies.Input('event-levels', 'value')
    ])
def uber_update_function(times, sources, levels):
    low = pd.Timestamp(times[0] - 2, unit='s')  # , tz='US/Eastern')
    high = pd.Timestamp(times[1] + 2, unit='s')  # , tz='US/Eastern')

    print("Showing from {} to {}".format(low, high))
    print("Have {} to {}".format(log_data.index.min(), log_data.index.max()))

    timedata = log_data.loc[low:high]

    print("Only showing {} logs from {}".format(levels, sources))
    ret = timedata.loc[timedata['source'].isin(sources) & timedata['level'].isin(levels)]

    print(ret.head())
    return {
        'data': [go.Table(
            columnwidth=[15, 15, 5, 65],
            header=dict(values=['time'] + list(ret.columns),
                        fill=dict(color='#C2D4FF'),
                        align=['left'] * 5),
            cells=dict(values=[ret.index, ret.source, ret.level, ret.message],
                       fill=dict(color='#F5F8FF'),
                       align=['left'] * 5)
        )]
    }


if __name__ == '__main__':
    app.run_server(debug=True)
