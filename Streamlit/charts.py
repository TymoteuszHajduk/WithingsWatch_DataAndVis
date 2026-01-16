import altair as alt
import pandas as pd
from datetime import  timedelta

def sleep_chart(df_sleep_chart):
    #CHART 1
    df_sleep_chart['stages_sum'] = df_sleep_chart['lightsleepduration'] + df_sleep_chart['remsleepduration'] + df_sleep_chart['deepsleepduration']
    # If Total > Sum, the remainder is WASO.
    df_sleep_chart['calc_waso'] = df_sleep_chart['total_sleep_time'] - df_sleep_chart['stages_sum']
    df_sleep_chart['calc_waso'] = df_sleep_chart['calc_waso'].clip(lower=0)  # Ensure no negative numbers

    # B. Time Handling (The "Looping" Logic)
    # Convert Date to string for X-axis
    df_sleep_chart['date_str'] = pd.to_datetime(df_sleep_chart['date'], unit='s').dt.strftime('%Y-%m-%d')

    # Get Start Hour (0-24)
    df_sleep_chart['start_h'] = (df_sleep_chart['start'] % 86400) / 3600

    # Normalize for Plotting (Continuous Scale)
    # If start is before Noon (e.g. 01:00), add 24 so it sits *after* 23:00 of previous day
    # Logic: If hour < 12, it belongs to "next morning" (add 24).
    df_sleep_chart['start_plot'] = df_sleep_chart['start_h'].apply(lambda x: x + 24 if x < 12 else x)

    # 3. Melt to Long Format (Creating Segments)
    # We include our calculated WASO in the melt
    df_long = df_sleep_chart.melt(
        id_vars=['date_str', 'start_plot', 'total_sleep_time'],
        value_vars=['deepsleepduration', 'remsleepduration', 'lightsleepduration', 'calc_waso'],
        var_name='stage_raw',
        value_name='duration_seconds'
    )

    # Filter out zero-duration segments (cleaner chart)
    df_long = df_long[df_long['duration_seconds'] > 0]

    # Map Names
    stage_map = {
        'deepsleepduration': 'Deep',
        'remsleepduration': 'REM',
        'lightsleepduration': 'Light',
        'calc_waso': 'Awake'
    }
    df_long['Stage'] = df_long['stage_raw'].map(stage_map)

    # Convert duration to hours for stacking
    df_long['duration_h'] = df_long['duration_seconds'] / 3600
    df_long['share'] = df_long['duration_seconds'] / df_long['total_sleep_time']

    # 4. Calculate Stacking Positions
    # Define Order: Deep -> REM -> Light -> Awake (Bottom to Top)
    stage_order = ['Deep', 'REM', 'Light', 'Awake']
    df_long['Stage'] = pd.Categorical(df_long['Stage'], categories=stage_order, ordered=True)
    df_long = df_long.sort_values(['date_str', 'Stage'])


    df_long['cum_dur'] = df_long.groupby('date_str')['duration_h'].cumsum()
    df_long['prev_cum_dur'] = df_long.groupby('date_str')['duration_h'].shift(1).fillna(0)

    df_long['y_bottom'] = df_long['start_plot'] + df_long['prev_cum_dur']
    df_long['y_top'] = df_long['start_plot'] + df_long['cum_dur']

    # 5. Altair Chart with Custom Axis
    # Colors: Bleak/Scientific
    scale_colors = alt.Scale(
        domain=['Deep', 'REM', 'Light', 'Awake'],
        range=['#2C3E50', '#778899', '#B0C4DE', '#E0E0E0']
    )

    chart = alt.Chart(df_long).mark_bar(width=40).encode(
        x=alt.X('date_str:N', title='Date', axis=alt.Axis(labelAngle=0)),

        # Y-Axis: We use the continuous values (22, 23, 24, 25...)
        # But we us 'labelExpr' to modulo them by 24 for the display labels
        y=alt.Y('y_bottom:Q',
                title='Time',
                scale=alt.Scale(zero=False, domain=[21, 34]),  # Adjust domain to fit your sleep window
                axis=alt.Axis(
                    tickCount=12,
                    # THIS is the magic line for looping labels:
                    labelExpr="datum.value % 24"
                )
                ),
        y2='y_top:Q',

        color=alt.Color('Stage:N', scale=scale_colors, legend=alt.Legend(orient='bottom')),

        tooltip=[
            alt.Tooltip('Stage', title='Stage'),
            alt.Tooltip('share', format='.1%', title='Share'),
        ]
    ).properties(
        width=300,
        height=400
    )
    return chart



