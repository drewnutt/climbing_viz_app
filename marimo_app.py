import marimo

__generated_with = "0.19.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import requests
    import plotly.graph_objects as go
    import plotly.express as px
    import statsmodels.api as sm
    from datetime import date
    import pandas as pd
    import base64
    import io
    import numpy as np
    import datetime
    # Import from local modules
    from grades import GRADES, REVERSE_GRADES
    from figures import generate_pyramid, generate_scatter
    from data_cleaning import handle_roped, handle_boulders, handle_generic
    return (
        GRADES,
        REVERSE_GRADES,
        date,
        generate_pyramid,
        generate_scatter,
        handle_boulders,
        handle_generic,
        handle_roped,
        io,
        mo,
        pd,
        px,
        requests,
    )


@app.cell
def _():
    # Grade ranges for different climbing types
    grade_ranges = {
        'Roped': (0, 20000),
        'Bouldering': (20000, 30000),
        'Ice': (30000, 50000),
        'Mixed': (50000, 70000),
        'Aid': (70000, 80000),
        'Snow': (80000, 90000)
    }
    return (grade_ranges,)


@app.cell
def _(mo):
    download_button = mo.ui.run_button()
    mp_url = mo.ui.text('https://www.mountainproject.com/user/USERNUM/USER-NAME', max_length=60,kind='url',full_width=True)
    file_uploader = mo.ui.file(filetypes=['.csv'], kind='area', label='Upload CSV file')
    mo.vstack([
        mo.md('**Download your tick data from Mountain Project and upload it here:**'),
        mo.md('**OR** Enter your Mountain Project profile URL to download your ticks.csv:'),
        file_uploader,
        mp_url,
        download_button,
    ])
    return download_button, file_uploader, mp_url


@app.cell
def _(
    GRADES,
    date,
    download_button,
    file_uploader,
    grade_ranges,
    io,
    mo,
    mp_url,
    pd,
    requests,
):
    def get_ticks_data(text_url):
        mp_url = str(text_url)
        assert mp_url.startswith('https://www.mountainproject.com/user/'), f"Invalid URL:{mp_url}"
        mp_url += '/tick-export'
        page = requests.get(mp_url)
        assert page.status_code == 200, f"Invalid URL: {mp_url}"
        decoded = io.StringIO(page.text)
        downloaded_ticks = pd.read_csv(decoded, parse_dates=['Date'])
        return downloaded_ticks

    def csv_to_df(uploaded_file):
        if uploaded_file is not None and len(uploaded_file) > 0:
            file_contents = uploaded_file[0].contents
            return pd.read_csv(io.BytesIO(file_contents), parse_dates=['Date'])
        return None

    def update_send_dropdown(data, route_type):
        # find the max 'Rating Code' from the ticks data
        min_code, max_code = grade_ranges[route_type]
        max_grade = data['Rating Code'][(data['Rating Code'] >= min_code) & (data['Rating Code'] < max_code)].max()
        grades = {value: key for key, value in GRADES.items() if key < max_code and key >= min_code}
        if pd.isna(max_grade):
            max_grade = max(grades.values()) if grades else min_code
        return grades, GRADES[max_grade] if max_grade in GRADES else max(grades.values())


    def update_route_type(route_type, ticks_data):
        defaults = {
            'Roped': ('5', '5.12c', ['Onsight', 'Flash', 'Redpoint', 'Pinkpoint', 'Fell/Hung', 'N/A'], ['Onsight', 'Flash', 'Redpoint','Fell/Hung']),
            'Bouldering': ('V', 'V9', ['Send', 'Attempt','Flash'], ['Send','Flash','Attempt']),
            'Ice': (('WI', 'AI'), 'WI4', ['Onsight', 'Flash', 'Redpoint', 'Pinkpoint', 'TR','Fell/Hung', 'N/A'], ['Onsight', 'Redpoint', 'Flash','TR']),
            'Mixed': ('M', 'M6', ['Onsight', 'Flash', 'Redpoint', 'Pinkpoint', 'Fell/Hung', 'N/A'], ['Onsight', 'Redpoint', 'Flash']),
            'Aid': (('C', 'A'), 'A2', ['Onsight', 'Flash', 'Redpoint', 'Pinkpoint', 'Fell/Hung', 'N/A'], ['Onsight', 'Redpoint', 'Flash']),
            'Snow': (('Easy', 'Mod', 'Steep'), 'Mod. Snow', ['Send', 'Attempt','Flash'], ['Send','Flash','Attempt'])
        }
        prefix, default_max, send_opts, send_vals = defaults[route_type]

        if ticks_data is None or len(ticks_data) == 0:
            if isinstance(prefix, tuple):
                grade_options = {value: key for key, value in GRADES.items() if any(value.startswith(p) for p in prefix)}
            else:
                grade_options = {value: key for key, value in GRADES.items() if value.startswith(prefix)}
            max_grade = default_max
        else:
            grade_options, max_grade = update_send_dropdown(ticks_data, route_type)
        return grade_options, max_grade, send_opts, send_vals


    # Load data from either file upload or URL
    ticks_data = None
    if file_uploader.value is not None and len(file_uploader.value) > 0:
        ticks_data = csv_to_df(file_uploader.value)
    elif download_button.value:
        mo.stop(not download_button.value, "Downloading ticks data to generate graphs")
        ticks_data = get_ticks_data(mp_url.value)

    start_date = date(1960, 1, 1)
    def get_min_date(data):
        if data is not None and len(data) > 0:
            min_date = data['Date'].min()
            return min_date.date()
        return date(1960, 1, 1)

    if ticks_data is not None and len(ticks_data) > 0:
        start_date = get_min_date(ticks_data)

    date_selector = mo.ui.date_range(stop=date.today(), start=start_date, value=(start_date, date.today()))
    route_selector = mo.ui.radio(
        options=['Roped', 'Bouldering', 'Ice', 'Mixed', 'Aid', 'Snow'],
        value='Roped',
        label='Select Climbing Type'
    )
    leftside = mo.vstack([
        mo.hstack([mo.md("Select timeframe:"), date_selector.left()]),
        route_selector
    ])
    return (
        date_selector,
        leftside,
        route_selector,
        ticks_data,
        update_route_type,
    )


