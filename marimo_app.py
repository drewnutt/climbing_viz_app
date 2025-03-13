import marimo

__generated_with = "0.10.18"
app = marimo.App(width="medium")


@app.cell
def _():
    import micropip
    return (micropip,)


@app.cell
async def _(micropip):
    import marimo as mo
    import requests
    await micropip.install('plotly==5.14.0')
    import plotly.graph_objects as go
    import plotly.express as px
    import statsmodels.api as sm
    from datetime import date
    import pandas as pd
    import base64
    import io
    return base64, date, go, io, mo, pd, px, requests, sm


@app.cell
def _(datetime, go, mo, np, pd, px, sm):
    GRADES = {
        800: '3rd', 900: '4th', 950: 'Easy 5th', 1000: '5.0', 1100: '5.1', 1200: '5.2', 1300: '5.3', 1400: '5.4', 1500: '5.5', 1600: '5.6', 1800: '5.7', 1900: '5.7+', 2000: '5.8-', 2100: '5.8', 2200: '5.8+', 2300: '5.9-', 2400: '5.9', 2500: '5.9+', 2600: '5.10a', 2700: '5.10-', 2800: '5.10a/b', 2900: '5.10b', 3000: '5.10', 3100: '5.10b/c', 3200: '5.10c', 3300: '5.10+', 3400: '5.10c/d', 3500: '5.10d', 4600: '5.11a', 4700: '5.11-', 4800: '5.11a/b', 4900: '5.11b', 5000: '5.11', 5100: '5.11b/c', 5200: '5.11c', 5300: '5.11+', 5400: '5.11c/d', 5500: '5.11d', 6600: '5.12a', 6700: '5.12-', 6800: '5.12a/b', 6900: '5.12b', 7000: '5.12', 7100: '5.12b/c', 7200: '5.12c', 7300: '5.12+', 7400: '5.12c/d', 7500: '5.12d', 8600: '5.13a', 8700: '5.13-', 8800: '5.13a/b', 8900: '5.13b', 9000: '5.13', 9100: '5.13b/c', 9200: '5.13c', 9300: '5.13+', 9400: '5.13c/d', 9500: '5.13d', 10500: '5.14a', 10600: '5.14-', 10700: '5.14a/b', 10900: '5.14b', 11100: '5.14', 11150: '5.14b/c', 11200: '5.14c', 11300: '5.14+', 11400: '5.14c/d', 11500: '5.14d', 11600: '5.15a', 11700: '5.15-', 11800: '5.15a/b', 11900: '5.15b', 12000: '5.15', 12100: '5.15c', 12200: '5.15+', 12300: '5.15c/d', 12400: '5.15d',
            20000: 'V-easy', 20005: 'V0-', 20008: 'V0', 20011: 'V0+', 20050: 'V0-1', 20075: 'V1-', 20100: 'V1', 20110: 'V1+', 20150: 'V1-2', 20170: 'V2-', 20200: 'V2', 20210: 'V2+', 20250: 'V2-3', 20270: 'V3-', 20300: 'V3', 20310: 'V3+', 20350: 'V3-4', 20370: 'V4-', 20400: 'V4', 20410: 'V4+', 20450: 'V4-5', 20470: 'V5-', 20500: 'V5', 20510: 'V5+', 20550: 'V5-6', 20570: 'V6-', 20600: 'V6', 20610: 'V6+', 20650: 'V6-7', 20670: 'V7-', 20700: 'V7', 20710: 'V7+', 20750: 'V7-8', 20770: 'V8-', 20800: 'V8', 20810: 'V8+', 20850: 'V8-9', 20870: 'V9-', 20900: 'V9', 20910: 'V9+', 20950: 'V9-10', 20970: 'V10-', 21000: 'V10', 21010: 'V10+', 21050: 'V10-11', 21070: 'V11-', 21100: 'V11', 21110: 'V11+', 21150: 'V11-12', 21170: 'V12-', 21200: 'V12', 21210: 'V12+', 21250: 'V12-13', 21270: 'V13-', 21300: 'V13', 21310: 'V13+', 21350: 'V13-14', 21370: 'V14-', 21400: 'V14', 21410: 'V14+', 21450: 'V14-15', 21470: 'V15-', 21500: 'V15', 21510: 'V15+', 21550: 'V15-16', 21570: 'V16-', 21600: 'V16', 21610: 'V16+', 21650: 'V16-17', 21670: 'V17-', 21700: 'V17',
        30000: 'WI1', 30750: 'WI2-', 31000: 'WI2', 31250: 'WI2+', 31500: 'WI2-3', 31750: 'WI3-', 32000: 'WI3', 32250: 'WI3+', 32500: 'WI3-4', 32750: 'WI4-', 33000: 'WI4', 33250: 'WI4+', 33500: 'WI4-5', 33750: 'WI5-', 34000: 'WI5', 34250: 'WI5+', 34500: 'WI5-6', 34750: 'WI6-', 35000: 'WI6', 35250: 'WI6+', 35500: 'WI6-7', 35750: 'WI7-', 36000: 'WI7', 36250: 'WI7+', 36500: 'WI7-8', 36750: 'WI8-', 37000: 'WI8', 38000: 'AI1', 38050: 'AI1-2', 38100: 'AI2', 38150: 'AI2-3', 38200: 'AI3', 38250: 'AI3-4', 38300: 'AI4', 38350: 'AI4-5', 38400: 'AI5', 38450: 'AI5-6', 38500: 'AI6',
        50000: 'M1', 50250: 'M1+', 50500: 'M1-2', 50750: 'M2-', 51000: 'M2', 51250: 'M2+', 51500: 'M2-3', 51750: 'M3-', 52000: 'M3', 52250: 'M3+', 52500: 'M3-4', 52750: 'M4-', 53000: 'M4', 53250: 'M4+', 53500: 'M4-5', 53750: 'M5-', 54000: 'M5', 54250: 'M5+', 54500: 'M5-6', 54750: 'M6-', 55000: 'M6', 55250: 'M6+', 55500: 'M6-7', 55750: 'M7-', 56000: 'M7', 56250: 'M7+', 56500: 'M7-8', 56750: 'M8-', 57000: 'M8', 57250: 'M8+', 57500: 'M8-9', 57750: 'M9-', 58000: 'M9', 58250: 'M9+', 58500: 'M9-10', 58750: 'M10-', 59000: 'M10', 59250: 'M10+', 59500: 'M10-11', 59750: 'M11-', 60000: 'M11', 60050: 'M11+', 60900: 'M12-', 61000: 'M12', 61050: 'M12+', 61900: 'M13-', 62000: 'M13', 62050: 'M13+',
        70000: 'C0', 70010: 'A0', 70250: 'C0+', 70260: 'A0+', 70500: 'C0-1', 70510: 'A0-1', 70750: 'C1-', 70760: 'A1-', 71000: 'C1', 71010: 'A1', 71250: 'C1+', 71260: 'A1+', 71500: 'C1-2', 71510: 'A1-2', 71750: 'C2-', 71760: 'A2-', 72000: 'C2', 72010: 'A2', 72250: 'C2+', 72260: 'A2+', 72500: 'C2-3', 72510: 'A2-3', 72750: 'C3-', 72760: 'A3-', 73000: 'C3', 73010: 'A3', 73250: 'C3+', 73260: 'A3+', 73500: 'C3-4', 73510: 'A3-4', 73750: 'C4-', 73760: 'A4-', 74000: 'C4', 74010: 'A4', 74250: 'C4+', 74260: 'A4+', 74500: 'C4-5', 74510: 'A4-5', 74750: 'C5-', 74760: 'A5-', 75000: 'C5', 75010: 'A5', 75250: 'C5+', 75260: 'A5+',
        80000: "Easy Snow", 81000: "Mod. Snow", 82000: "Steep Snow"
    }
    def filter_time(ticks, start_date, end_date):
        if start_date is not None:
            ticks = ticks.loc[ticks['Date'] >= pd.to_datetime(start_date), :]
        if end_date is not None:
            ticks = ticks.loc[ticks['Date'] <= pd.to_datetime(end_date), :]
        return ticks

    def handle_roped(rope_type, ticks, criteria_send, start_date, end_date, criteria_max, criteria_multi):
        ticks = ticks[ticks['Rating Code'] < 20000]
        ticks = ticks.loc[ticks['Route Type'].isin(rope_type), :]
        ticks = filter_time(ticks, start_date, end_date)
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

        ticks['Style'] = ticks['Lead Style']
        return ticks

    def handle_boulders(ticks, criteria_send, start_date, end_date, criteria_max, criteria_boulder):
        ticks = ticks[(ticks['Rating Code'] >= 20000) & (ticks['Rating Code'] < 30000)]
        ticks = ticks.loc[ticks['Style'].isin(criteria_send)]
        ticks = filter_time(ticks, start_date, end_date)
        ticks = ticks.loc[ticks['Rating Code'] <= criteria_max, :]
        ticks['Grade'] = pd.cut(
            ticks['Rating Code'],
            bins=[0] + [key for key in GRADES.keys() if (key <= criteria_max) & (key >= 20000)],
            labels=[value for key, value in GRADES.items() if (key <= criteria_max) & (key >= 20000)])
        if criteria_boulder:
            ticks['Grade'] = ticks['Grade'].apply(lambda x: 'V' + x.split('-')[0][1:].strip('+-'))

        return ticks

    def generate_pyramid(ticks,route_type, rope_type, criteria_send, start_date, end_date,
                         criteria_max, criteria_multi, criteria_boulder):
        if ticks is None:
            return go.Figure()
        # Filter the dataframe based on criteria
        if route_type == "Rope":
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
        if route_type == "Rope":
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
                symbol=None if route_type != 'Rope' else 'Route Type',
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
    mo.output.clear()
    return (
        GRADES,
        filter_time,
        generate_pyramid,
        generate_scatter,
        handle_boulders,
        handle_roped,
    )


