import marimo

__generated_with = "0.10.18"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import requests
    import plotly.graph_objects as go
    from datetime import date
    import pandas as pd
    import base64
    import io
    from grades import GRADES
    from figures import generate_pyramid, generate_scatter
    return (
        GRADES,
        base64,
        date,
        generate_pyramid,
        generate_scatter,
        go,
        io,
        mo,
        pd,
        requests,
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