@app.cell
def _(leftside, mo, route_selector, ticks_data, update_route_type):
    if ticks_data is not None and len(ticks_data) > 0:
        grade_options, max_grade, send_options, send_value = update_route_type(route_selector.value, ticks_data)
    else:
        grade_options, max_grade, send_options, send_value = update_route_type(route_selector.value, None)

    rope_selector = mo.ui.multiselect(options=['Sport','Trad','TR'],value=['Sport'],label='Rope Type')
    criteria_send = mo.ui.multiselect(options=send_options,value=send_value,label='Send Type')
    max_grade_selector = mo.ui.dropdown(options=list(grade_options.keys()),value=max_grade,label='Maximum Grade')
    multipitch_checkbox = mo.ui.checkbox(label="Include MultiPitch Routes")
    boulder_checkbox = mo.ui.checkbox(label="Combine -,+, and normal grades",value=True)


    gui = []
    if route_selector.value == "Roped":
        gui += [rope_selector]
    gui += [criteria_send]
    gui += [max_grade_selector]
    if route_selector.value in ['Roped','Ice','Aid','Mixed']:
        gui += [multipitch_checkbox]
    elif route_selector.value == 'Bouldering':
        gui += [boulder_checkbox]
    mo.hstack([leftside,mo.vstack(gui)])
    return (
        boulder_checkbox,
        criteria_send,
        max_grade_selector,
        multipitch_checkbox,
        rope_selector,
    )


