# Voxora Studio

**A lightweight, offline desktop text-to-speech application for Windows.**

Voxora Studio is a desktop application built with Python, CustomTkinter, and Supertonic 3. It converts written text into speech using locally stored AI models. Users can preview generated audio and save it as a WAV file.

The application is designed to work offline after the required model files have been installed.

## Features

- **Offline text-to-speech:** Generate speech locally without sending text to an online service.
- **Two languages:** English and Hindi.
- **10 voices:** Five female and five male voice options.
- **Adjustable speech speed:** Control generation speed from 0.7× to 1.3×.
- **Quality control:** Choose between 4, 8, and 12 inference steps.
- **Audio preview:** Listen to generated speech before saving.
- **Audio controls:** Play, pause, resume, seek, and track playback progress.
- **WAV export:** Save generated audio to your preferred location.
- **Modern interface:** Dark midnight-blue theme with custom dropdown controls.

## Technology Stack

- Python 3.13
- CustomTkinter
- Supertonic 3
- ONNX Runtime
- NumPy
- Pygame
- SoundFile

## Project Status

Voxora Studio is currently in its initial release preparation stage.

## Installation (Windows)

### For regular users

You do not need Python or any development tools to run the packaged application.

1. Open the [Voxora Studio Releases](../../releases) page.
2. Download the latest `VoxoraStudio-Windows.zip` file.
3. Extract the ZIP file.
4. Open the extracted `VoxoraStudio` folder.
5. Double-click `VoxoraStudio.exe`.

**Important:**

- Keep the entire extracted folder together. Do not move the EXE out of its folder.
- The `models` directory must remain beside the executable.
- The first launch may take some time while the AI model initializes.
- After setup, speech generation works offline.

## Building the Windows Executable

Developers can create a standalone Windows application using PyInstaller.

### 1. Install PyInstaller

```powershell
python -m pip install pyinstaller
```

### 2. Build the application

Run from the project root:

```powershell
python -m PyInstaller --noconfirm --clean --onedir --windowed --icon=VoxoraStudio.ico --name VoxoraStudio --collect-all customtkinter --collect-all supertonic --collect-all onnxruntime --collect-all pygame --collect-all soundfile app.py
```

### 3. Prepare the portable application

After the build finishes:

1. Copy the `models` folder into `dist/VoxoraStudio/`.
2. Copy `VoxoraStudio.ico` into `dist/VoxoraStudio/`.
3. Keep the generated `_internal` folder and executable together.

The portable application will be available in:

```text
dist/VoxoraStudio/
```

Zip the entire `VoxoraStudio` folder to distribute the portable application.

## Developer Setup

### Requirements

- Windows 10 or Windows 11 (64-bit)
- Python 3.13
- Git
- Internet connection for downloading dependencies and model files

### 1. Clone the repository

Open PowerShell and run:

```powershell
git clone https://github.com/EnergiousNPC/Voxora-Studio.git
cd Voxora-Studio
```

### 2. Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Download the AI model

Voxora Studio uses the Supertonic 3 model.

Install the Hugging Face CLI if it is not already available:

```powershell
python -m pip install huggingface_hub
```

Download the model:

```powershell
hf download Supertone/supertonic-3 --revision 724fb5abbf5502583fb520898d45929e62f02c0b --local-dir models/supertonic-3
```

The model files should be located in:

```text
models/supertonic-3/
```

### 5. Run Voxora Studio

```powershell
python app.py
```

The application should now launch.

**Note:** The model files are not included in this Git repository. Each developer must download them separately before running the application.

## Model and Third-Party Licenses

Voxora Studio uses the Supertonic 3 text-to-speech model and several third-party Python packages.

Each third-party component is subject to its own license. Refer to `LICENSE` and `THIRD_PARTY_NOTICES.md` for licensing information.

- Supertonic model: https://huggingface.co/Supertone/supertonic-3
- Supertonic source code: https://github.com/supertone-inc/supertonic

## Contributing

Contributions, bug reports, and suggestions are welcome. Please open an issue or submit a pull request on GitHub.

## Acknowledgements

Special thanks to Supertone for developing Supertonic 3 and making the text-to-speech technology available.

---

**Voxora Studio**  
Built with Python and Supertonic 3.