import pickle
import numpy as np
import src.utils as utils
from datetime import timedelta
from dash import html

# Load data from file
with open('./data/test_data.pkl', 'rb') as f:
    df = pickle.load(f)

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

# Text to be displayed
report = (
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

report = (
    html.H2('Data Analysis'),
    html.H4('Data Check'),
    html.Div(
        f'''{len(dropped)} wrongly formatted datapoints were found within the
        data and will be removed from the analysis.'''
    ),
    html.H4('Outliers'),
    html.Div(
        f'''{len(outliers)} suspicious data points were detected and will be
        treated as outliers.'''
    ),
    html.H4('Points of Interest'),
    html.Div(
        f'''{len(local_mins)} local minima and {len(local_maxs)} local
        maxima were found within the data.'''
    ),
    html.H4('Periodicity'),
    html.Div(
        f'''The data is observed to have a periodicity of about {period // 60}
        hours. We are most likely observing a pattern conditioned by the time
        of the day.'''
    ),
)


data = {
    'df': df,
    'dropped': dropped,
    'time_ints': time_ints,
    'values': values,
    'outliers': outliers,
    'local_mins': local_mins,
    'local_maxs': local_maxs,
    'period': period,
    'extended_times': extended_times,
    'prediction': prediction,
    'times': times,
    'auto_correlation': auto_correlation,
    'report': report,
}
