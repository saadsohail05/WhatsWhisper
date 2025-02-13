import torch
import os
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks
from modelscope.hub.snapshot_download import snapshot_download

# Set torch threads
torch.set_num_threads(8)
torch.set_num_interop_threads(8)

# Define model cache directory and ID
MODEL_ID = 'damo/speech_zipenhancer_ans_multiloss_16k_base'
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models')

# Create cache directory if it doesn't exist
os.makedirs(CACHE_DIR, exist_ok=True)

# Check if model is already downloaded
model_dir = os.path.join(CACHE_DIR, 'damo', MODEL_ID.split('/')[-1])
print(f"Checking if model exists in: {model_dir}")
if not os.path.exists(model_dir):
    print(f"Model not found. Downloading to: {CACHE_DIR}")
    model_dir = snapshot_download(MODEL_ID, cache_dir=CACHE_DIR)
    print(f"Model downloaded successfully to: {model_dir}")
else:
    print(f"Model already exists at: {model_dir}")

# Initialize model with local path
ans = pipeline(
    Tasks.acoustic_noise_suppression,
    model=model_dir,
    device='cpu'
)

result = ans('audio.mpga', output_path='output.wav')
print("done")