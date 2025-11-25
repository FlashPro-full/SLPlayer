# Building SLPlayer Executable

This guide explains how to create a standalone `.exe` file from the SLPlayer Python application.

## Prerequisites

1. **Python 3.8+** installed
2. All project dependencies installed:
   ```bash
   pip install -r requirements.txt
   ```
3. **PyInstaller** installed:
   ```bash
   pip install pyinstaller
   ```

## Quick Build (Windows)

### Option 1: Using the batch script
```bash
build.bat
```

### Option 2: Using PyInstaller directly
```bash
pyinstaller --clean build_exe.spec
```

## Quick Build (Linux/Mac)

```bash
chmod +x build.sh
./build.sh
```

## Manual Build Steps

1. **Install PyInstaller** (if not already installed):
   ```bash
   pip install pyinstaller
   ```

2. **Build the executable**:
   ```bash
   pyinstaller --clean build_exe.spec
   ```

3. **Find your executable**:
   - The executable will be in the `dist` folder
   - File name: `SLPlayer.exe` (Windows) or `SLPlayer` (Linux/Mac)

## Advanced Options

### Create a one-file executable (current spec)
The current `build_exe.spec` creates a single `.exe` file with all dependencies bundled.

### Create a one-folder distribution
If you want a folder with the executable and DLLs (faster startup, easier debugging):

```bash
pyinstaller --onefile --windowed --name SLPlayer main.py
```

### Add an icon
1. Create or obtain an `.ico` file (Windows) or `.icns` file (Mac)
2. Update `build_exe.spec`:
   ```python
   icon='path/to/icon.ico',  # Add this to the EXE() section
   ```

### Include additional data files
If you need to include additional files (images, configs, etc.), update the `datas` list in `build_exe.spec`:
```python
datas=[
    ('path/to/data', 'data'),
    ('resources', 'resources'),
],
```

## Troubleshooting

### Missing DLL errors
If you get DLL errors at runtime:
1. Check that all Qt plugins are included
2. Try adding `--collect-all PyQt5` to the PyInstaller command
3. For QWebEngineView, ensure Qt WebEngine plugins are included

### Large file size
The executable will be large (100-200MB) because it includes:
- Python interpreter
- PyQt5 and all Qt libraries
- QWebEngineView (Chromium-based, very large)
- All other dependencies

To reduce size:
- Use `--exclude-module` to exclude unused modules
- Consider using UPX compression (already enabled in spec)

### QWebEngineView not working
If web pages don't load:
1. Ensure `PyQtWebEngine` is properly installed
2. Check that Qt WebEngine plugins are included
3. Try adding to hiddenimports:
   ```python
   'PyQt5.QtWebEngineWidgets',
   'PyQt5.QtWebEngineCore',
   ```

### Missing ctypes DLLs
The build script automatically includes SDK DLLs if they exist:
- `HDSDK.dll` from `requirements/Huidu_Gen6SDK_V2.0.2/`
- `viplexcore.dll` from `requirements/ViplexCore3.6.3.0101.CTM21.11.1_x64/`
- `hdmi_interface.dll` (if present in project root)

If DLLs are missing:
1. Ensure SDK folders are in the `requirements` directory
2. Or manually copy DLL files to the same folder as the executable after building
3. The application will work without SDK DLLs but controller features will be unavailable

## Testing the Executable

1. **Test on the build machine first**
2. **Test on a clean machine** (without Python installed) to ensure all dependencies are included
3. **Check all features**:
   - GUI displays correctly
   - File operations work
   - WebEngine loads pages (if used)
   - Video playback works
   - SDK DLLs load correctly

## Distribution

After building:
1. The `dist` folder contains your executable
2. If using SDK DLLs, copy them to the same folder as the executable
3. Create an installer (optional) using tools like:
   - Inno Setup (Windows)
   - NSIS (Windows)
   - InstallBuilder (Cross-platform)

## Notes

- The first run may be slower as files are extracted
- Antivirus software may flag PyInstaller executables (false positive)
- Consider code signing for production releases

