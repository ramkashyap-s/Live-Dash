import faust
app = faust.App('example', broker='kafka://localhost', store='memory://')
topic = app.topic('twitch-message')