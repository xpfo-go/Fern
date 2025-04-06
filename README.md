usage:
  python: 
        python 3.11
  mcp:
    pip install mcp
  tts:
    pip install pyttsx3 pyaudio
  stt:
    pip install RealtimeSTT
    This will install all the necessary dependencies, including a CPU support only version of PyTorch.
    Although it is possible to run RealtimeSTT with a CPU installation only (use a small model like "tiny" or "base" in this case) you will get way better experience using CUDA (please scroll down).

    Linux Installation
    Before installing RealtimeSTT please execute:
    
    sudo apt-get update
    sudo apt-get install python3-dev
    sudo apt-get install portaudio19-dev
    
    MacOS Installation
    Before installing RealtimeSTT please execute:
    
    brew install portaudio
