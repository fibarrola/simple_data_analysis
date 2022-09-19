# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
from datetime import datetime
from src.process_data import data

corr_fig = go.Figure()
corr_fig.add_trace(
    go.Scatter(x=data['times'], y=data['auto_correlation'], name='Autocorrelation')
)
corr_fig.update_layout(
    title='Autocorrelation', height=300, margin=dict(l=20, r=20, t=50, b=20)
)


# Generate graphics
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets=external_stylesheets)

my_marks = {}
for ind in range(len(data['df'])):
    tiempo = datetime.strftime(data['df']['Timestamps'][ind], '%H%M')
    if tiempo == '0000' or tiempo == '1200':
        my_marks[data['time_ints'][ind]] = datetime.strftime(
            data['df']['Timestamps'][ind], '%Y-%m-%d, %H:%M'
        )

app.layout = html.Div(
    [
        html.H1(children='Data Visualization', style={'padding-left': 40}),
        html.P(
            children='''
            Analysis of unknown data. The datapoints considered to be outliers are
            highlighted and the overall trend is shown, along with a prediction
            for the next two hours. This is a blind analysis, given that the origin of the data
            is unknown, as well as what the displayed values represent.
        ''',
            style={'padding-left': 40},
        ),
        html.Div(
            children=[
                html.H4(
                    children=['Visualization of Data from file'],
                    style={'padding-left': 40, 'padding-top': 40},
                ),
                html.P(
                    children=['(Click and drag to zoom. Double click to zoom back).'],
                    style={'padding-left': 40},
                ),
                dcc.Graph(id='graph-with-slider'),
            ]
        ),
        html.Div(
            children=[
                dcc.RangeSlider(
                    id='year-slider',
                    min=data['time_ints'][0],
                    max=data['time_ints'][-1],
                    marks=my_marks,
                    step=600,
                    value=[data['time_ints'][0], data['time_ints'][-1]],
                ),
            ],
            style={'padding-left': '5%', 'padding-right': '3%'},
        ),
        dcc.Graph(id='autocorrelation', figure=corr_fig),
        html.Div(
            children=data['report'],
            style={'padding-left': 40, 'padding-top': 40, 'padding-bottom': 40},
        ),
    ]
)


@app.callback(Output('graph-with-slider', 'figure'), Input('year-slider', 'value'))
def update_figure(date):
    to_drop = []
    for ind in range(len(data['df'])):
        if data['time_ints'][ind] < date[0]:
            to_drop.append(ind)
        elif data['time_ints'][ind] > date[1]:
            to_drop.append(ind)
    filtered_df = data['df'].drop(to_drop)

    filtered_outliers = []
    for x in data['outliers']:
        if date[0] < data['time_ints'][x] < date[1]:
            filtered_outliers.append(x)

    fig = go.Figure()
    fig.add_trace(
        go.Bar(x=filtered_df["Timestamps"], y=filtered_df["Values"], name='Values')
    )

    fig.add_trace(
        go.Scatter(
            x=filtered_df["Timestamps"][filtered_outliers],
            y=[data['values'][k] for k in filtered_outliers],
            mode='markers',
            name='Outliers',
        )
    )

    fig.add_trace(
        go.Scatter(
            x=data['extended_times'], y=data['prediction'], mode='lines', name='Trend'
        )
    )

    fig.update_layout(
        legend={'yanchor': "top", 'y': 0.99, 'xanchor': "right", 'x': 0.99},
        margin=dict(l=20, r=20, t=20, b=50),
        height=400,
    )

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
