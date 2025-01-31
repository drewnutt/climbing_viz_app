#!/usr/bin/env python
import os
import requests
import plotly.express as px
import plotly.graph_objects as go
import dash
from dash import dcc, html, Input, Output, State
from datetime import date
import pandas as pd
import base64
import io
from grades import GRADES
from figures import generate_pyramid, generate_scatter


if os.getenv('HOST'):
    del os.environ['HOST']


# Plotly configuration
config = {'displayModeBar': False}

# Create a Dash app
app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])

# Define the layout of the app
app.layout = html.Div([
    html.Div(children=['Upload your climbing ticks.csv to view your Route Pyramid!'],
             style={'fontSize': '18px'}),
    dcc.Upload(
        id='upload-data',
        children=html.Div(['Drag and Drop or ',html.A('Select Files')]),
        style={'width': '74vw',
               'height': '30px',
               'lineHeight': '30px',
               'borderWidth': '1px',
               'borderStyle': 'dashed',
               'borderRadius': '5px',
               'textAlign': 'center',
               'margin': '10px'},
               multiple=False),
    html.Div(children=['Enter your Mountain Project profile URL to download your ticks.csv'],
             style={'fontSize': '18px'}),
    dcc.Input(id='mp-url', type='url', placeholder='https://www.mountainproject.com/user/USERNUM/USER-NAME',
              style={'width': '75vw'}),
    # add a button to download ticks.csv
    html.Button('Download', id='download-button', n_clicks=0),
    html.Div(children=[
            html.Div(children=[html.H4(children='Route Type'), 
                        dcc.RadioItems(['Rope','Boulder'],'Rope',id='route-type',
                                style={'width':'75vw'})],
                        style={'width':'75vw', 'flex-basis':'10rem'}),
            html.Div(children=[html.H4(children='Rope Type'),
                    dcc.Checklist(['Sport', 'Trad', 'TR'], ['Sport'],
                                id='rope-type',style={'width': '75vw'})],
                    style={'width':'75vw','flex-basis':'10rem'},id='rope-div'),
            ], style={'display':'flex','flex-direction':'row'}),

    dcc.Dropdown(['Onsight', 'Flash', 'Redpoint', 'Pinkpoint', 'Fell/Hung', 'N/A'],
                 ['Onsight', 'Flash', 'Redpoint'],
                 multi=True, searchable=False, id='send-dropdown',
                 style={'width':'75vw'}),
    dcc.DatePickerRange(min_date_allowed=date(2010, 1, 1),
                 max_date_allowed=date(2025, 1, 1), start_date=date(2022, 1, 1), end_date=date.today(),
                 id='date-range', style={'width':'75vw'}),
    html.Div(children=['Max Grade:',
        dcc.Dropdown(options=[{'label': value, 'value': key} for key,value in GRADES.items() if value.startswith('5')], value=8500, id='max-dropdown',
                                    searchable=False, clearable=False)],
            style={'width':'30vw'}),
    html.Div(children=[dcc.Checklist(['Include Multipitch Routes'],['Include Multipitch Routes'],
                  id='multi-filter'),], id='multi-div', style={'width':'75vw'}),
    # make a new Div that has a checklist for combining +,-,and normal boulder grades
    html.Div(children=[dcc.Checklist(['Combine -,+, and normal grades'],['Combine -,+, and normal grades'],
                  id='boulder-filter'),], id='boulder-div', hidden=True, style={'width':'75vw'}),
    dcc.Tabs([
        dcc.Tab(label='Pyramid', value="tab-pyramid"),
        dcc.Tab(label='Scatter', value="tab-scatter"),
    ], id='tabs', value='tab-pyramid'),
    html.Div(id='tabs-content-graph', style={'width':'75vw'}, children=[dcc.Graph(figure=go.Figure(), config=config, id='graph-display')]),# ,dcc.Checklist(['Show Attempts'], ['Show Attempts'], id='attempts-filter')
    # add a checkbox to toggle showing of attempts
    dcc.Store(id='ticks-data-store', data=pd.read_csv('ticks.csv').to_json(date_format='iso', orient='split')),
    dcc.Store(id='tab-store', data='tab-pyramid')
])


@app.callback(
        Output('max-dropdown', 'options'),
        Output('max-dropdown', 'value'),
        Output('multi-div', 'hidden'),
        Output('boulder-div', 'hidden'),
        Output('rope-div', 'hidden'),
        Output('send-dropdown', 'options'),
        Output('send-dropdown', 'value'),
        [Input('route-type', 'value')],
        State('ticks-data-store', 'data'),
        )
