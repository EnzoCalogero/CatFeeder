import pandas as pd
from datetime import datetime as dt

import dash_daq as daq
import dash
import dash_core_components as dcc
import dash_html_components as html


all = pd.read_csv('data/improved.csv')

minDay = all['Day'].min()
maxDay = all['Day'].max()

df=all[all.Day == maxDay]


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children='Xander the Cat!!!!'),

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
            value='val'
    ),
html.Div([
    dcc.DatePickerSingle(
        id='my-date-picker-single',
        min_date_allowed=minDay,
        max_date_allowed=maxDay,
        initial_visible_month=maxDay,
        date=maxDay,

    )], style={'width': '30%', 'display': 'inline-block'}),
#    html.Div(id='output-Eaten'),
#    html.Div(id='output-Given'),
html.Div([
            daq.LEDDisplay(
                id='LED-display_given',
                label="Given gr",
                labelPosition='top',
                size=32,
                value=0
                ),
], style={'width': '30%', 'display': 'inline-block'}),
html.Div([
            daq.LEDDisplay(
                id='LED-display_eaten',
                label="Eaten gr",
                labelPosition='top',
                size=32,
                value=0
                ),

  ], style={'width': '30%', 'display': 'inline-block'}),
    dcc.Graph(
        id='graph_01',

    )
])


@app.callback(
    dash.dependencies.Output('graph_01', 'figure'),
    [dash.dependencies.Input('variable-dropdown', 'value'),
     dash.dependencies.Input('my-date-picker-single', 'date')
     ])
def update_output(value,date):

    df = all[all.Day == date]
    return {
            'data': [{
                'type': 'scatter',
                'y': df[value],
                'x': df['Hour'],
            }
            ],
            'layout': {
                'title': date
            }
        }


@app.callback(
    dash.dependencies.Output('LED-display_eaten', 'value'),
    [dash.dependencies.Input('my-date-picker-single', 'date')])
def update_output(date):
    string_prefix = 'Total Given for: '

    df = all[all.Day == date]
    eatenDay = df.eaten_cum_Day.max()

    return  str(eatenDay)


@app.callback(
    dash.dependencies.Output('LED-display_given', 'value'),
    [dash.dependencies.Input('my-date-picker-single', 'date')])
def update_output(date):
    string_prefix = 'Total Given for: '

    df = all[all.Day == date]
    givenDay = df.given_cum_Day.max()

    return  str(givenDay)

if __name__ == '__main__':

    app.run_server(debug=True)