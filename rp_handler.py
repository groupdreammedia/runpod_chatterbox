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
                return
                    print("Initializing model...")
                        model = ChatterboxTTS.from_pretrained(device="cuda")

                        def handler(event):
                            input_data = event.get("input", {})
                                prompt = input_data.get("prompt", "")
                                    audio_b64 = input_data.get("audio", None)
                                        if not prompt: return {"status": "error", "error": "No prompt"}
                                            
                                                try:
                                                        if model is None: initialize_model()
                                                                
                                                                        ref_path = None
                                                                                if audio_b64:
                                                                                                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                                                                                                                    tmp.write(base64.b64decode(audio_b64))
                                                                                                                                    ref_path = tmp.name
                                                                                                                                                    
                                                                                                                                                            audio = model.generate(prompt, audio_prompt_path=ref_path)
                                                                                                                                                                    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as out:
                                                                                                                                                                                    sr = getattr(model, "sr", 24000)
                                                                                                                                                                                                torchaudio.save(out.name, audio.cpu(), sr)
                                                                                                                                                                                                            with open(out.name, "rb") as f:
                                                                                                                                                                                                                                res = base64.b64encode(f.read()).decode("utf-8")
                                                                                                                                                                                                                                            os.unlink(out.name)
                                                                                                                                                                                                                                                    
                                                                                                                                                                                                                                                            if ref_path: os.unlink(ref_path)
                                                                                                                                                                                                                                                                    return {"status": "success", "audio_base64": res}
                                                                                                                                                                                                                                                                        except Exception as e:
                                                                                                                                                                                                                                                                                    return {"status": "error", "error": str(e)}

                                                                                                                                                                                                                                                                                    if __name__ == "__main__":
                                                                                                                                                                                                                                                                                            runpod.serverless.start({"handler": handler})
                                                                                                                                                                                                                                                                                            