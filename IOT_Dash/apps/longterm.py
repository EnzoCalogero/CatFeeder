from datetime import datetime as dt

import dash
import dash_core_components as dcc
import dash_daq as daq
import dash_html_components as html
import pandas as pd
import numpy as np
#from scipy import signal
from app import app

################################
## Data feasures Section  ######
################################

# all = pd.read_csv('data/improved.csv')
improved = pd.read_csv('data/improved.csv')

# df = all[all.Day == maxDay]

################################
## Data Quality Section   ######
################################

# daily frequency
interval_min = 5.4  # minutes between measurements
total_measure_daily = (60 * 24 / interval_min) - 2

df_ = pd.DataFrame({'Count': improved.groupby('Day')['Hour'].count(),
                    'DailyEaten': improved.groupby('Day')['eaten_cum_Day'].max(),
                    'DailyGiven': improved.groupby('Day')['given_cum_Day'].max(),

                    'Massimo': improved.groupby('Day')['Hour'].max(),
                    'Minimo': improved.groupby('Day')['Hour'].min(),
                    'CoverRatio': improved.groupby('Day')['Hour'].count() / total_measure_daily
                    })
# Dataquality['Day']=Dataquality.index
df_ = df_.reset_index()
df_['Date'] = pd.to_datetime(df_.Day, infer_datetime_format=True)

df_ = df_[df_.Day > '2019-07-12']

# removing last day
oggi = dt.today().strftime("%Y-%m-%d")
df_ = df_[df_.Day < oggi]

df_['CoverRatio'].loc[(df_['CoverRatio'] > 1.0)] = 1.0

minDay = df_['Date'].min()
maxDay = df_['Date'].max()

################################
##   Functions Section    ######
################################
def smoothTriangle(data, degree=5): # added 5 as smoother degree
    triangle = np.concatenate((np.arange(degree + 1), np.arange(degree)[::-1]))  # up then down
    smoothed = []

    for i in range(degree, len(data) - degree * 2):
        point = data[i:i + len(triangle)] * triangle
        smoothed.append(np.sum(point) / np.sum(triangle))
    # Handle boundaries
    smoothed = [smoothed[0]] * int(degree + degree / 2) + smoothed
    while len(smoothed) < len(data):
        smoothed.append(smoothed[-1])
    return smoothed


################################
##     Layout Section     ######
################################

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

layout = html.Div(children=[
    html.H1(children='Xander... the Cat!!!!     .....Long term.....'),

    html.Div(children='''
        Long Term Analysis!!!.
    '''),

    ##################################### Next Line  #############################

    html.Div([
        daq.Knob(
            id='my-knob',
            label="Data Quality, Cover Ratio",
            max=100,
            value=90,
            scale={'start': 0, 'labelInterval': 10, 'interval': 5},
            color={"gradient": True, "ranges": {"red": [0, 50], "yellow": [50, 89], "green": [89, 100]}}
        ),
        html.Div(id='knob-output')
    ], style={'width': '50%', 'display': 'inline-block'}),
    html.Div([
        dcc.DatePickerRange(
            id='my-date-picker-range',
            min_date_allowed=minDay,
            max_date_allowed=maxDay,
            start_date=minDay,
            end_date=maxDay),

        html.Div(id='output-container-date-picker-range'),

    ], style={'width': '50%', 'display': 'inline-block'}),
    ##################################### Next Line  #############################

    html.Div([
        daq.LEDDisplay(
            id='LED-display_eaten_average',
            label="Eaten gr",
            labelPosition='top',
            size=32,
            value=0
        ),
    ], style={'width': '30%', 'display': 'inline-block'}),
    html.Div([
        daq.LEDDisplay(
            id='LED-display_given_average',
            label="Given gr",
            labelPosition='top',
            size=32,
            value=0
        ),

    ], style={'width': '30%', 'display': 'inline-block'}),
    html.Div(id='next line'),
    ####################################### Next Line  #############################

    html.Div([
        dcc.Graph(
            id='graph_given',
        )
    ], style={'width': '30%', 'display': 'inline-block'}),

    html.Div([
        dcc.Graph(
            id='graph_eaten',
        )
    ], style={'width': '30%', 'display': 'inline-block'}),
    html.Div([
        dcc.Graph(
            id='graph_quality',
        )
    ], style={'width': '30%', 'display': 'inline-block'}),
])


