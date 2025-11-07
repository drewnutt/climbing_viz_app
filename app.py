import base64
import io
from datetime import date

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from figures import generate_pyramid, generate_scatter
from grades import GRADES, REVERSE_GRADES
from data_cleaning import handle_roped, handle_boulders, handle_generic
# from pyodide.http import pyxhr as requests
# try:
# except ImportError:
# import requests


grade_ranges = {
    'Roped': (0, 20000),
    'Bouldering': (20000, 30000),
    'Ice': (30000, 50000),
    'Mixed': (50000, 70000),
    'Aid': (70000, 80000),
    'Snow': (80000, 90000)
}

if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame()
    st.session_state.ticks = pd.DataFrame()

st.set_page_config(layout='wide')
# Title
st.title('Mountain Project Visualization App')
interface, graphs = st.columns([0.4,0.6])

# still doesn't work in pyodide
# @st.cache_data
# def get_data(mp_url):
#     assert mp_url.startswith('https://www.mountainproject.com/user/'), f"Invalid URL:{mp_url}"
#     mp_url += '/tick-export'
#     page = requests.get(mp_url, headers={'Origin': 'null'})
#     if page.ok:
#         assert page.status_code == 200, f"Invalid URL: {mp_url}"
#     decoded = io.StringIO(page.text)
#     downloaded_ticks = pd.read_csv(decoded, parse_dates=['Date'])
#     st.session_state.data = downloaded_ticks
#     st.session_state.downloaded = True
#     return downloaded_ticks

@st.cache_data
def csv_to_df(uploaded_file):
    if uploaded_file is not None:
        return pd.read_csv(uploaded_file, parse_dates=['Date'])
    return None
with interface:
    # textbox for MP URL
    # mp_url = st.text_input('Enter the URL of the Mountain Project page you want to analyze:', placeholder='https://www.mountainproject.com/user/USRNUM/USER-NAME', key='url', help='Enter the URL of the Mountain Project user page you want to analyze.')
    # # # button to submit the URL
    # st.button('Submit', on_click=get_data, args=(mp_url,))
    # st.write('OR')

    # create a file uploader for the user to upload their tick data
    st.write('Download your tick data from Mountain Project and upload it here:')
    uploaded_file = st.file_uploader('Upload your tick data:', type=['csv'], key='file')
    st.session_state.data = csv_to_df(uploaded_file) if uploaded_file is not None else st.session_state.data

    # if the button is clicked and the URL is not empty, then run get_data()
    # data = get_data(mp_url) if mp_url != 'https://www.mountainproject.com/user/USRNUM/USER-NAME' else None

    # if data is not None, then run the following code
    start_date = date(1960,1,1)
    end_date = date.today()
    def get_min_date(data):
        return data['Date'].min().date()
    if len(st.session_state.data):
        start_date = get_min_date(st.session_state.data)
    # create a date range selector from start_date to end_date
    date_range = st.date_input('Date Range:', (start_date,end_date), min_value=start_date, max_value=end_date, key='date_range')

    # create a list of radio buttons for the user to select the climbing type
    climbing_type = st.radio('Select Climbing Type:', ['Roped :mount_fuji:', 'Bouldering','Ice','Mixed','Aid','Snow :snowflake:'], key='climbing_type', args=(uploaded_file,))
    def update_send_dropdown(data, route_type):
        # find the max 'Rating Code' from the ticks data
        min_code, max_code = grade_ranges[route_type]
        max_grade = data['Rating Code'][(data['Rating Code'] >= min_code) & (data['Rating Code'] < max_code)].max()
        grades = {value: key for key, value in GRADES.items() if key < max_code and key >= min_code}
        if pd.isna(max_grade):
            max_grade = max(grades.values())
        return grades, GRADES[max_grade]
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
        
        if ticks_data is None:
            if isinstance(prefix, tuple):
                grade_options = {value: key for key, value in GRADES.items() if any(value.startswith(p) for p in prefix)}
            else:
                grade_options = {value: key for key, value in GRADES.items() if value.startswith(prefix)}
            max_grade = default_max
        else:
            grade_options, max_grade = update_send_dropdown(ticks_data, route_type)
        return grade_options, max_grade, send_opts, send_vals
    if len(st.session_state.data):
        grade_options, max_grade, send_options, send_value = update_route_type(climbing_type.split()[0], st.session_state.data)
    # based on the climbing_type selected, generate a pills list for the user to select the rope type
        climb_type = st.pills('Select Rope Type', send_options, selection_mode='multi', key='climb_type', default=send_value)
        # create a slider for the user to select the max grade
        criteria_max = st.select_slider('Select Max Grade:', options=list(grade_options.keys()), key='criteria_max', value=max_grade)

        c_type = climbing_type.split()[0]
        r_type, c_multi, c_boulder = [], False, False
        if c_type == 'Roped':
            # add another multi pills list for the user to select the type of roped climbing
            rope_type = st.pills('Rope Type', ['Sport','Trad','TR'], selection_mode='multi', key='rope_type', default=['Sport'])
            # add a checkbox for including multipitch climbs
            criteria_multi = st.checkbox('Include Multipitch Climbs', key='criteria_multi')
            r_type = st.session_state.rope_type
            c_multi = st.session_state.criteria_multi
            c_boulder = False
        elif c_type == 'Bouldering':
            # add a checkbox for including boulder grades
            criteria_boulder = st.checkbox('Combine -,+, and normal grades', key='criteria_boulder')
            c_boulder = st.session_state.criteria_boulder

        # create a ticks dataframe based on the currently selected options
        if len(st.session_state.data):
            handler = handle_generic
            args = [st.session_state.data, st.session_state.climb_type, st.session_state.date_range[0], st.session_state.date_range[1], REVERSE_GRADES[st.session_state.criteria_max], grade_ranges[c_type][0], grade_ranges[c_type][1]]
            if c_type == 'Roped':
                handler = handle_roped
                args = [st.session_state.rope_type, st.session_state.data, st.session_state.climb_type, st.session_state.date_range[0], st.session_state.date_range[1], REVERSE_GRADES[st.session_state.criteria_max], st.session_state.criteria_multi]
            elif c_type == 'Bouldering':
                handler = handle_boulders
                args = [st.session_state.data, st.session_state.climb_type, st.session_state.date_range[0], st.session_state.date_range[1], REVERSE_GRADES[st.session_state.criteria_max], st.session_state.criteria_boulder]
            

            ticks = handler(*args)
            st.session_state.ticks = ticks