@app.cell
def _(
    REVERSE_GRADES,
    boulder_checkbox,
    criteria_send,
    date_selector,
    grade_ranges,
    handle_boulders,
    handle_generic,
    handle_roped,
    max_grade_selector,
    multipitch_checkbox,
    pd,
    rope_selector,
    route_selector,
    ticks_data,
):
    # Process data based on route type
    filtered_ticks = pd.DataFrame()
    if ticks_data is not None and len(ticks_data) > 0:
        c_type = route_selector.value
        handler = handle_generic
        args = [
            ticks_data,
            criteria_send.value,
            date_selector.value[0],
            date_selector.value[1],
            REVERSE_GRADES[max_grade_selector.value],
            grade_ranges[c_type][0],
            grade_ranges[c_type][1]
        ]

        if c_type == 'Roped':
            handler = handle_roped
            args = [
                rope_selector.value,
                ticks_data,
                criteria_send.value,
                date_selector.value[0],
                date_selector.value[1],
                REVERSE_GRADES[max_grade_selector.value],
                multipitch_checkbox.value
            ]
        elif c_type == 'Bouldering':
            handler = handle_boulders
            args = [
                ticks_data,
                criteria_send.value,
                date_selector.value[0],
                date_selector.value[1],
                REVERSE_GRADES[max_grade_selector.value],
                boulder_checkbox.value
            ]

        filtered_ticks = handler(*args)
    return (filtered_ticks,)


@app.cell
def _(mo):
    # Pyramid chart options
    remove_sent = mo.ui.checkbox(label='Remove sent routes from attempts', value=False)
    remove_duplicates = mo.ui.checkbox(label='Remove duplicates', value=False)
    v0_as_half = mo.ui.checkbox(label='Count V0 as 0.5 points', value=False)
    mo.hstack([remove_sent, remove_duplicates, v0_as_half])
    return remove_duplicates, remove_sent, v0_as_half