def create_fixed_axis_area_chart(df):
    #CHART 2
    primary_color = "#325d88"

    # 1. Define Gradient
    gradient = alt.Gradient(
        gradient='linear',
        stops=[
            alt.GradientStop(offset=0, color=primary_color),
            alt.GradientStop(offset=1, color='white')
        ],
        x1=1, x2=1, y1=1, y2=0
    )

    # 2. Calculate Dynamic Axis Values
    print(df)
    # Y-AXIS: 1000-step intervals
    max_val = df['value'].max()
    y_ticks = list(range(0, int(max_val) + 2000, 1000))

    # X-AXIS: Strictly every 4 hours
    # We find the start and end of your data to generate the correct ticks


    # Generate a list of timestamps: 00:00, 04:00, 08:00...
    # We align 'start' to the floor of the hour to ensure clean ticks
      # Starts at midnight of the first day
    x_tick_values =  list(range(df['timestamp'].min(), df['timestamp'].max() + 1, 4))


    # 3. Base Chart
    base = alt.Chart(df).encode(
        x=alt.X('timestamp:Q',
                axis=alt.Axis(
                    title=None,
                    grid=False,
                    domain=True,  # Ensure the bottom axis line is visible
                    domainColor='gray',
                    # FORCE the specific ticks here:
                    values=x_tick_values,
                     labelExpr = "format(datum.value, '02d') + ':00'"
                ))
    )

    # 4. Layer 1: The Area (Gradient Fill, No Top Line)
    area = base.mark_area(line=False, opacity=0.99).encode(
        y=alt.Y('value:Q',
                # Enforce Y-axis 1000 steps
                axis=alt.Axis(values=y_ticks, title=None, grid=True, domain=False),
                scale=alt.Scale(domain=[0, max_val + 500]),
                ),
        color=alt.value(gradient)
    )

    # 5. Layer 2: Invisible Tooltip Interaction
    selection = alt.selection_point(fields=['timestamp'], nearest=True, on='mouseover', empty='none', clear='mouseout')

    points = base.mark_circle(opacity=0).encode(
        y='value:Q',
        tooltip=[alt.Tooltip('value', title='Steps', format=',.0f')]
    ).add_params(
        selection
    )

    # 6. Layer 3: Vertical Cursor Rule
    rule = base.mark_rule(color='gray', strokeWidth=0.5, opacity=0.5).encode(
        y='value:Q',
        opacity=alt.condition(selection, alt.value(0.5), alt.value(0))
    ).transform_filter(
        selection
    )
    step_total = df['value'].sum()
    strtotal = 'Steps: ' + str(step_total)
    label = alt.Chart(pd.DataFrame({'text': [strtotal]})).mark_text(

        align='right',
        baseline='top',
        fontSize=20,
        fontWeight='bold'
    ).encode(

        x=alt.value(300),
        y=alt.value(10),
        text='text'
    )
    # Combine
    chart = alt.layer(area,points, rule, label).properties(
        width=600,
        height=300,

    ).configure_view(
        stroke=None
    ).configure_axis(
        labelFont='Lato, Helvetica, Arial, sans-serif',
        labelColor='gray',
        gridColor='#f0f0f0'
    )

    return chart


