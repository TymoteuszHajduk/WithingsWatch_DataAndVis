from collections import defaultdict
def process_steps(data, starthour, endhour):
    result_dict = defaultdict(int)
    #could be optimised assuming sorted entry data, kept this for stability
    for j in data['body']['series']:
        if int(j) < endhour and int(j) >= starthour:
            result_dict[(int(j)%86400)//3600] += data['body']['series'][j]['steps']
    return list(result_dict.items())
def process_sleep_summary(data):
    result_list = []
    for row in data['body']['series']:
        date = (row['enddate'] // 86400) * 86400
        start = row['startdate']
        end = row['enddate']
        total_sleep_time = row['data']['total_sleep_time']
        lightsleepduration = row['data']['lightsleepduration']
        remsleepduration = row['data']['remsleepduration']
        deepsleepduration = row['data']['deepsleepduration']
        waso = row['data']['waso']
        sleep_score = row['data']['sleep_score']
        result_list.append((date, start,end, total_sleep_time, lightsleepduration, remsleepduration, deepsleepduration, sleep_score, waso))
    return result_list
def process_heart_rate(data):
    return [(i,data['body']['series'][i]['heart_rate']) for i in data['body']['series']]