def update_route_type(route_type, ticks_data):
    if ticks_data is None:
        if route_type == 'Rope':
            grade_options = [{'label': value, 'value': key} for key,value in GRADES.items() if value.startswith('5')]
            max_grade = 8500
        grade_options = [{'label': value, 'value': key} for key,value in GRADES.items() if value.startswith('V')]
        max_grade = 20800
    grade_options, max_grade = update_send_dropdown(ticks_data, route_type)
    if route_type == 'Rope':
        return grade_options, max_grade, False, True, False, ['Onsight', 'Flash', 'Redpoint', 'Pinkpoint', 'Fell/Hung', 'N/A'], ['Onsight', 'Flash', 'Redpoint']
    return grade_options, max_grade, True, False, True, ['Send', 'Attempt','Flash'], ['Send','Flash']



@app.callback(Output('tab-store', 'data'),
              [Input('tabs', 'value')],
              prevent_initial_call=True)
def update_tab(tab):
    return tab

@app.callback(
    Output('max-dropdown', 'options', allow_duplicate=True),
    Output('max-dropdown', 'value', allow_duplicate=True),
    [Input('ticks-data-store', 'data')],
    State('route-type', 'value'),
    prevent_initial_call=True)
def update_send_dropdown(ticks_data, route_type):
    # find the max 'Rating Code' from the ticks data
    data = pd.read_json(io.StringIO(ticks_data), orient='split')
    if route_type == 'Rope':
        # the max grade is the highest value in the 'Rating Code' column that is less than 20000
        max_grade = data['Rating Code'][data['Rating Code'] < 20000].max()
        grades = [{'label': value, 'value': key} for key,value in GRADES.items() if value.startswith('5') and key <= max_grade]
        return grades, max_grade
    max_grade = data['Rating Code'][(data['Rating Code'] < 30000) & (data['Rating Code'] >= 20000)].max()
    boulder_grades = [{'label': value, 'value': key} for key,value in GRADES.items() if value.startswith('V') and key <= max_grade]
    return boulder_grades, max_grade

@app.callback(
        Output('graph-display', 'figure'),
        [Input('tab-store', 'data'),
         Input('ticks-data-store', 'data'),
         Input('route-type', "value"),
         Input('rope-type', "value"),
         Input('send-dropdown', "value"),
         Input('date-range', "start_date"),
         Input('date-range', "end_date"),
         Input('max-dropdown', "value"),
         Input('multi-filter', "value"),
         Input('boulder-filter', "value"),],
        )
def render_graphs(tab, ticks_data, route_type, rope_type, criteria_send, start_date, end_date,
                   criteria_max, criteria_multi, criteria_boulder):
    if tab == 'tab-pyramid':
        pyramid = generate_pyramid(ticks_data, route_type, rope_type, criteria_send, start_date, end_date,
                   criteria_max, criteria_multi, criteria_boulder)
        return pyramid
    elif tab == 'tab-scatter':
        scatter = generate_scatter(ticks_data, route_type, rope_type, criteria_send, start_date, end_date,
                       criteria_max, criteria_multi, criteria_boulder)
        return scatter


@app.callback(
    Output('ticks-data-store', 'data', allow_duplicate=True),
    [Input('upload-data', 'contents')],
    prevent_initial_call=True)
def upload_update_output(upload_data):
    _, upload_data = upload_data.split(',')
    decoded = io.StringIO(base64.b64decode(upload_data).decode('utf-8'))
    downloaded_ticks = pd.read_csv(decoded, parse_dates=['Date'])
    return downloaded_ticks.to_json(date_format='iso', orient='split')

@app.callback(
    Output('ticks-data-store', 'data', allow_duplicate=True),
    [Input('download-button', 'n_clicks')],
    [State('mp-url', 'value')],
    prevent_initial_call=True
)
def mp_update_output(n_clicks, mp_url):
    assert mp_url.startswith('https://www.mountainproject.com/user/'), "Invalid URL"
    mp_url += '/tick-export'
    page = requests.get(mp_url)
    assert page.status_code == 200, f"Invalid URL: {mp_url}"
    decoded = io.StringIO(page.text)
    downloaded_ticks = pd.read_csv(decoded, parse_dates=['Date'])
    return downloaded_ticks.to_json(date_format='iso', orient='split')


if __name__ == '__main__':
    app.run_server(debug=True)