def sleepwalking_chart(df):
    #CHART 3
    df['datetime'] = pd.to_datetime(df['date'], unit='s')

    # Logic to create the specific "{Day}/{Next Day}" label
    # We map weekday numbers to short names, then format the string
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    df['label'] = df['datetime'].apply(
        lambda x: f"{days[x.weekday()]}/{days[(x.weekday() + 1) % 7]}"
    )
    df['datetime_show'] = df['datetime'].dt.strftime('%Y-%m-%d') + '/' + (df['datetime'] + timedelta(days=1)).dt.strftime('%Y-%m-%d')

    # 2. ALTAIR CHART LOGIC
    # ---------------------------------------------------------

    # Color Palette Definition
    # 'scientific_bg': A very dark, desaturated navy/black
    # 'true_red': A sharp, slightly deep red for 'True'
    # 'false_white': Pure white for 'False'
    scientific_bg = "#0B1019"
    text_color = "#6E88A3"  # Muted blue-grey for labels
    true_red = "#D32F2F"  # Classy, non-neon red
    false_white = "#FFFFFF"

    sleepwalking_chart = alt.Chart(df).mark_rect(
        stroke="#2C3E50",  # Thin frame color (dark blue-grey)
        strokeWidth=1  # Thin frame
    ).encode(
        # X-Axis: Use the generated label, sorted by the original date
        x=alt.X('label:N',sort=alt.EncodingSortField(field="date", order="ascending"),
            axis=alt.Axis(
                title=None,
                labelAngle=0,
                labelColor=text_color,
                labelFont="Roboto Mono, monospace",  # Scientific font look
                domain=False,  # Remove axis line
                ticks=False  # Remove ticks

            )
        ),

        # Y-Axis: Hidden, just to give the bar some height if needed,
        # or you can rely on view config. Here we just keep it clean.

        # Color: Mapped strictly to Status
        color=alt.Color(
            'status:N',
            scale=alt.Scale(
                domain=[True, False],
                range=[true_red, false_white]
            ),
            legend=None  # Hide legend for cleaner look
        ),

        # Tooltip for context
        tooltip=alt.Tooltip('datetime_show', title='date')
    ).properties(
        width=600,
        height=80,  # Strip layout
        background=scientific_bg,
        padding={'left': 20, 'top': 20, 'right': 20, 'bottom': 20}
    ).configure_view(
        strokeWidth=0  # Removes the outer box around the whole chart
    )
    return sleepwalking_chart
def vitality_chart(df, trend_var):
   #CHART 4
    # 1. Pre-processing: Ensure date is datetime
    # We create a copy to avoid modifying the original dataframe
    chart_df = df.copy()
    if not pd.api.types.is_datetime64_any_dtype(chart_df['date']):
        chart_df['date_dt'] = pd.to_datetime(chart_df['date'], unit='s')
    else:
        chart_df['date_dt'] = chart_df['date']

    # Calculate bounds for the background rectangles so they fit the frame exactly
    min_date = chart_df['date_dt'].min()
    max_date = chart_df['date_dt'].max()

    # Define Axis Limits
    y_min, y_max = 40, 120

    # 2. Define the Background Zones Data
    # Colors: Dark Green (<55), Fresh Green (55-80), Intense Brown (>80)
    zones = pd.DataFrame([
        {'start': 40, 'end': 55, 'color': '#006400'},  # Deep Vitality
        {'start': 55, 'end': 80, 'color': '#0EC410'},  # Fresh Vitality
        {'start': 80, 'end': 120, 'color': '#FF6808'}  # Warning/Rotten
    ])
    # Add date bounds to zones so they stretch across the chart perfectly
    zones['x_start'] = min_date
    zones['x_end'] = max_date

    # Layer A: Background Zones
    background = alt.Chart(zones).mark_rect(opacity=0.6).encode(
        y=alt.Y('start:Q', scale=alt.Scale(domain=[y_min, y_max])),
        y2='end:Q',
        x='x_start:T',
        x2='x_end:T',
        color=alt.Color('color:N', scale=None),
        tooltip=alt.value(None)

    )

    # Layer B: Thin Separator Lines (at 55 and 80)
    separators = alt.Chart(pd.DataFrame({'y': [55, 80]})).mark_rule(
        color='black', strokeWidth=0.5, opacity=0.4
    ).encode(y='y:Q')

    # Layer C: The Main Data Line
    line = alt.Chart(chart_df).mark_line(
        color='black', size=2
    ).encode(
        x=alt.X('date_dt:T', axis=alt.Axis(title=None, labels=False, grid=False)),
        y=alt.Y('mean:Q',
                scale=alt.Scale(domain=[y_min, y_max]),
                axis=alt.Axis(title='Average asleep heart rate', grid=False)),
        tooltip = alt.value(None),
    )
    if trend_var >= 0:
        arrow = "↗"
    else:
        arrow = "↘"

        # Format: "Trend: ↘ 5.2" (using absolute value)
    trend_text = f"Trend: {arrow} {abs(trend_var):.1f}"
    # Layer D: Trend Text Label
    # Positioned relative to the data (top left corner)
    text_data = pd.DataFrame({
        'x': [min_date],
        'y': [118],  # Position near the top limit (120)
        'text': [trend_text]
    })

    text = alt.Chart(text_data).mark_text(
        align='left',
        baseline='top',
        dx=5,  # Offset 5 pixels from the left edge
        dy=5,  # Offset 5 pixels from the top
        fontWeight='bold',
        fontSize=12
    ).encode(
        x='x:T',
        y='y:Q',
        text='text:N'
    )

    # Combine and configure interaction
    return (background + separators + line + text).properties(
        width=600,
        height=300,

    )

