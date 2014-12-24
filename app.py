from flask import Flask, request, redirect
import twilio.twiml
import redis

app = Flask(__name__)

rickroll = 'http://hazzardweb.net/wp-content/uploads/RickRoll/RickRoll.mp3'

@app.route('/')
def hello_world():
    resp = twilio.twiml.Response()

    with resp.gather(numDigits=1, action='/handle-digit', method="POST") as g:
        g.say('Thank you for calling Nullspace Labs')
        g.say('Press 1 to call the Nullspace batphone')
        g.say('Press 2 to ring the doorbell')
        g.say('Press 3 to transcribe a message to eye arsey')
        g.say('Press 4 to listen to Rick Astley')

    return str(resp)

@app.route("/handle-digit", methods=['GET', 'POST'])
def handle_digit():
    digit_pressed = request.values.get('Digits', None)
    print 'caller pressed: ' + str(digit_pressed)
    resp = twilio.twiml.Response()
    
    if digit_pressed == "4":
        resp.play(rickroll)
    elif digit_pressed == "3":
        resp.say('record a message up to 30 seconds')
        resp.record(maxLength="30", transcribeCallback='/handle-transcription', action="/handle-recording")
    elif digit_pressed == "2":
        resp.say('Doorbell is ringing, if you are locked outside, stay there and wait for emergency personnel to arrive')
    elif digit_pressed == "1":
        resp.say('connecting')
        resp.dial('+12343124521')
    else:
        resp.say('unrecognized digit')
        return redirect("/")
    return str(resp)   

@app.route('/handle-transcription', methods=['GET', 'POST'])
def handle_transcription():
    transcription = request.values.get('TranscriptionText')
    r = redis.Redis()
    r.lpush('saytoirc', 'transcription: ' + str(transcription))

@app.route('/handle-recording', methods=['GET', 'POST'])
def handle_recording():
    recording_url = request.values.get('RecordingUrl', None)
    r = redis.Redis()
    r.lpush('saytoirc', str('Voicemail for #nsl ' + recording_url))
    print recording_url
    resp = twilio.twiml.Response()
    resp.say('Thank you')
    return str(resp)

if __name__ == '__main__':
    app.debug = True
    app.run('0.0.0.0', port=80)
