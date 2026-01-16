from charts import *
from interface_functions import *
from datetime import datetime, timedelta, timezone
from manager import Manager
import os
#setup
days_back = int(os.environ.get('DASHBOARD_DAYS_BACK', 30))
END_DATE = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days = 1)
START_DATE =	END_DATE - timedelta(days = days_back)
manager = Manager()
#ui setup
st.set_page_config(page_title='my_health_dashboard', layout = 'wide', page_icon= ':heartpulse:', initial_sidebar_state='expanded')

#FUll CACHED DATA
HR, STEPS, SLEEP_SUMMARIES = load_data(START_DATE.timestamp(), END_DATE.timestamp())
sleepwalking_data = get_sleepwalking_nights(df_sleep= SLEEP_SUMMARIES, df_steps= STEPS, start_stamp = START_DATE.timestamp(), end_stamp = END_DATE.timestamp())
nightly_heartrates_data = get_nightly_heartrates(df_sleep= SLEEP_SUMMARIES, df_heartrate= HR, start_stamp = START_DATE.timestamp(), end_stamp = END_DATE.timestamp())


#this hides the boxes for swapping charts for dataframe views
st.markdown("""
    <style>
    [data-testid="stElementToolbar"] {
        display: none ;
    }
    </style>
""", unsafe_allow_html=True)



with st.sidebar:
    update_button = st.button(label = 'Update the data', icon = ':material/refresh:')
    if update_button:
        manager.update_all_data()
    st.header('File exporting')
    file_type_option = st.selectbox('Choose the desired file format', options = ['xlsx','csv'], accept_new_options=False)
    separator = ';'
    if file_type_option == 'csv':
        separator = st.segmented_control(label='Choose the separator', options=[';', ','], default=';')
    data_type_options = st.pills('Choose the parameters to be downloaded',options=['Heart rate', 'Hourly step counts', 'Sleep summaries'], selection_mode='multi')
    data_types_map = {'Heart rate': 'heart_rate','Hourly step counts': 'steps', 'Sleep summaries': 'sleep_summaries'}
    start = st.date_input('Enter a start date', min_value = START_DATE, max_value = END_DATE, key = 95)
    end = st.date_input('Enter an end date', min_value=START_DATE, max_value=END_DATE, key=96)
    download_button = st.button(label='Export your dataset', icon=':material/download:', key =77)
    #converting to timestamps
    start_midnight= datetime.combine(start, datetime.min.time())
    start_midnight = start_midnight.replace(tzinfo = timezone.utc)
    end_midnight = datetime.combine(end, datetime.min.time())
    end_midnight = end_midnight.replace(tzinfo = timezone.utc)
    if download_button:
        for dtype in data_type_options:
            manager.export_to_file(data_types_map[dtype], start_midnight.timestamp(), end_midnight.timestamp(), str(data_types_map[dtype]) +start.strftime('%Y%m%d') + end.strftime('%Y%m%d'), file_format=file_type_option, separator= separator )


row0 = st.columns(1)

with row0[0]:
    with st.container(border = False):
        st.markdown("<h1 style='text-align: center;'>Your health and activity data, in a single place</h1>", unsafe_allow_html=True)

row1 = st.columns(2)

with row1[0]:
    with st.container(height=600, border = True):
        st.markdown("<h3 style='text-align: center;'>Sleep quality</h3>", unsafe_allow_html=True)
        slider_sleep_start,slider_sleep_end = st.slider('Select the time frame', value=[START_DATE + timedelta(days = 2),END_DATE - timedelta(days = 2)],format="DD/MM/YY", key =32, min_value = START_DATE, max_value = END_DATE - timedelta(days = 1))
        #converting to timestamps and filtering
        slider_sleep_start = slider_sleep_start.timestamp()
        slider_sleep_end = slider_sleep_end.timestamp()
        relevant_sleep_data = SLEEP_SUMMARIES[(SLEEP_SUMMARIES['end']<=slider_sleep_end) & (SLEEP_SUMMARIES['start']>=slider_sleep_start) ]
        df_sleep_chart = pd.DataFrame(relevant_sleep_data)

        st.altair_chart(sleep_chart(df_sleep_chart))

with row1[1]:
    with st.container(height=600, border = True, key ='c2'):
        st.markdown("<h3 style='text-align: center;'>Detect sleepwalking</h3>", unsafe_allow_html=True)
        selected_date = st.slider(label = 'Select the start of the week:',min_value=START_DATE,max_value=END_DATE - timedelta(days = 1),value=START_DATE,step=timedelta(weeks=1),format="YYYY-MM-DD"
        )
        threshold = st.number_input("Enter the threshold (in no. of steps between bed and rise time)", min_value=0, value=50, step=1)
        #converting to timestamps and filtering
        selected_date = selected_date.timestamp()
        chart_sleep_data =filter_sleepwalking_data(sleepwalking_data, selected_date, (selected_date + (7 * 24 * 60 * 60)), threshold)

        st.altair_chart(sleepwalking_chart(chart_sleep_data))


row2 = st.columns(2)

with row2[0]:
    with st.container(height=550, border = True, key ='c3'):
        st.markdown("<h3 style='text-align: center;'>Your daily activity</h3>", unsafe_allow_html=True)
        slider_steps_dt = st.slider('Select the day', value=END_DATE - timedelta(days=2), format="DD/MM/YY", min_value = START_DATE, max_value=END_DATE - timedelta(days = 1))
        slider_steps = slider_steps_dt.timestamp()
        #slider in local time, correction for +1 gmt
        steps_data = pd.DataFrame(STEPS[(STEPS['timestamp'] >= slider_steps + 3600) & (STEPS['timestamp'] < (slider_steps + 86400 + 360))])
        steps_data['timestamp'] = (steps_data['timestamp'] % 86400) // 3600
        st.altair_chart(create_fixed_axis_area_chart(steps_data))

with row2[1]:
    with st.container(height=550, border = True, key ='c4'):
        st.markdown("<h3 style='text-align: center;'>Monitor your nightly heartrate</h3>", unsafe_allow_html=True)
        slider_hr_start, slider_hr_end = st.slider('Select the time frame', value=[START_DATE + timedelta(days = 2), END_DATE - timedelta(days = 2)],
                                                   format="DD/MM/YY", key=33, min_value= START_DATE, max_value=END_DATE - timedelta(days = 1))
        #timestamps, filtering, calling the trend function
        slider_hr_start = slider_hr_start.timestamp()
        slider_hr_end = slider_hr_end.timestamp()
        selected_heartrates = pd.DataFrame(nightly_heartrates_data[
                                               (nightly_heartrates_data['date'] >= slider_hr_start) & (
                                                       nightly_heartrates_data['date'] < slider_hr_end)])
        trend = get_trend(selected_heartrates[['date']], selected_heartrates['mean'])

        nightly_heartrates_chart = vitality_chart(selected_heartrates, trend)
        st.altair_chart(nightly_heartrates_chart)
