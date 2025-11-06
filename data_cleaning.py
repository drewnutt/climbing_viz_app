import pandas as pd
from grades import GRADES

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

def handle_generic(ticks, criteria_send, start_date, end_date, criteria_max, min_code, max_code):
    ticks = ticks[(ticks['Rating Code'] >= min_code) & (ticks['Rating Code'] < max_code)]
    ticks = ticks.loc[ticks['Style'].isin(criteria_send)]
    ticks = filter_time(ticks, start_date, end_date)
    ticks = ticks.loc[ticks['Rating Code'] <= criteria_max, :]
    ticks['Grade'] = pd.cut(
        ticks['Rating Code'],
        bins=[0] + [key for key in GRADES.keys() if (key <= criteria_max) & (key >= min_code)],
        labels=[value for key, value in GRADES.items() if (key <= criteria_max) & (key >= min_code)])
    return ticks
