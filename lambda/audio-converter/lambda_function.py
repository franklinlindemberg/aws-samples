import os
import json
import stat
import shutil
import base64
from pydub import AudioSegment
from tempfile import TemporaryDirectory

VALID_INPUT_EXTENSIONS = ['audio/aac', 'audio/m4a']
VALID_OUTPUT_EXTENSIONS = ['audio/wav']


class BadRequest(Exception):
    def __init__(self, message):
        self.message = message


def setup_pydub():
    lambda_tmp_dir = '/tmp'

    os.environ['PATH'] += ':/tmp'

    ffmpeg_bin = "{0}/ffmpeg".format(lambda_tmp_dir)
    shutil.copyfile('/var/task/ffmpeg', ffmpeg_bin)
    os.chmod(ffmpeg_bin, os.stat(ffmpeg_bin).st_mode | stat.S_IEXEC)
    ffprobe_bin = "{0}/ffprobe".format(lambda_tmp_dir)
    shutil.copyfile('/var/task/ffprobe', ffprobe_bin)
    os.chmod(ffprobe_bin, os.stat(ffprobe_bin).st_mode | stat.S_IEXEC)


def get_bad_request_response(message):
    return {
        'statusCode': 400,
        'body': json.dumps({'message': message}),
    }


def get_valid_response(output_audio_path, output_extension):
    with open(output_audio_path, 'rb') as outfile:
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': f'audio/{output_extension}'
            },
            'body': base64.b64encode(outfile.read()).decode('utf-8'),
            'isBase64Encoded': True
        }


def get_file_extension(header):
    return header.split('/')[1]


def save_file(input_audio_path, input_audio):
    with open(input_audio_path, 'wb') as outfile:
        outfile.write(input_audio)


def process_request_parameters(event):
    headers = event.get('Headers', event.get('headers'))
    if not headers:
        raise BadRequest('Missing headers')

    content_type = headers.get('Content-Type', headers.get('content-type'))
    if not content_type or content_type not in VALID_INPUT_EXTENSIONS:
        raise BadRequest('Invalid content-type header')

    accept = headers.get('Accept', headers.get('accept'))
    if not accept or accept not in VALID_OUTPUT_EXTENSIONS:
        raise BadRequest('Invalid accept header')

    body = event.get('body')
    if not body:
        raise BadRequest('Missing body')

    input_extension = get_file_extension(content_type)
    output_extension = get_file_extension(accept)
    input_audio = base64.b64decode(body)

    return input_extension, output_extension, input_audio


def lambda_handler(event, context):

    try:
        input_extension, output_extension, input_audio = process_request_parameters(event)

        setup_pydub()

        with TemporaryDirectory() as tmp:
            input_audio_path = f'{tmp}/audio.{input_extension}'
            output_audio_path = f'{tmp}/audio.{output_extension}'

            save_file(input_audio_path, input_audio)

            f_audio = AudioSegment.from_file(input_audio_path, input_extension)\
                .set_frame_rate(16000)\
                .set_channels(1)

            if f_audio.duration_seconds > 30.0:
                raise BadRequest('Audio file exceeds 30 seconds')

            f_audio.export(output_audio_path, format=output_extension)

            return get_valid_response(output_audio_path, output_extension)
    except BadRequest as ex:
        return get_bad_request_response(ex.message)
