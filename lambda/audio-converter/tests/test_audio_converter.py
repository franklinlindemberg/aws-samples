import requests

input_audio_path = 'trimmed_sample.m4a'

with open(input_audio_path, "rb") as image_file:

    url = '<URL_API_GATEWAY>'
    headers = {
        'Content-Type': 'audio/m4a',
        'Accept': 'audio/wav'
    }

    data = image_file.read()

    r = requests.post(url, data=data, headers=headers)

    if r.status_code == 200:
        with open("output.wav", "wb") as output_file:
            output_file.write(r.content)
    else:
        print(r.text)
