fb_url = 'https://graph.facebook.com/v2.6/me/messages'
data = {
    'recipient': '{"id":1336677726453307}',
    'message': '{"attachment":{"type":"audio", "payload":{}}}'
}
files = {
    'filedata': ('mymp3.mp3', open("mymp3.mp3", "rb"), 'audio/mp3')}
params = {'access_token': ACCESS_TOKEN}
resp = requests.post(fb_url, params=params, data=data, files=files)