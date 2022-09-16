# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pickle
from datetime import datetime, timedelta
import numpy as np
from src import utils


# Load data from file
file = open('./data/test_data.pkl', 'rb')
df = pickle.load(file)
file.close()


# Delete incorrect rows
df, dropped = utils.clear_timestamps(df)


# Transform timestamps to a series of integers for performing outlier analysis
time_ints = utils.tstamps_to_ints(df)


# Find outliers and remove from values
values = np.array(df['Values'])
outliers, values_cleared = utils.get_outliers(time_ints, values)


# Get global tendency and find relevant points
filtered_values, local_mins, local_maxs = utils.filter_values(values_cleared, 0.005)
prediction = utils.sillyPredict(filtered_values)
# df['Trend'] = filtered_values
extended_times = list(df["Timestamps"])
for k in range(len(prediction) - len(df["Timestamps"])):
    extended_times.append(extended_times[-1] + timedelta(seconds=60))


# Periodicity analysis
auto_correlation, period = utils.get_period(filtered_values)
period = df['Timestamps'][period] - df['Timestamps'][0]
times = [
    (x - df["Timestamps"][0]).days * 24 + (x - df["Timestamps"][0]).seconds / 3600
    for x in df['Timestamps']
]
corr_fig = go.Figure()
corr_fig.add_trace(go.Scatter(x=times, y=auto_correlation, name='Autocorrelation'))
corr_fig.update_layout(title='Autocorrelation')


# Text to be displayed
markdown_text = (
    '''
        ### Data Analysis \n
        Data Check:
    '''
    + str(len(dropped))
    + '''
        wrongly formatted datapoints were found within the
        data and will be removed from the analysis.\n\n
        Outliers:
    '''
    + str(len(outliers))
    + '''
        suspicious data points were detected and will be
        treated as outliers. \n\n
        Points of interest:
    '''
    + str(len(local_mins))
    + ''' local minima and '''
    + str(len(local_maxs))
    + '''
        local maxima were found within the data. \n\n
        Periodicity:
        The data is observed to have a periodicity of about '''
    + str(period // 60)
    + ''' hours.
'''
)


# Generate graphics
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets=external_stylesheets)

my_marks = {}
for ind in range(len(df)):
    tiempo = datetime.strftime(df['Timestamps'][ind], '%H%M')
    if tiempo == '0000' or tiempo == '1200':
        my_marks[time_ints[ind]] = datetime.strftime(
            df['Timestamps'][ind], '%Y-%m-%d, %H:%M'
        )

app.layout = html.Div(
    [
        html.H1(children='Data Visualization'),
        html.Div(
            children='''
        Analysis of unknown data. The datapoints considered to be outliers are
        highlighted and the overall trend is shown, along with a prediction
        for the next two hours.
    '''
        ),
        dcc.Graph(id='graph-with-slider'),
        dcc.RangeSlider(
            id='year-slider',
            min=time_ints[0],
            max=time_ints[-1],
            marks=my_marks,
            step=600,
            value=[time_ints[0], time_ints[-1]],
        ),
        dcc.Graph(id='autocorrelation', figure=corr_fig),
        dcc.Markdown(children=markdown_text),
    ]
)


@app.callback(Output('graph-with-slider', 'figure'), Input('year-slider', 'value'))
def update_figure(date):
    print(date)
    to_drop = []
    for ind in range(len(df)):
        if time_ints[ind] < date[0]:
            to_drop.append(ind)
        elif time_ints[ind] > date[1]:
            to_drop.append(ind)
    filtered_df = df.drop(to_drop)

    filtered_outliers = []
    for x in outliers:
        if date[0] < time_ints[x] < date[1]:
            filtered_outliers.append(x)

    fig = go.Figure()
    fig.update_layout(title='Visualization of data from file')
    fig.add_trace(
        go.Bar(x=filtered_df["Timestamps"], y=filtered_df["Values"], name='Values')
    )

    fig.add_trace(
        go.Scatter(
            x=filtered_df["Timestamps"][filtered_outliers],
            y=[values[k] for k in filtered_outliers],
            mode='markers',
            name='Outliers',
        )
    )

    # fig.add_trace(go.Scatter(x=filtered_df["Timestamps"], y=filtered_df["Trend"],
    #                           mode='lines', name='Trend'))
    fig.add_trace(
        go.Scatter(x=extended_times, y=prediction, mode='lines', name='Trend')
    )

    fig.update_layout()

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
