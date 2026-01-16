request_config =  {
    "heart_rate": {
        'url': 'https://wbsapi.withings.net/v2/measure',
        'params': {
            'action': 'getintradayactivity',
            'data_fields': 'heart_rate'
        }
    },
    "steps": {
        'url': 'https://wbsapi.withings.net/v2/measure',
        'params': {
            'action': 'getintradayactivity',
            'data_fields': 'steps'
        }
    },

    "sleep_summary": {
        'url': 'https://wbsapi.withings.net/v2/sleep',
        'params': {
            'action': 'getsummary',
            'data_fields': 'sleep_score,total_sleep_time,deepsleepduration,remsleepduration,lightsleepduration,breathing_disturbances_intensity,waso'
        }
    }
}
read_queries_config = {
    'heart_rate' : 'SELECT * FROM heart_rate WHERE (timestamp >= :start) AND (timestamp < :end)',
    'steps' : 'SELECT * FROM steps WHERE (timestamp >= :start) AND (timestamp < :end)',
    'sleep_summaries' : 'SELECT * FROM sleep_summaries WHERE (end >= :start) AND (end <:end)',
    }
