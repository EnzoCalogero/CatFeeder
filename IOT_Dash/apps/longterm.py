from datetime import datetime as dt
import dash
import dash_core_components as dcc
import dash_daq as daq
import dash_html_components as html
import pandas as pd

from app import app
################################
## Data seasures Section  ######ß
################################

#all = pd.read_csv('data/improved.csv')
improved = pd.read_csv('data/improved.csv')


#df = all[all.Day == maxDay]

################################
## Data Quality Section   ######
################################

#daily frequency
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

df_=df_[df_.Day > '2019-07-12']

# removing last day
oggi= dt.today().strftime("%Y-%m-%d")
df_=df_[df_.Day < oggi]

df_['CoverRatio'].loc[(df_['CoverRatio'] > 1.0)] = 1.0

minDay = df_['Date'].min()
maxDay = df_['Date'].max()

################################
##     Layout Section     ######
################################

#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

#app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

layout = html.Div(children=[
    html.H1(children='Xander... the Cat!!!!     .....Long term.....'),

    html.Div(children='''
        Long Term Analysis!!!.
    '''),

    dcc.DatePickerRange(
        id='my-date-picker-range',
        min_date_allowed=minDay,
        max_date_allowed=maxDay,
        start_date=minDay,
        end_date=maxDay
    ),
    html.Div(id='output-container-date-picker-range'),
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


# Graph callbacks...

@app.callback(
    dash.dependencies.Output('graph_eaten', 'figure'),
    [dash.dependencies.Input('my-date-picker-range', 'start_date'),
     dash.dependencies.Input('my-date-picker-range', 'end_date')])
def update_output(start_date, end_date):
    print("start date: {}".format(start_date))
    print("end date: {}".format(end_date))


    temp=df_[(df_['Day'] >= start_date) & (df_['Day'] <= end_date)]
    return {
        'data': [{
            'type': 'scatter',
            'y': temp['DailyEaten'],
            'x': temp['Day'],
            'mode': 'lines+markers',
            'name': 'EatenperDay',
        },
        ],
        'layout': {
            'title': "Daily Eaten"
        }
    }


@app.callback(
    dash.dependencies.Output('graph_given', 'figure'),
    [dash.dependencies.Input('my-date-picker-range', 'start_date'),
     dash.dependencies.Input('my-date-picker-range', 'end_date')
     ])
def update_output(start_date, end_date):
    temp = df_[(df_['Day'] >= start_date) & (df_['Day'] <= end_date)]

    return {
        'data': [{
            'type': 'scatter',
            'y': temp['DailyGiven'],
            'x': temp['Day'],
            'mode':  'lines+markers',
            'name': 'GivenperDay',
        },
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
            'mode':  'lines+markers',
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

    return str(round(eatenDay_average,1))


@app.callback(
    dash.dependencies.Output('LED-display_given_average', 'value'),
    [dash.dependencies.Input('my-date-picker-range', 'start_date'),
     dash.dependencies.Input('my-date-picker-range', 'end_date')])
def update_output2(start_date, end_date):
    temp = df_[(df_['Day'] >= start_date) & (df_['Day'] <= end_date)]

    givenDay_average = temp['DailyGiven'].mean()

    return str(round(givenDay_average,1))

if __name__ == '__main__':
    app.run_server(debug=True)

