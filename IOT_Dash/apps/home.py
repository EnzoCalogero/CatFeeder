import flask
from dash.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc
import base64
import os

from app import app
colors = {
    'background': '#111111',
    'text': '#253471'}
# Dash Variables


layout = html.Div([
    html.Div([
        html.Div([

            html.H2(
                children="Dashboard Menu",
                id="h2_come",
                style={
                    'textAlign': 'center',
                    'text': colors['text'],
                    'font-family':'Glacial Indifference',
                    'color': colors['text'],
                    'bgcolor': colors['background']}
            )
        ], className='ten columns'),

    ], className="row"),
    ###########################################################################################################
    html.Div([
        html.P(id='intermediate-value_home', style={'float': 'right'}),
    ], className="row"),
    html.Div([
        html.P(dcc.Link('daily', href='/daily'), ),
    ]),
    html.Div([
        html.P(dcc.Link('longterm', href='/longterm'), ),
    ])
], style={
    'font-family': 'Glacial Indifference',
    'padding': '0px 10px 15px 10px',
    'marginLeft': 'auto',
    'marginRight': 'auto',
    'width': '160vh',
    'color': colors['text'],
    'boxShadow': '0px 0px 5px 5px rgba(37,52,113,0.4)'}
)