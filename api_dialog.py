import requests
import json
import time
import datetime

def refresh_tokens():
    with open('state.json') as f:
        tokens_state = json.load(f)
        refresh_token = tokens_state['refresh_token']
        client_id = tokens_state['client_id']
        client_secret = tokens_state['client_secret']
    new_tokens = requests.post(url = 'https://wbsapi.withings.net/v2/oauth2', data = {'action':'requesttoken', 'client_id': client_id , 'client_secret' : client_secret, 'grant_type' : 'refresh_token', 'refresh_token': refresh_token })
    new_tokens = new_tokens.json()
    with open('state.json', 'r') as f:
        state = json.load(f)
    state['access_token'] = new_tokens['body']['access_token']
    state['refresh_token'] = new_tokens['body']['refresh_token']
    with open('state.json', 'w') as f:
        json.dump(state, f)
    if new_tokens['status'] != 0:
        raise RuntimeError("Cannot connect with Withings API to refresh the token")
    else:
        print("Token refreshed succesfully")
        return new_tokens['body']['access_token']

class RequestWrap:
    def __init__(self):
        self._access_token = None
        self._userid = None
        self.update_access_token()
    def update_access_token(self):
        with open('state.json') as f:
            tokens_state = json.load(f)
            self._access_token = tokens_state['access_token']
            self._userid = tokens_state['userid']
    def request(self,request_config, start_date, end_date):
        data = request_config['params'].copy()
        #two types of start-end date params - api quirk
        data['userid'] = self._userid
        data['startdate'] = start_date
        data['enddate'] = end_date
        data['startdateymd'] = datetime.date.fromtimestamp(start_date).strftime('%Y-%m-%d')
        data['enddateymd'] = datetime.date.fromtimestamp(end_date).strftime('%Y-%m-%d')
        request = requests.post(url=request_config["url"],
                                    data=data,
                                    headers={'Authorization': 'Bearer ' + self._access_token})
        data = request.json()
        if data['status'] == 401:
            refresh_tokens()
            self.update_access_token()
            return self.request(request_config, start_date, end_date)
        elif data['status'] != 0:
            raise RuntimeError("Cannot connect with Withings to refresh the data")
        return data
class TimeSlicer:
    def __init__(self):
        with open('state.json', 'r') as f:
            data = json.load(f)
        self.lastupdate = data['lastupdate']
        self.current_rounded_time = (int(time.time()) // 86400) * 86400
    def time_slices_generator(self):
        """yields a start - end date value pair"""
        start_cursor = self.lastupdate
        end_cursor = self.lastupdate + 86400
        while start_cursor < self.current_rounded_time:
            yield start_cursor, end_cursor
            start_cursor += 86400
            end_cursor += 86400
    def lastupdateupdater(self):
        try:
            with open('state.json', 'r') as f:
                data = json.load(f)
                data['lastupdate'] = self.current_rounded_time
            with open('state.json', 'w') as f:
                json.dump(data, f)
        except FileNotFoundError:
            raise RuntimeError("Cannot find the state.json file")
