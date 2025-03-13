import base64
import io
from datetime import date

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from figures import generate_pyramid, generate_scatter
from grades import GRADES, REVERSE_GRADES

# convert the marimo_app.py to a streamlit app
# write the streamlit app below

if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame()

st.set_page_config(layout='wide')
# Title
st.title('Mountain Project Visualization App')
interface, graphs = st.columns([0.4,0.6])

@st.cache_data
def get_data(mp_url):
    assert mp_url.startswith('https://www.mountainproject.com/user/'), f"Invalid URL:{mp_url}"
    mp_url += '/tick-export'
    page = requests.get(mp_url)
    if page.ok:
        assert page.status_code == 200, f"Invalid URL: {mp_url}"
    decoded = io.StringIO(page.text)
    downloaded_ticks = pd.read_csv(decoded, parse_dates=['Date'])
    return downloaded_ticks

@st.cache_data
def csv_to_df(uploaded_file):
    if uploaded_file is not None:
        return pd.read_csv(uploaded_file, parse_dates=['Date'])
    return None
with interface:
    # textbox for MP URL
    # mp_url = st.text_input('Enter the URL of the Mountain Project page you want to analyze:', 'https://www.mountainproject.com/user/USRNUM/USER-NAME', key='url', help='Enter the URL of the Mountain Project user page you want to analyze.')
    # # button to submit the URL
    # button = st.button('Submit', on_click=get_data, args=(mp_url,))

    # create a file uploader for the user to upload their tick data
    uploaded_file = st.file_uploader('Upload your tick data:', type=['csv'], key='file')
    st.session_state.data = csv_to_df(uploaded_file) if uploaded_file is not None else st.session_state.data
    data = st.session_state.data

    # if the button is clicked and the URL is not empty, then run get_data()
    # data = get_data(mp_url) if mp_url != 'https://www.mountainproject.com/user/USRNUM/USER-NAME' else None

    # if data is not None, then run the following code
    start_date = date(1960,1,1)
    end_date = date.today()
    def get_min_date(data):
        return data['Date'].min().date()
    if len(st.session_state.data):
        start_date = get_min_date(data)
    # create a date range selector from start_date to end_date
    date_range = st.date_input('Date Range:', (start_date,end_date), min_value=start_date, max_value=end_date, key='date_range', on_change=csv_to_df, args=(uploaded_file,))

    # create a list of radio buttons for the user to select the climbing type
    climbing_type = st.radio('Select Climbing Type:', ['Roped :knot::mountain:', 'Bouldering :rock:','Ice :ice_cube:','Mixed','Aid','Snow :snowflake:'], key='climbing_type', on_change=csv_to_df, args=(uploaded_file,))
    def update_send_dropdown(data, route_type):
        # find the max 'Rating Code' from the ticks data
        if route_type == 'Roped':
            # the max grade is the highest value in the 'Rating Code' column that is less than 20000
            max_grade = data['Rating Code'][data['Rating Code'] < 20000].max()
            grades = {value:key for key,value in GRADES.items() if value.startswith('5') and key <= max_grade}
            return grades, GRADES[max_grade]
        max_grade = data['Rating Code'][(data['Rating Code'] < 30000) & (data['Rating Code'] >= 20000)].max()
        boulder_grades = {value: key for key,value in GRADES.items() if value.startswith('V') and key <= max_grade}
        return boulder_grades, GRADES[max_grade]
    def update_route_type(route_type, ticks_data):
        if ticks_data is None:
            if route_type == 'Roped':
                grade_options = {value:key for key,value in GRADES.items() if value.startswith('5')}
                max_grade = '5.12c'
            grade_options = {value:key for key,value in GRADES.items() if value.startswith('V')}
            max_grade = 'V9'
        else:
            grade_options, max_grade = update_send_dropdown(ticks_data, route_type)
        if route_type == 'Roped':
            return grade_options, max_grade, ['Onsight', 'Flash', 'Redpoint', 'Pinkpoint', 'Fell/Hung', 'N/A'], ['Onsight', 'Flash', 'Redpoint','Fell/Hung']
        return grade_options, max_grade, ['Send', 'Attempt','Flash'], ['Send','Flash','Attempt']
    if len(data):
        grade_options, max_grade, send_options, send_value = update_route_type(climbing_type.split()[0], data)
    # based on the climbing_type selected, generate a pills list for the user to select the rope type
        climb_type = st.pills('Select Rope Type', send_options, selection_mode='multi', key='climb_type', default=send_value, on_change=csv_to_df, args=(uploaded_file,))
        # create a slider for the user to select the max grade
        criteria_max = st.select_slider('Select Max Grade:', options=list(grade_options.keys()), key='criteria_max', value=max_grade, on_change=csv_to_df, args=(uploaded_file,))

        c_type = climbing_type.split()[0]
        r_type, c_multi, c_boulder = [], False, False
        if c_type == 'Roped':
            # add another multi pills list for the user to select the type of roped climbing
            rope_type = st.pills('Rope Type', ['Sport','Trad','TR'], selection_mode='multi', key='rope_type', default=['Sport'], on_change=csv_to_df, args=(uploaded_file,))
            # add a checkbox for including multipitch climbs
            criteria_multi = st.checkbox('Include Multipitch Climbs', key='criteria_multi', on_change=csv_to_df, args=(uploaded_file,))
            r_type = st.session_state.rope_type
            c_multi = st.session_state.criteria_multi
            c_boulder = False
        elif c_type == 'Bouldering':
            # add a checkbox for including boulder grades
            criteria_boulder = st.checkbox('Combine -,+, and normal grades', key='criteria_boulder', on_change=csv_to_df, args=(uploaded_file,))
            c_boulder = st.session_state.criteria_boulder

# generate a pyramid based on the climbing type
with graphs:
    if not len(data):
        st.write('No data available')
        st.stop()
    # generate tabs for the user to select the type of visualization
    data_tab, pyramid_tab, scatter_tab = st.tabs(['Data','Pyramid','Scatter'])
    with data_tab:
        if len(st.session_state.data):
            st.write(data)
    with scatter_tab:
        figure = generate_scatter(data, c_type, r_type, st.session_state.climb_type, st.session_state.date_range[0], st.session_state.date_range[1], REVERSE_GRADES[st.session_state.criteria_max], c_multi, c_boulder)
        st.plotly_chart(figure, key='scatter')
    with pyramid_tab:
        figure = generate_pyramid(data, c_type, r_type, st.session_state.climb_type, st.session_state.date_range[0], st.session_state.date_range[1], REVERSE_GRADES[st.session_state.criteria_max], c_multi, c_boulder)
        st.plotly_chart(figure, key='pyramid')
