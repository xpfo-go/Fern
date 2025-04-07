# Updates

Latest Version: v0.0.0

Currently demo.

# Installation
## Python: 
develop version: Python 3.11. Maybe 3.9 < Python < 3.13 is ok.

Installable Python kits, and information about using Python, are available at
[python.org](https://www.python.org/).
## MCP:
[MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
### Overview
The Model Context Protocol allows applications to provide context for LLMs in a standardized way, separating the concerns of providing context from the actual LLM interaction. This Python SDK implements the full MCP specification, making it easy to:

- Build MCP clients that can connect to any MCP server
- Create MCP servers that expose resources, prompts and tools
- Use standard transports like stdio and SSE
- Handle all MCP protocol messages and lifecycle events

### Installation MCP
We recommend using [uv](https://docs.astral.sh/uv/) to manage your Python projects. 

If you have uv-managed, Add MCP to your project dependencies:
```bash
uv add "mcp"
```

Alternatively, for projects using pip for dependencies:
```bash
pip install "mcp"
```


## TTS:

### Overview

Currently using [pyttsx3](https://pypi.org/project/pyttsx3/)

Full documentation of the Library: https://pyttsx3.readthedocs.io/en/latest/

### Installation
```bash
pip install pyttsx3
```
> If you get installation errors , make sure you first upgrade your wheel version using : pip install –upgrade wheel

### Linux installation requirements :
If you are on a linux system and if the voice output is not working , then: Install espeak , ffmpeg and libespeak1 as shown below:

```bash
sudo apt update && sudo apt install espeak ffmpeg libespeak1
```

## STT:
[RealtimeSTT GitHub](https://github.com/KoljaB/RealtimeSTT)
```bash
pip install RealtimeSTT
```

This will install all the necessary dependencies, including a **CPU support only** version of PyTorch.

Although it is possible to run RealtimeSTT with a CPU installation only (use a small model like "tiny" or "base" in this case) you will get way better experience using CUDA (please scroll down).

### Linux Installation

Before installing RealtimeSTT please execute:

```bash
sudo apt-get update
sudo apt-get install python3-dev
sudo apt-get install portaudio19-dev
```

### MacOS Installation

Before installing RealtimeSTT please execute:

```bash
brew install portaudio
```
### GPU Support with CUDA (recommended)

### Updating PyTorch for CUDA Support

To upgrade your PyTorch installation to enable GPU support with CUDA, follow these instructions based on your specific CUDA version. This is useful if you wish to enhance the performance of RealtimeSTT with CUDA capabilities.

#### For CUDA 11.8:
To update PyTorch and Torchaudio to support CUDA 11.8, use the following commands:

```bash
pip install torch==2.5.1+cu118 torchaudio==2.5.1 --index-url https://download.pytorch.org/whl/cu118
```

#### For CUDA 12.X:
To update PyTorch and Torchaudio to support CUDA 12.X, execute the following:

```bash
pip install torch==2.5.1+cu121 torchaudio==2.5.1 --index-url https://download.pytorch.org/whl/cu121
```

Replace `2.5.1` with the version of PyTorch that matches your system and requirements.

### Steps That Might Be Necessary Before

> **Note**: *To check if your NVIDIA GPU supports CUDA, visit the [official CUDA GPUs list](https://developer.nvidia.com/cuda-gpus).*

If you didn't use CUDA models before, some additional steps might be needed one time before installation. These steps prepare the system for CUDA support and installation of the **GPU-optimized** installation. This is recommended for those who require **better performance** and have a compatible NVIDIA GPU. To use RealtimeSTT with GPU support via CUDA please also follow these steps:

1. **Install NVIDIA CUDA Toolkit**:
    - select between CUDA 11.8 or CUDA 12.X Toolkit
        - for 12.X visit [NVIDIA CUDA Toolkit Archive](https://developer.nvidia.com/cuda-toolkit-archive) and select latest version.
        - for 11.8 visit [NVIDIA CUDA Toolkit 11.8](https://developer.nvidia.com/cuda-11-8-0-download-archive).
    - Select operating system and version.
    - Download and install the software.

2. **Install NVIDIA cuDNN**:
    - select between CUDA 11.8 or CUDA 12.X Toolkit
        - for 12.X visit [cuDNN Downloads](https://developer.nvidia.com/cudnn-downloads).
            - Select operating system and version.
            - Download and install the software.
        - for 11.8 visit [NVIDIA cuDNN Archive](https://developer.nvidia.com/rdp/cudnn-archive).
            - Click on "Download cuDNN v8.7.0 (November 28th, 2022), for CUDA 11.x".
            - Download and install the software.
    
3. **Install ffmpeg**:

    > **Note**: *Installation of ffmpeg might not actually be needed to operate RealtimeSTT* <sup> *thanks to jgilbert2017 for pointing this out</sup>

    You can download an installer for your OS from the [ffmpeg Website](https://ffmpeg.org/download.html).  
    
    Or use a package manager:

    - **On Ubuntu or Debian**:
        ```bash
        sudo apt update && sudo apt install ffmpeg
        ```

    - **On Arch Linux**:
        ```bash
        sudo pacman -S ffmpeg
        ```

    - **On MacOS using Homebrew** ([https://brew.sh/](https://brew.sh/)):
        ```bash
        brew install ffmpeg
        ```

    - **On Windows using Winget** [official documentation](https://learn.microsoft.com/en-us/windows/package-manager/winget/) :
        ```bash
        winget install Gyan.FFmpeg
        ```
        
    - **On Windows using Chocolatey** ([https://chocolatey.org/](https://chocolatey.org/)):
        ```bash
        choco install ffmpeg
        ```

    - **On Windows using Scoop** ([https://scoop.sh/](https://scoop.sh/)):
        ```bash
        scoop install ffmpeg
        ```    

####  Train your own OpenWakeWord models
Look [here](https://github.com/dscripka/openWakeWord?tab=readme-ov-file#training-new-models) for information about how to train your own OpenWakeWord models. You can use a [simple Google Colab notebook](https://colab.research.google.com/drive/1q1oe2zOyZp7UsB3jJiQ1IFn8z5YfjwEb?usp=sharing) for a start or use a [more detailed notebook](https://github.com/dscripka/openWakeWord/blob/main/notebooks/automatic_model_training.ipynb) that enables more customization (can produce high quality models, but requires more development experience).

### Convert model to ONNX format

You might need to use tf2onnx to convert tensorflow tflite models to onnx format:

```bash
pip install -U tf2onnx
python -m tf2onnx.convert --tflite my_model_filename.tflite --output my_model_filename.onnx
```

## FAQ

### Q: I encountered the following error: "Unable to load any of {libcudnn_ops.so.9.1.0, libcudnn_ops.so.9.1, libcudnn_ops.so.9, libcudnn_ops.so} Invalid handle. Cannot load symbol cudnnCreateTensorDescriptor." How do I fix this?

**A:** This issue arises from a mismatch between the version of `ctranslate2` and cuDNN. The `ctranslate2` library was updated to version 4.5.0, which uses cuDNN 9.2. There are two ways to resolve this issue:
1. **Downgrade `ctranslate2` to version 4.4.0**:
   ```bash
   pip install ctranslate2==4.4.0
   ```
2. **Upgrade cuDNN** on your system to version 9.2 or above.

## Contribution

Contributions are always welcome! 

Shoutout to [Steven Linn](https://github.com/stevenlafl) for providing docker support. 

