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


if os.getenv('HOST'):
    del os.environ['HOST']

# constant for grade/code conversion
GRADES = {1700: "5.easy",1900: "5.7", 2200: "5.8",2500: "5.9",
          2800: "5.10a",3100: "5.10b", 3400: "5.10c",4500: "5.10d",
          4800: "5.11a",5100: "5.11b", 5400: "5.11c",6500: "5.11d",
          6800: "5.12a",7100: "5.12b", 7400: "5.12c",8500: "5.12d",
          8800: "5.13a",9100: "5.13b", 9400: "5.13c",10400: "5.13d"}
BOULDER_GRADES = {20000 + 100 * i: f"V{i}" for i in range(1,18)} | \
            {20000 + 100 * i - 30: f"V{i}-" for i in range(2,18)}  | {20000 + 100 * i + 10:f"V{i}+" for i in range(1,17)} | \
            {20000 + 100 * i + 50: f"V{i}-{i+1}" for i in range(2,17)}  
BOULDER_GRADES = BOULDER_GRADES | {20000: "V-easy", 20005: "V0-", 20010: "V0+", 20008: "V0"}
# sort the boulder grades by value
BOULDER_GRADES = dict(sorted(BOULDER_GRADES.items(), key=lambda x: x[0]))

# generate BOULDER_GRADES 
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
        dcc.Dropdown(options=[{'label': value, 'value': key} for key,value in GRADES.items()], value=8500, id='max-dropdown',
                                    searchable=False, clearable=False)],
            style={'width':'30vw'}),
    html.Div(children=[dcc.Checklist(['Include Multipitch Routes'],['Include Multipitch Routes'],
                  id='multi-filter'),], id='multi-div', style={'width':'75vw'}),
    # make a new Div that has a checklist for combining +,-,and normal boulder grades
    html.Div(children=[dcc.Checklist(['Combine -,+, and normal grades'],['Combine -,+, and normal grades'],
                  id='boulder-filter'),], id='boulder-div', hidden=True, style={'width':'75vw'}),
    dcc.Loading([dcc.Graph(id='graph-pyramid', config=config,
              style={'width':'80vw', 'height':'80vh'})]),
    dcc.Store(id='ticks-data-store')
])
@app.callback(
        Output('max-dropdown', 'options'),
        Output('max-dropdown', 'value'),
        Output('multi-div', 'hidden'),
        Output('boulder-div', 'hidden'),
        Output('rope-div', 'hidden'),
        Output('send-dropdown', 'options'),
        [Input('route-type', 'value')],
        )
def update_route_type(route_type):
    if route_type == 'Rope':
        grades = [{'label': value, 'value': key} for key,value in GRADES.items()]
        return grades, 8500, False, True, False, ['Onsight', 'Flash', 'Redpoint', 'Pinkpoint', 'Fell/Hung', 'N/A']
    elif route_type == 'Boulder':
        print(BOULDER_GRADES)
        boulder_grades = [{'label': value, 'value': key} for key,value in BOULDER_GRADES.items()]
        return boulder_grades, 20800, True, False, True, ['Send', 'Attempt','Flash']

def handle_roped(rope_type, ticks, criteria_send, start_date, end_date, criteria_max, criteria_multi):
    ticks = ticks.loc[ticks['Route Type'].isin(rope_type), :]
    if start_date is not None:
        ticks = ticks.loc[ticks['Date'] >= pd.to_datetime(start_date), :]
    if end_date is not None:
        ticks = ticks.loc[ticks['Date'] <= pd.to_datetime(end_date), :]
    if 'N/A' in criteria_send:
        ticks = ticks.loc[ticks['Lead Style'].isna() | ticks['Lead Style'].isin(criteria_send), :]
    else:
        ticks = ticks.loc[ticks['Lead Style'].isin(criteria_send), :]
    if criteria_multi == []:
        ticks = ticks.loc[ticks['Pitches']==1, :]
    ticks = ticks.loc[ticks['Rating Code']<= criteria_max, :]

    # Calculate climbing pyramid metrics
    ticks['Grade'] = pd.cut(
        ticks['Rating Code'],
        bins=[0] + [key for key in GRADES.keys() if key <= criteria_max],
        labels=[value for key, value in GRADES.items() if key <= criteria_max])
    return ticks

def handle_boulders(ticks, criteria_send, start_date, end_date, criteria_max, criteria_boulder):
    ticks = ticks.loc[ticks['Style'].isin(criteria_send)]
    if start_date is not None:
        ticks = ticks.loc[ticks['Date'] >= pd.to_datetime(start_date), :]
    if end_date is not None:
        ticks = ticks.loc[ticks['Date'] <= pd.to_datetime(end_date), :]
    ticks = ticks.loc[ticks['Rating Code'] <= criteria_max, :]
    ticks['Grade'] = pd.cut(
        ticks['Rating Code'],
        bins=[0] + [key for key in BOULDER_GRADES.keys() if key <= criteria_max],
        labels=[value for key, value in BOULDER_GRADES.items() if key <= criteria_max])
    if criteria_boulder:
        ticks['Grade'] = ticks['Grade'].apply(lambda x: x.replace('-', '').replace('+', '') if x != 'V-easy' else x)

    return ticks

@app.callback(
        Output('graph-pyramid', 'figure', allow_duplicate=True),
        [Input('ticks-data-store', 'data'),
         Input('route-type', "value"),
         Input('rope-type', "value"),
         Input('send-dropdown', "value"),
         Input('date-range', "start_date"),
         Input('date-range', "end_date"),
         Input('max-dropdown', "value"),
         Input('multi-filter', "value"),
         Input('boulder-filter', "value"),],
         prevent_initial_call=True)
def parse_contents(ticks_data,route_type, rope_type, criteria_send, start_date, end_date,
                   criteria_max, criteria_multi, criteria_boulder):
    if ticks_data is None:
        return go.Figure()
    ticks = pd.read_json(io.StringIO(ticks_data), orient='split')
    # Filter the dataframe based on criteria
    if route_type == "Rope":
        ticks = handle_roped(rope_type, ticks, criteria_send, start_date, end_date, criteria_max, criteria_multi)
    else:
        ticks = handle_boulders(ticks, criteria_send, start_date, end_date, criteria_max, criteria_boulder)
    counts = ticks.groupby('Grade', observed=False)['URL'].nunique().reset_index()
    counts.columns = ['Grade', 'Routes']
    counts.sort_values(by='Grade', ascending=False, inplace=True)

    # Create a chart based on the filtered dataframe
    fig = px.funnel(counts, x='Routes', y='Grade', title="User's Route Pyramid")

    return fig

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
