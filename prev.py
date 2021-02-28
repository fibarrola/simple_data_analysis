# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""


import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import pickle
from datetime import datetime
import numpy as np

from importlib import reload  
from src import utils

import matplotlib.pyplot as plt



# Load data from file
file = open('./data/test_data.pkl', 'rb')
df = pickle.load(file)
file.close()

# Delete incorrect rows
df = utils.clear_timestamps(df)

# Transform timestamps to a series of integers for performing outlier analysis
time_ints = utils.tstamps_to_ints(df)

# Find outliers and remove from values
values = np.array(df['Values'])
outliers, values_cleared = utils.get_outliers(time_ints, values)

# Get global tendency and find relevant points
filtered_values, local_mins, local_maxs = utils.filter_values(values_cleared, 0.005)
    
df['Trend'] = filtered_values


# plt.plot(time_ints,values,time_ints,outliers)
# plt.show()

# plt.plot(time_ints,values,time_ints,filtered_values)
# plt.show()

# plt.plot(neg_of)
# plt.show()

# plt.plot(second_der)
# plt.show()


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)



my_marks = {}
for ind in range(len(df)):
    tiempo = datetime.strftime(df['Timestamps'][ind],'%H%M')
    if tiempo=='0000' or tiempo=='1200':
        my_marks[time_ints[ind]] = datetime.strftime(df['Timestamps'][ind],'%Y-%m-%d, %H:%M')
             
app.layout = html.Div([
    dcc.Graph(id='graph-with-slider'),
        dcc.RangeSlider(
            id='year-slider',
            min=time_ints[0],
            max=time_ints[-1],
            marks = my_marks,
            step = 600,
            value=[time_ints[0],time_ints[-1]]
        )  
])  
             
@app.callback(
    Output('graph-with-slider', 'figure'),
    Input('year-slider', 'value'))

def update_figure(date):
    to_drop = []
    for ind in range(len(df)):
        if time_ints[ind] < date[0]:
            to_drop.append(ind)
        elif time_ints[ind] > date[1]:
            to_drop.append(ind)
    filtered_df = df.drop(to_drop)
    
    fig = px.bar(filtered_df, x="Timestamps", y="Values")
    # fig.add_trace(px.line(filtered_df, x="Timestamps", y="Trend"))
    fig.update_layout(transition_duration=500)

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
    # app.run_server(debug=False)