@app.cell
def _(
    REVERSE_GRADES,
    filtered_ticks,
    generate_pyramid,
    generate_scatter,
    max_grade_selector,
    mo,
    pd,
    px,
    remove_duplicates,
    remove_sent,
    rope_selector,
    route_selector,
    v0_as_half,
):
    import re

    def get_most_common_location(locations):
        """
        Find the most common location from a list of location strings.
        Locations are provided as '>' separated strings.
        Returns the leftmost location that is contained within all locations.
        """
        if not locations or len(locations) == 0:
            return ''
        # Handle NaN values
        locations = [str(loc) if pd.notna(loc) else '' for loc in locations]
        locations = [loc for loc in locations if loc]  # Remove empty strings
        if not locations:
            return ''

        locations_split = [loc.split('>') for loc in locations]
        common_location = locations_split[0]
        for location in locations_split[1:]:
            common_location = [l for l in common_location if l in location]
        return '>'.join(common_location)

    def render_data(data,route_selector):
        display_df = data.copy()
        cols = ['Date','Route','Style','Notes','Location','Length', 'URL']
        _c_type = route_selector.value
        if _c_type != 'Roped':
            cols += ['Pitches']
        # Format the Date column to MM/DD/YYYY
        display_df['Date'] = display_df['Date'].dt.strftime('%m/%d/%Y')
        return mo.ui.dataframe(display_df[cols])

    def calculate_pitches_per_day(ticks, allow_repeats=True):
        """
        Calculate total pitches climbed on each day for non-bouldering routes.

        Args:
            ticks: DataFrame with climbing ticks (must have 'Date', 'Pitches', 'Route', 'Location' columns)
            allow_repeats: If False, only count each route once per day

        Returns:
            DataFrame with columns: Date, TotalPitches, RouteCount, Location
        """
        if ticks is None or len(ticks) == 0:
            return pd.DataFrame(columns=['Date', 'TotalPitches', 'RouteCount', 'Location']), None

        # Filter for non-bouldering routes (Rating Code < 20000 or >= 30000)
        non_boulder_ticks = ticks[~((ticks['Rating Code'] >= 20000) & (ticks['Rating Code'] < 30000))].copy()

        if len(non_boulder_ticks) == 0:
            return pd.DataFrame(columns=['Date', 'TotalPitches', 'RouteCount', 'Location']), None

        # Remove duplicates if not allowing repeats
        if not allow_repeats:
            non_boulder_ticks = non_boulder_ticks.drop_duplicates(subset=['Date', 'Route'], keep='first')

        # Fill NaN pitches with 1 (assuming single pitch if not specified)
        non_boulder_ticks['Pitches'] = non_boulder_ticks['Pitches'].fillna(1)
        # Convert to numeric, handling any string values
        non_boulder_ticks['Pitches'] = pd.to_numeric(non_boulder_ticks['Pitches'], errors='coerce').fillna(1)

        # Group by date and sum pitches
        daily_pitches = non_boulder_ticks.groupby('Date').agg({
            'Pitches': 'sum',
            'Route': 'count'
        }).reset_index()
        daily_pitches.columns = ['Date', 'TotalPitches', 'RouteCount']

        # Add location column using get_most_common_location
        daily_pitches['Location'] = non_boulder_ticks.groupby('Date')['Location'].apply(list).values
        daily_pitches['Location'] = daily_pitches['Location'].apply(get_most_common_location)
        daily_pitches['Routes'] = non_boulder_ticks.groupby('Date')['Route'].apply(list).values

        # Format Date column
        daily_pitches['Date'] = daily_pitches['Date'].dt.strftime('%m/%d/%Y')

        # make a plotly figure of the data
        daily_pitches_fig = px.scatter(daily_pitches, x='Date', y='TotalPitches', hover_data=['Routes', 'Location'])
        return daily_pitches, daily_pitches_fig

    def calculate_vpoints_per_day(ticks, v0_as_half=False, allow_repeats=True):
        """
        Calculate v-points climbed on each day.
        V-points are calculated by extracting the number from V-grades (V0, V1, V2, etc.)
        and summing them per day.

        Args:
            ticks: DataFrame with bouldering ticks (must have 'Date', 'Grade', 'Route' columns)
            v0_as_half: If True, count V0 as 0.5 points instead of 0
            allow_repeats: If False, only count each route once per day

        Returns:
            DataFrame with columns: Date, VPoints, RouteCount
        """
        if ticks is None or len(ticks) == 0:
            return pd.DataFrame(columns=['Date', 'VPoints', 'RouteCount']), None

        # Filter for bouldering routes (Rating Code >= 20000 and < 30000)
        boulder_ticks = ticks[(ticks['Rating Code'] >= 20000) & (ticks['Rating Code'] < 30000)].copy()
        # remove ticks without 'Send' or 'Flash'
        boulder_ticks = boulder_ticks[boulder_ticks['Style'].isin(['Send','Flash'])]

        if len(boulder_ticks) == 0:
            return pd.DataFrame(columns=['Date', 'VPoints', 'RouteCount']), None

        # Remove duplicates if not allowing repeats
        if not allow_repeats:
            boulder_ticks = boulder_ticks.drop_duplicates(subset=['Date', 'Route'], keep='first')

        def extract_v_number(grade_str):
            """Extract the numeric part from a V-grade string."""
            if pd.isna(grade_str):
                return 0

            grade_str = str(grade_str).strip()

            # Handle V-easy or similar
            if 'easy' in grade_str.lower() or grade_str == 'V-easy':
                return 0

            # Extract number after 'V'
            if grade_str.startswith('V'):
                # Remove 'V' prefix
                num_str = grade_str[1:]
                # Extract the first number (handle cases like "V0-", "V0+", "V0-1", "V1-2")
                match = re.search(r'^(\d+)', num_str)
                if match:
                    num = int(match.group(1))
                    # Handle V0 as 0.5 if option is enabled
                    if num == 0 and v0_as_half:
                        return 0.5
                    return num
            return 0

        # Extract v-points from grades
        boulder_ticks['VPoints'] = boulder_ticks['Grade'].apply(extract_v_number)

        # Group by date and sum v-points
        daily_vpoints = boulder_ticks.groupby('Date').agg({
            'VPoints': 'sum',
            'Route': 'count'
        }).reset_index()
        daily_vpoints.columns = ['Date', 'VPoints', 'RouteCount']

        # add a column for the list of the routes climbed on each day
        daily_vpoints['Routes'] = boulder_ticks.groupby('Date')['Route'].apply(list).values
        # add a column to indicate the location of the routes climbed on each day
        daily_vpoints['Location'] = boulder_ticks.groupby('Date')['Location'].apply(list).values
        # aggregate the list of locations by finding the most common location
        daily_vpoints['Location'] = daily_vpoints['Location'].apply(get_most_common_location)

        # Format Date column
        daily_vpoints['Date'] = daily_vpoints['Date'].dt.strftime('%m/%d/%Y')

        # plot the data using plotly
        daily_vpoints_fig = px.scatter(daily_vpoints, x='Date', y='VPoints', hover_data=['Routes', 'Location'])
        return daily_vpoints, daily_vpoints_fig

    # Create v-points display
    if route_selector.value == 'Bouldering' and len(filtered_ticks) > 0 and len(filtered_ticks) > 0:
        # Calculate v-points per day
        vpoints_data, vpoints_fig = calculate_vpoints_per_day(
            filtered_ticks,
            v0_as_half=v0_as_half.value,
            allow_repeats=not remove_duplicates
        )

        if len(vpoints_data) > 0:
            vpoints_display = mo.ui.plotly(vpoints_fig)
        else:
            vpoints_display = mo.md("No bouldering data available for v-points calculation.")
    else:
        vpoints_display = mo.md("Select 'Bouldering' as the climbing type to see v-points calculation.")
    # Create pitches display
    if route_selector.value != 'Bouldering' and len(filtered_ticks) > 0:
        pitches_data, pitches_fig = calculate_pitches_per_day(
            filtered_ticks,
            allow_repeats=not remove_duplicates
            )
        if len(pitches_data) > 0:
            pitches_display = mo.ui.plotly(pitches_fig)
        else:
            pitches_display = mo.md("No non-bouldering data available for pitches calculation.")
    else:
        pitches_display = mo.md("Select a non-bouldering climbing type to see pitches calculation.")

    if filtered_ticks is None or len(filtered_ticks) == 0:
        output = mo.md("No data available. Please upload a CSV file or download data from Mountain Project.")
    else:
        pyramid_fig = generate_pyramid(
                    filtered_ticks,
                    route_selector.value,
                    rope_selector.value if route_selector.value == 'Roped' else [],
                    remove_sent=remove_sent.value,
                    remove_duplicates=remove_duplicates.value)
        scatter_fig = generate_scatter(
                    filtered_ticks,
                    route_selector.value,
                    rope_selector.value if route_selector.value == 'Roped' else [],
                    REVERSE_GRADES[max_grade_selector.value])
        rendered_data = render_data(filtered_ticks, route_selector)
        # Create tabs for visualizations
        tab_dict = {
            "Pyramid": pyramid_fig,
            "Scatter": scatter_fig,
            "Data": rendered_data
        }
        # Add V-Points tab only for bouldering
        if route_selector.value == 'Bouldering':
            tab_dict["V-Points"] = vpoints_display
        # Add Pitches tab for non-bouldering routes
        else:
            tab_dict["Pitches"] = pitches_display
        output = mo.ui.tabs(tab_dict, lazy=True)
    output
    return (get_most_common_location,)


