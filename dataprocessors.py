from collections import defaultdict
def process_steps(data, starthour, endhour):
    result_dict = defaultdict(int)
    #could be optimised assuming sorted entry data, kept this for stability
    for j in data['body']['series']:
        if int(j) < endhour and int(j) >= starthour:
            result_dict[(int(j)%86400)//3600] += data['body']['series'][j]['steps']
    result_list = []
    for key, value in result_dict.items():
        result_list.append((starthour + key * 3600, value))
    return result_list
def process_sleep_summary(data):
    result_list = []
    for row in data['body']['series']:
        date = (row['enddate'] // 86400) * 86400
        start = row['startdate']
        end = row['enddate']
        total_sleep_time = row['data'].get('total_sleep_time', 0)
        lightsleepduration = row['data'].get('lightsleepduration', 0)
        remsleepduration = row['data'].get('remsleepduration', 0)
        deepsleepduration = row['data'].get('deepsleepduration', 0)
        waso = row['data'].get('waso', 0)
        sleep_score = row['data'].get('sleep_score', 0)
        result_list.append((date, start,end, total_sleep_time, lightsleepduration, remsleepduration, deepsleepduration, sleep_score, waso))
    return result_list
def process_heart_rate(data):
    return [(i,data['body']['series'][i]['heart_rate']) for i in data['body']['series']]