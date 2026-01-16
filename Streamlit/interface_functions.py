import streamlit as st
import pandas as pd
from file_dialog import FileDialog
from sklearn.linear_model import LinearRegression

@st.cache_data
def load_data(start_time, end_time):
    with FileDialog() as db:
        hr_data = db.read_from_db('heart_rate', start_time, end_time)
        steps_data = db.read_from_db('steps', start_time, end_time)
        sleep_data = db.read_from_db('sleep_summaries', start_time, end_time)
        return hr_data, steps_data, sleep_data

@st.cache_data
def get_sleepwalking_nights(df_sleep, df_steps, start_stamp, end_stamp, ):
    sleepwalking_nights = []
    df_sleep_selection = df_sleep[(df_sleep['end'] >= start_stamp) & (df_sleep['end'] <= end_stamp)][['date', 'start', 'end']]
    df_steps_selection = df_steps[(df_steps['timestamp']<end_stamp) & (df_steps['timestamp']>=start_stamp)]
    for row in df_sleep_selection.itertuples():
        current_night_sum = df_steps_selection[(df_steps_selection['timestamp'] < (row.end //3600) * 3600) & (df_steps_selection['timestamp'] >= ((row.start)//3600) * 3600) + 3600]['value'].sum()
        sleepwalking_nights.append((row.date, current_night_sum))
    sleepwalking_df = pd.DataFrame(sleepwalking_nights, columns=['date', 'numsteps'])
    return sleepwalking_df

@st.cache_data
def get_nightly_heartrates(df_sleep, df_heartrate, start_stamp, end_stamp, ):
    nightly_heartrates = []
    df_sleep_selection = df_sleep[(df_sleep['end'] >= start_stamp) & (df_sleep['end'] <= end_stamp)][
        ['date', 'start', 'end']]
    df_heartrate_selection = df_heartrate[(df_heartrate['timestamp'] < end_stamp) & (df_heartrate['timestamp'] >= start_stamp)]
    for row in df_sleep_selection.itertuples():
        current_night_mean = df_heartrate_selection[(df_heartrate_selection['timestamp'] < row.end)  & (df_heartrate_selection['timestamp'] >= row.start)]['value'].mean()
        nightly_heartrates.append((row.date, current_night_mean))
    nightly_heartrates_df = pd.DataFrame(nightly_heartrates, columns=['date', 'mean'])
    return nightly_heartrates_df

def filter_sleepwalking_data(sleepwalking_df, start_stamp, end_stamp, threshold):
    sleepwalking_df = pd.DataFrame(sleepwalking_df[(sleepwalking_df['date'] >= start_stamp) & (sleepwalking_df['date'] < end_stamp)])
    sleepwalking_df['status'] = sleepwalking_df['numsteps'] >= threshold
    return sleepwalking_df

def get_trend(xcol, ycol):
    model = LinearRegression()
    model.fit(xcol, ycol)
    slope = model.coef_[0]
    trend = slope * (xcol.max() - xcol.min())
    return float(trend.iloc[0])







