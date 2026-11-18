"""Meta MMS VITS speech for languages without an Edge TTS voice."""

from __future__ import annotations

from pathlib import Path

_MODELS = {
    "or": "facebook/mms-tts-ory",
    "pa": "facebook/mms-tts-pan",
}

_cache = {}


def generate_mms_audio(text: str, out_path: Path, lang_code: str) -> None:
    import numpy as np
    import scipy.io.wavfile
    import torch
    from transformers import AutoTokenizer, VitsModel

    model_id = _MODELS.get(lang_code, f"facebook/mms-tts-{lang_code}")
    if model_id not in _cache:
        print(f"[mms] Loading {model_id} ...")
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        model = VitsModel.from_pretrained(model_id)
        model.eval()
        _cache[model_id] = (tokenizer, model)
    tokenizer, model = _cache[model_id]

    inputs = tokenizer(text, return_tensors="pt")
    with torch.no_grad():
        waveform = model(**inputs).waveform

    samples = waveform.cpu().numpy().squeeze()
    samples = np.clip(samples, -1.0, 1.0)
    scipy.io.wavfile.write(str(out_path), int(model.config.sampling_rate), samples)
