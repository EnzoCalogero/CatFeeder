import dash
import dash_core_components as dcc
import dash_daq as daq
import dash_html_components as html
import pandas as pd

from app import app
################################
## Data seasures Section  ######ß
################################

all = pd.read_csv('data/improved.csv')

minDay = all['Day'].min()
maxDay = all['Day'].max()

df = all[all.Day == maxDay]
print(all.head())
################################
## Data Quality Section   ######
################################

#daily frequency
interval_min = 5.4  # minutes between measurements
total_measure_daily = (60 * 24 / interval_min) - 2

DataQuality = pd.DataFrame({'Count': all.groupby('Day')['Hour'].count(),
                            'Massimo': all.groupby('Day')['Hour'].max(),
                            'Minimo': all.groupby('Day')['Hour'].min(),
                            'CoverRatio': all.groupby('Day')['Hour'].count() / total_measure_daily
                            })
DataQuality = DataQuality.reset_index()


# Quick check on data for the day on the dataset
def Min_quality_data(day):
    if (all[all.Dayv==day]).empty:
        return False
    return True


################################
##     Layout Section     ######
################################

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children='Xander... the Cat!!!!'),

    html.Div(children='''
        Xander Eating!!!.
    '''),
    dcc.Dropdown(
        id='variable-dropdown',
        options=[
            {'label': 'Level', 'value': 'val'},
            {'label': 'Eaten', 'value': 'eaten'},
            {'label': 'Given', 'value': 'given'},
            {'label': 'Eaten Cumulative', 'value': 'eaten_cum_Day'},
            {'label': 'Given Cumulative', 'value': 'given_cum_Day'}
        ],
        multi=False,
        value='val'
    ),
    ####################################### Next Line  #############################

    html.Div([
        dcc.DatePickerSingle(
            id='my-date-picker-single',
            min_date_allowed=minDay,
            max_date_allowed=maxDay,
            initial_visible_month=maxDay,
            date=maxDay,

        )], style={'width': '30%', 'display': 'inline-block'}),
    html.Div([
        daq.LEDDisplay(
            id='LED-display_eaten',
            label="Eaten gr",
            labelPosition='top',
            size=32,
            value=0
        ),
    ], style={'width': '30%', 'display': 'inline-block'}),
    html.Div([
        daq.LEDDisplay(
            id='LED-display_given',
            label="Given gr",
            labelPosition='top',
            size=32,
            value=0
        ),

    ], style={'width': '30%', 'display': 'inline-block'}),
    ####################################### Next Line  #############################
    html.Div([
        dcc.Graph(
            id='graph_01',

        )
    ], style={'width': '30%', 'display': 'inline-block'}),

    html.Div([
        dcc.Graph(
            id='graph_cumulative',

        )
    ], style={'width': '30%', 'display': 'inline-block'}),

    html.Div([
        dcc.Graph(
            id='graph_minute',

        )
    ], style={'width': '30%', 'display': 'inline-block'}),

    ####################################### Next Line  #############################
    html.Div(children='''
       Data Quality Review.
   '''),
    ####################################### Next Line  #############################

    html.Div([
        daq.GraduatedBar(
            id='GraduatedBar-quality_count',
            color={"gradient":True, "ranges": {"green": [90, 100],"yellow": [70, 80],"red": [0, 60]}},
            showCurrentValue=True,
            max=100,
            value=10
        )
    ], style={'width': '20%', 'display': 'inline-block'}),
    html.Div([
        daq.LEDDisplay(
            id='LED-quality_count',
            labelPosition='top',
            label='Cover daily measures',
            size=32,
            value=90
        ),
    ], style={'width': '10%', 'display': 'inline-block'}),

])


@app.callback(
    dash.dependencies.Output('graph_01', 'figure'),
    [dash.dependencies.Input('variable-dropdown', 'value'),
     dash.dependencies.Input('my-date-picker-single', 'date')
     ])
def update_output(value, date):
    df = all[all.Day == date]
    return {
        'data': [{
            'type': 'scatter',
            'y': df[value],
            'x': df['Hour'],
            'mode':  'lines+markers',
            'name': value,
        },

        ],
        'layout': {
            'title': "Level on the {}".format(date)
        }
    }


@app.callback(
    dash.dependencies.Output('graph_cumulative', 'figure'),
    [dash.dependencies.Input('my-date-picker-single', 'date')
     ])
def update_output(date):

    df = all[all.Day == date]
    return {
        'data': [{
            'type': 'scatter',
            'y': df['eaten_cum_Day'],
            'x': df['Hour'],
            'mode':  'lines+markers',
            'name': 'Eaten Cumulative Day',
        },
            {
                'type': 'scatter',
                'y': df['eaten'],
                'x': df['Hour'],
                'mode': 'lines+markers',
                'name': 'Eaten',
            }
        ],
        'layout': {
            'title': "Eaten on the {}".format(date)
        }
    }


@app.callback(
    dash.dependencies.Output('graph_minute', 'figure'),
    [dash.dependencies.Input('my-date-picker-single', 'date')
     ])
def update_output1(date):
    print(date)

    df = all[all.Day == date]
    return {
        'data': [{
            'type': 'scatter',
            'y': df['given_cum_Day'],
            'x': df['Hour'],
            'mode':  'lines+markers',
            'name': 'given_cum_Day',
        },
            {
                'type': 'scatter',
                'y': df['given'],
                'x': df['Hour'],
                'mode': 'lines+markers',
                'name': 'Given',
            }
        ],
        'layout': {
            'title': "Given on the {}".format(date)
        }
    }

## LEDs for bowl statistics

@app.callback(
    dash.dependencies.Output('LED-display_eaten', 'value'),
    [dash.dependencies.Input('my-date-picker-single', 'date')])
def update_output2(date):

    df = all[all.Day == date]
    eatenDay = df.eaten_cum_Day.max()

    return str(eatenDay)


@app.callback(
    dash.dependencies.Output('LED-display_given', 'value'),
    [dash.dependencies.Input('my-date-picker-single', 'date')])
def update_output3(date):
    df = all[all.Day == date]
    givenDay = df.given_cum_Day.max()

    return str(givenDay)

## LEDs for data Quality statistics

@app.callback(
    dash.dependencies.Output('LED-quality_count', 'value'),
    [dash.dependencies.Input('my-date-picker-single', 'date')])
def update_output4(date):
    EntryNumber = DataQuality[DataQuality.Day == date]
    EntryNumber = EntryNumber[['Count']]
    return str(EntryNumber.Count.iloc[0])


@app.callback(
    dash.dependencies.Output('GraduatedBar-quality_count', 'value'),
    [dash.dependencies.Input('my-date-picker-single', 'date')])
def update_output5(date):

    CoverRatio = DataQuality[DataQuality.Day == date]
    CoverRatio = CoverRatio[['CoverRatio']]
    CoverRatio = (CoverRatio.CoverRatio.iloc[0]*100).astype(int)

    return CoverRatio

if __name__ == '__main__':
    app.run_server(debug=True)