@app.cell
def _(mo):
    download_button = mo.ui.run_button()
    mp_url = mo.ui.text('https://www.mountainproject.com/user/USERNUM/USER-NAME', max_length=60,kind='url',full_width=True)
    mo.vstack([mo.md('Enter your Mountain Project profile URL to download your ticks.csv'),
               mp_url,download_button,
              ])
    return download_button, mp_url


@app.cell
def _(date, download_button, io, mo, mp_url, pd, requests):
    def get_ticks_data(text_url):
        mp_url = str(text_url)
        assert mp_url.startswith('https://www.mountainproject.com/user/'), f"Invalid URL:{mp_url}"
        mp_url += '/tick-export'
        page = requests.get(mp_url)
        assert page.status_code == 200, f"Invalid URL: {mp_url}"
        decoded = io.StringIO(page.text)
        downloaded_ticks = pd.read_csv(decoded, parse_dates=['Date'])
        return downloaded_ticks
    mo.stop(not download_button.value,"Downloading ticks data to generate graphs")
    mp_ticks = get_ticks_data(mp_url.value)
    start_date = date(1960,1,1)
    def get_min_date(data):
        min_date = data['Date'].min()
        return min_date.date()
    if mp_ticks is not None:
        start_date = get_min_date(mp_ticks)
    date_selector = mo.ui.date_range(stop=date.today(),start=start_date,value=(start_date,date.today()))
    route_selector = mo.ui.radio(options=['Rope','Boulder','Ice','Aid','Mixed','Snow'],value='Rope',label='Route Type')
    mo.vstack([mo.hstack([mo.md("Select timeframe:"),date_selector.left(),]),route_selector])
    return (
        date_selector,
        get_min_date,
        get_ticks_data,
        mp_ticks,
        route_selector,
        start_date,
    )


