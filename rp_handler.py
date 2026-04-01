import runpod
import time
import torchaudio
import os
import tempfile
import base64
import io
from chatterbox.tts import ChatterboxTTS
from pathlib import Path

model = None
output_filename = "output.wav"

def handler(event, responseFormat="base64"):
        input = event['input']
        prompt = input.get('prompt')
        audio_base64 = input.get('audio_base64')  # Base64-encoded WAV/MP3 reference audio
    yt_url = input.get('yt_url')              # YouTube URL (legacy support)

    print(f"New request. Prompt: {prompt}")

    try:
                # Priority: audio_base64 > yt_url > no reference
                if audio_base64:
                                wav_file = decode_base64_audio(audio_base64)
                                print(f"Using base64 reference audio: {wav_file}")
elif yt_url:
            import yt_dlp
            _, wav_file = download_youtube_audio(yt_url, output_path="./my_audio", audio_format="wav")
            print(f"Using YouTube reference audio: {wav_file}")
else:
            wav_file = None
                print("No reference audio provided, using default voice")

        # Generate TTS
        if wav_file and os.path.exists(wav_file):
                        audio_tensor = model.generate(prompt, audio_prompt_path=wav_file)
else:
            audio_tensor = model.generate(prompt)

        # Save as WAV
        torchaudio.save(output_filename, audio_tensor, model.sr)

except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {"status": "error", "error": str(e)}

    # Convert to base64 string
    result_base64 = audio_tensor_to_base64(audio_tensor, model.sr)

    response = {
                "status": "success",
                "audio_base64": result_base64,
                "metadata": {
                                "sample_rate": model.sr,
                                "audio_shape": list(audio_tensor.shape)
                }
    }

    # Clean up temporary files
    if wav_file and os.path.exists(wav_file):
                try:
                                os.remove(wav_file)
                            except:
            pass

    return response

def decode_base64_audio(b64_string):
        """Decode base64 audio data and save to a temporary WAV file."""
    audio_bytes = base64.b64decode(b64_string)
    Path('./my_audio').mkdir(parents=True, exist_ok=True)
    tmp = tempfile.NamedTemporaryFile(suffix='.wav', delete=False, dir='./my_audio')
    tmp_path = tmp.name
    tmp.write(audio_bytes)
    tmp.close()
    print(f"Decoded {len(audio_bytes)} bytes of reference audio to {tmp_path}")
    return tmp_path

def audio_tensor_to_base64(audio_tensor, sample_rate):
        """Convert audio tensor to base64 encoded WAV data."""
    try:
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                                torchaudio.save(tmp_file.name, audio_tensor, sample_rate)
                                with open(tmp_file.name, 'rb') as audio_file:
                                                    audio_data = audio_file.read()
                                                os.unlink(tmp_file.name)
                                return base64.b64encode(audio_data).decode('utf-8')
    except Exception as e:
        print(f"Error converting audio to base64: {e}")
        raise

def initialize_model():
        global model
    if model is not None:
                print("Model already initialized")
                return model
            print("Initializing ChatterboxTTS model...")
    model = ChatterboxTTS.from_pretrained(device="cuda")
    print("Model initialized")

def download_youtube_audio(url, output_path="./downloads", audio_format="mp3", duration_limit=60):
        """Download audio from a YouTube video."""
    import yt_dlp
    Path(output_path).mkdir(parents=True, exist_ok=True)
    ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': f'{output_path}/output.%(ext)s',
                'postprocessors': [{
                                'key': 'FFmpegExtractAudio',
                                'preferredcodec': audio_format,
                                'preferredquality': '192',
                }],
                'postprocessor_args': ['-ar', '44100'],
                'prefer_ffmpeg': True,
    }
    if duration_limit:
                ydl_opts['postprocessors'].append({
                                'key': 'FFmpegVideoConvertor',
                                'preferedformat': audio_format,
                })
                ydl_opts['postprocessor_args'].extend(['-t', str(duration_limit)])
            try:
                        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                                        info = ydl.extract_info(url, download=False)
                                        print(f"Title: {info.get('title', 'Unknown')}")
                                        print(f"Duration: {info.get('duration', 'Unknown')} seconds")
                                        if duration_limit:
                                                            actual_duration = min(duration_limit, info.get('duration', 0))
                                                            print(f"Downloading first {actual_duration} seconds")
                                                        ydl.download([url])
                                        expected_filepath = os.path.join(output_path, f"output.{audio_format}")
                                        return info, expected_filepath
            except Exception as e:
                        print(f"An error occurred: {str(e)}")
                        return None, None

if __name__ == '__main__':
        initialize_model()
    runpod.serverless.start({'handler': handler})
