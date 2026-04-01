import runpod
import base64
import os
import tempfile
import torchaudio
from chatterbox.tts import ChatterboxTTS

model = None

def initialize_model():
        global model
        if model is not None:
                    print("Model already initialized")
                    return
                print("Initializing ChatterboxTTS model...")
    model = ChatterboxTTS.from_pretrained(device="cuda")
    print("Model initialized successfully")

def handler(event):
        input_data = event.get("input", {})
    prompt = input_data.get("prompt", "")
    audio_base64 = input_data.get("audio", None)

    if not prompt:
                return {"status": "error", "error": "No prompt provided"}

    print(f"New request. Prompt length: {len(prompt)} chars")

    try:
                ref_path = None
                if audio_base64:
                                ref_bytes = base64.b64decode(audio_base64)
                                tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
                                tmp.write(ref_bytes)
                                tmp.close()
                                ref_path = tmp.name
                                print(f"Reference audio: {len(ref_bytes)} bytes")

                if ref_path and os.path.exists(ref_path):
                                audio_tensor = model.generate(prompt, audio_prompt_path=ref_path)
    else:
            audio_tensor = model.generate(prompt)

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as out_f:
                        torchaudio.save(out_f.name, audio_tensor, model.sr)
                        with open(out_f.name, "rb") as f:
                                            result_b64 = base64.b64encode(f.read()).decode("utf-8")
                                        os.unlink(out_f.name)

        if ref_path and os.path.exists(ref_path):
                        os.unlink(ref_path)

        return {
                        "status": "success",
                        "audio_base64": result_b64,
                        "metadata": {
                                            "sample_rate": model.sr,
                                            "audio_shape": list(audio_tensor.shape),
                        },
        }

except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "error": str(e)}

if __name__ == "__main__":
        initialize_model()
    runpod.serverless.start({"handler": handler})