# Call backs Data quality...


@app.callback(
    dash.dependencies.Output('knob-output', 'children'),
    [dash.dependencies.Input('my-knob', 'value')])
def update_output(value):
    return 'The Cover Ratio used has to be >= {}.'.format(value)


# Graph callbacks...

@app.callback(
    dash.dependencies.Output('graph_eaten', 'figure'),
    [dash.dependencies.Input('my-date-picker-range', 'start_date'),
     dash.dependencies.Input('my-date-picker-range', 'end_date'),
     dash.dependencies.Input('my-knob', 'value')])
def update_output(start_date, end_date, cover_ratio):
    print("start date: {}".format(start_date))
    print("end date: {}".format(end_date))
    cover_ratio = cover_ratio / 100.
    print(cover_ratio)

    temp = df_[(df_['Day'] >= start_date) & (df_['Day'] <= end_date)]
    temp = temp[temp['CoverRatio'] >= cover_ratio]


    return {
        'data': [{
            'type': 'scatter',
            'y': temp['DailyEaten'],
            'x': temp['Day'],
            'mode': 'lines+markers',
            'name': 'EatenperDay',
        },   #  just added second element... in the list...
            {
                'type': 'scatter',
                'y': smoothTriangle(temp['DailyEaten']),
                'x': temp['Day'],
                'mode': 'lines+markers',
                'name': 'EatenperDay-average',
            }
        ],
        'layout': {
            'title': "Daily Eaten"
        }
    }


@app.callback(
    dash.dependencies.Output('graph_given', 'figure'),
    [dash.dependencies.Input('my-date-picker-range', 'start_date'),
     dash.dependencies.Input('my-date-picker-range', 'end_date'),
     dash.dependencies.Input('my-knob', 'value')
     ])
def update_output(start_date, end_date, cover_ratio):
    cover_ratio = cover_ratio / 100.
    temp = df_[(df_['Day'] >= start_date) & (df_['Day'] <= end_date)]
    temp = temp[temp['CoverRatio'] >= cover_ratio]

    return {
        'data': [{
            'type': 'scatter',
            'y': temp['DailyGiven'],
            'x': temp['Day'],
            'mode': 'lines+markers',
            'name': 'GivenperDay',
        },
            {
                'type': 'scatter',
                'y': smoothTriangle(temp['DailyGiven']),
                'x': temp['Day'],
                'mode': 'lines+markers',
                'name': 'DailyGiven-average',
            }
        ],
        'layout': {
            'title': "Daily Given "
        }
    }


@app.callback(
    dash.dependencies.Output('graph_quality', 'figure'),
    [dash.dependencies.Input('my-date-picker-range', 'start_date'),
     dash.dependencies.Input('my-date-picker-range', 'end_date')
     ])
def update_output1(start_date, end_date):
    temp = df_[(df_['Day'] >= start_date) & (df_['Day'] <= end_date)]
    return {
        'data': [{
            'type': 'scatter',
            'y': temp['CoverRatio'],
            'x': temp['Day'],
            'mode': 'lines+markers',
            'name': 'given_cum_Day',
        },
        ],
        'layout': {
            'title': "Cover Ratio"
        }
    }


## LEDs for bowl statistics

@app.callback(
    dash.dependencies.Output('LED-display_eaten_average', 'value'),
    [dash.dependencies.Input('my-date-picker-range', 'start_date'),
     dash.dependencies.Input('my-date-picker-range', 'end_date')])
def update_output2(start_date, end_date):
    temp = df_[(df_['Day'] >= start_date) & (df_['Day'] <= end_date)]

    eatenDay_average = temp['DailyEaten'].mean()

    return str(round(eatenDay_average, 1))


@app.callback(
    dash.dependencies.Output('LED-display_given_average', 'value'),
    [dash.dependencies.Input('my-date-picker-range', 'start_date'),
     dash.dependencies.Input('my-date-picker-range', 'end_date')])
def update_output2(start_date, end_date):
    temp = df_[(df_['Day'] >= start_date) & (df_['Day'] <= end_date)]

    givenDay_average = temp['DailyGiven'].mean()

    return str(round(givenDay_average, 1))


if __name__ == '__main__':
    app.run_server(debug=True)
