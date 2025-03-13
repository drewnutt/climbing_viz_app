#!/usr/bin/env python3
import datetime
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import io
import statsmodels.api as sm
from data_cleaning import handle_roped, handle_boulders
from grades import GRADES

def generate_pyramid(ticks,route_type, rope_type, criteria_send, start_date, end_date,
                     criteria_max, criteria_multi, criteria_boulder):
    if ticks is None:
        return go.Figure()
    # Filter the dataframe based on criteria
    if route_type == "Roped":
        ticks = handle_roped(rope_type, ticks, criteria_send, start_date, end_date, criteria_max, criteria_multi)
        send = ['Onsight', 'Flash', 'Redpoint', 'Pinkpoint']
        attempt = ['Fell/Hung', 'N/A']
        tickvals=[f'5.{v}' for v in range(8,10)] + [f'5.{v}a' for v in range(10,16)]
    else:
        ticks = handle_boulders(ticks, criteria_send, start_date, end_date, criteria_max, criteria_boulder)
        # create a new column with only the numeric part of the grade
        ticks['Grade'] = ticks['Grade'].apply(lambda x: 'V' + x.split()[0][1:])
        send = ['Send', 'Flash']
        attempt = ['Attempt']
        tickvals=[f'V{v}' for v in range(0,17)]
        # check the 'Style' column for the values in 'send' and 'attempt'
    send = [s for s in send if s in ticks['Style'].unique()]
    attempt = [a for a in attempt if a in ticks['Style'].unique()]
    counts = ticks.groupby(['Grade','Style']).count().reset_index()
    counts = counts[counts['Style'].isin(send + attempt)]
    counts = counts.pivot(index='Grade',columns='Style',values='Date').reset_index()
    # convert the counts to integers from objects
    counts[send + attempt] = counts[send + attempt].fillna(0).astype(int)
    # print counts to determine the types
    counts['Top'] = counts[send].sum(axis=1)
    counts['attempt'] = counts[attempt].sum(axis=1)
    counts = counts.sort_values(by='Grade',ascending=False)

    # Create a funnel-like chart that puts 'Redpoints','Flashes','Onsights' on the right side
    # and 'Fell/Hung' and 'N/A' on the left side
    fig = go.Figure()
    # construct a hovertemplate dynamically based on the columns in the dataframe
    hovertemplate = '<b>%{y}</b>: %{x} Total<br>'
    for i, s in enumerate(send):
        hovertemplate += f'  %{{customdata[{i}]}} {s}<br>'
    hovertemplate = hovertemplate[:-4]
    fig.add_trace(go.Bar(y=counts['Grade'],x=counts['Top'],orientation='h',
                         name='Send', customdata=np.stack([counts[s] for s in send],axis=-1),
                         hovertemplate=hovertemplate))
    hovertemplate = '<b>%{y}</b>: %{customdata[0]} Total'
    fig.add_trace(go.Bar(y=counts['Grade'],x=-counts['attempt'],orientation='h',
                         name='Attempt', customdata=counts['attempt'].values[:,None],
                         hovertemplate=hovertemplate))

    # flip the y-axis so that V0 is at the bottom
    fig.update_yaxes(autorange='reversed')
    fig.update_yaxes(tickvals=tickvals)
    fig.update_layout(barmode='overlay')
    fig.update_layout(title='Climbing Pyramid', xaxis_title='Number of Routes', yaxis_title='Grade')

    return fig

def generate_scatter(ticks,route_type, rope_type, criteria_send, start_date, end_date,
                     criteria_max, criteria_multi, criteria_boulder):
    if ticks is None:
        return go.Figure()
    # Filter the dataframe based on criteria
    if route_type == "Roped":
        ticks = handle_roped(rope_type, ticks, criteria_send, start_date, end_date, criteria_max, criteria_multi)
        tickvals = [key for key,value in GRADES.items() if value.startswith('5') and key <= criteria_max]
        ticktext = [value for key,value in GRADES.items() if value.startswith('5') and key <= criteria_max]
        label = 'YDS'
        style = 'Lead Style'
        checkstring = '5'
    else:
        ticks = handle_boulders(ticks, criteria_send, start_date, end_date, criteria_max, criteria_boulder)
        checkstring = 'V'
        label = 'V-Scale'
        style = 'Style'

    tickvals, ticktext = [], []
    for key,value in GRADES.items():
        if value.startswith(checkstring) and key <= criteria_max:
            if '-' in value or '+' in value:
                continue
            if 'b' in value or 'd' in value:
                continue
            tickvals.append(key)
            ticktext.append(value)

    # Create a chart based on the filtered dataframe
    fig = px.scatter(ticks, x='Date', y='Rating Code', color=style,
            hover_data={'Route':True, 'Rating Code':False, 'Grade':True, 'Date':True},
            symbol=None if route_type != 'Roped' else 'Route Type',
            # add trendline
            trendline="ols", trendline_color_override='dark blue',
            width=1000, height=600)
    # add another trendline for all data regardless of style
    ticks['timestamp']=pd.to_datetime(ticks['Date'])
    ticks['serialtime']=[(d-datetime.datetime(1970,1,1)).days for d in ticks['timestamp']]

    x = sm.add_constant(ticks['serialtime'])
    model = sm.OLS(ticks['Rating Code'], x).fit()
    ticks['bestfit']=model.fittedvalues
    fig.add_trace(go.Scatter(x=ticks['Date'], y=ticks['bestfit'], mode='lines', name='All Data', line=dict(color='dark blue', width=2)))
    fig.update_yaxes(tickvals=tickvals, ticktext=ticktext, title=label)

    return fig