# generate a pyramid based on the climbing type
with graphs:
    if not len(st.session_state.data):
        st.write('No data available')
        st.stop()
    # generate tabs for the user to select the type of visualization
    pyramid_tab, scatter_tab, data_tab = st.tabs(['Pyramid','Scatter', 'Data'])
    with data_tab:
        if len(st.session_state.ticks):
            display_df = st.session_state.ticks.copy()
            cols = ['Date','Route','Style','Notes','Location','Length', 'URL']
            # ,'Grade'
            if c_type != 'Roped':
                cols += ['Pitches']
            # format the Date column to MM/DD/YYYY
            display_df['Date'] = display_df['Date'].dt.strftime('%m/%d/%Y')
            # write the types of each column
            st.dataframe(display_df[cols])

            # Can't use this with stlite yet
            # st.dataframe(display_df, hide_index=True, column_order=cols,
            #              column_config={
            #                  'Date': st.column_config.DateColumn('Date of Climb', format='MMM D YYYY', pinned=True),
            #                  'Route': st.column_config.TextColumn('Route Name', pinned=True),
            #                  'URL': st.column_config.LinkColumn('Mountain Project Link', display_text='MP Link'),
            #                  })

    with scatter_tab:
        figure = generate_scatter(st.session_state.ticks, c_type, r_type, REVERSE_GRADES[st.session_state.criteria_max])
        st.plotly_chart(figure, key='scatter')
    with pyramid_tab:
        cb1, cb2 = st.columns([0.5,0.5])
        with cb1:
            st.checkbox('Remove sent routes from attempts', key='remove_sent')
        with cb2:
            st.checkbox('Remove duplicates', key='remove_duplicates')
        figure = generate_pyramid(st.session_state.ticks, c_type, r_type,
                                  remove_sent=st.session_state.remove_sent, remove_duplicates=st.session_state.remove_duplicates)
        st.plotly_chart(figure, key='pyramid')
