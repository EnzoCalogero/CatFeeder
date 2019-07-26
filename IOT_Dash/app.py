import dash
import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
###added next line....
app.scripts.config.serve_locally = True

app.config.suppress_callback_exceptions = True