@app.cell
def _(filtered_ticks, get_most_common_location, pd):
    ticks = filtered_ticks.copy()
    # Filter for non-bouldering routes (Rating Code < 20000 or >= 30000)
    non_boulder_ticks = ticks[~((ticks['Rating Code'] >= 20000) & (ticks['Rating Code'] < 30000))].copy()
    # Remove duplicates if not allowing repeats
    if True:
        non_boulder_ticks = non_boulder_ticks.drop_duplicates(subset=['Date', 'Route'], keep='first')

    # Fill NaN pitches with 1 (assuming single pitch if not specified)
    non_boulder_ticks['Pitches'] = non_boulder_ticks['Pitches'].fillna(1)
    # Convert to numeric, handling any string values
    non_boulder_ticks['Pitches'] = pd.to_numeric(non_boulder_ticks['Pitches'], errors='coerce').fillna(1)

    # Group by date and sum pitches
    daily_pitches = non_boulder_ticks.groupby('Date').agg({
        'Pitches': 'sum',
        'Route': 'count'
    }).reset_index()
    daily_pitches.columns = ['Date', 'TotalPitches', 'RouteCount']

    # Add location column using get_most_common_location
    daily_pitches['Location'] = non_boulder_ticks.groupby('Date')['Location'].apply(list).values
    daily_pitches['Location'] = daily_pitches['Location'].apply(get_most_common_location)
    daily_pitches['Routes'] = non_boulder_ticks.groupby('Date')['Location'].apply(list).values

    # Format Date column
    daily_pitches['Date'] = daily_pitches['Date'].dt.strftime('%m/%d/%Y')
    daily_pitches
    return


@app.cell
def _(ticks_data):
    ticks_data
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