@app.cell
def _(GRADES, mo, mp_ticks, route_selector):
    def update_send_dropdown(data, route_type):
        # find the max 'Rating Code' from the ticks data
        if route_type == 'Rope':
            # the max grade is the highest value in the 'Rating Code' column that is less than 20000
            max_grade = data['Rating Code'][data['Rating Code'] < 20000].max()
            grades = {value:key for key,value in GRADES.items() if value.startswith('5') and key <= max_grade}
            return grades, GRADES[max_grade]
        max_grade = data['Rating Code'][(data['Rating Code'] < 30000) & (data['Rating Code'] >= 20000)].max()
        boulder_grades = {value: key for key,value in GRADES.items() if value.startswith('V') and key <= max_grade}
        return boulder_grades, GRADES[max_grade]
    def update_route_type(route_type, ticks_data):
        if ticks_data is None:
            if route_type == 'Rope':
                grade_options = {value:key for key,value in GRADES.items() if value.startswith('5')}
                max_grade = '5.12c'
            grade_options = {value:key for key,value in GRADES.items() if value.startswith('V')}
            max_grade = 'V9'
        grade_options, max_grade = update_send_dropdown(ticks_data, route_type)
        if route_type == 'Rope':
            return grade_options, max_grade, ['Onsight', 'Flash', 'Redpoint', 'Pinkpoint', 'Fell/Hung', 'N/A'], ['Onsight', 'Flash', 'Redpoint','Fell/Hung']
        return grade_options, max_grade, ['Send', 'Attempt','Flash'], ['Send','Flash','Attempt']


    grade_options, max_grade, send_options, send_value = update_route_type(route_selector.value,mp_ticks)


    rope_selector = mo.ui.multiselect(options=['Sport','Trad','TR'],value=['Sport'],label='Rope Type')
    criteria_send = mo.ui.multiselect(options=send_options,value=send_value,label='Send Type')
    max_grade_selector = mo.ui.dropdown(options=grade_options,value=max_grade,label='Maximum Grade')
    multipitch_checkbox = mo.ui.checkbox(label="Include MultiPitch Routes")
    boulder_checkbox = mo.ui.checkbox(label="Combine -,+, and normal grades",value=True)
    gui = []
    if route_selector.value == "Rope":
        gui += [rope_selector]
    gui += [criteria_send]
    if route_selector.value in ['Rope','Ice','Aid','Mixed']:
        gui += [multipitch_checkbox]
    elif route_selector.value == 'Boulder':
        gui += [boulder_checkbox]
    mo.vstack(gui)
    return (
        boulder_checkbox,
        criteria_send,
        grade_options,
        gui,
        max_grade,
        max_grade_selector,
        multipitch_checkbox,
        rope_selector,
        send_options,
        send_value,
        update_route_type,
        update_send_dropdown,
    )


@app.cell
def _(
    boulder_checkbox,
    criteria_send,
    date_selector,
    generate_pyramid,
    max_grade_selector,
    mp_ticks,
    multipitch_checkbox,
    rope_selector,
    route_selector,
):
    generate_pyramid(mp_ticks, route_selector.value, rope_selector.value, criteria_send.value,
                     date_selector.value[0],date_selector.value[1], max_grade_selector.value, 
                     multipitch_checkbox.value, boulder_checkbox.value)
    return


@app.cell
def _(
    boulder_checkbox,
    criteria_send,
    date_selector,
    generate_scatter,
    max_grade_selector,
    mp_ticks,
    multipitch_checkbox,
    rope_selector,
    route_selector,
):
    generate_scatter(mp_ticks, route_selector.value, rope_selector.value, criteria_send.value,
                     date_selector.value[0], date_selector.value[1], max_grade_selector.value, 
                     multipitch_checkbox.value, boulder_checkbox.value)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
