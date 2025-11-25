# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from pathlib import Path

block_cipher = None

# Collect SDK DLLs if they exist
binaries = []
sdk_base = Path('requirements')

# Huidu SDK DLL
huidu_dll_path = sdk_base / 'Huidu_Gen6SDK_V2.0.2' / 'x64' / 'HDSDK.dll'
if not huidu_dll_path.exists():
    huidu_dll_path = sdk_base / 'Huidu_Gen6SDK_V2.0.2' / 'HDSDK.dll'
if huidu_dll_path.exists():
    binaries.append((str(huidu_dll_path), '.'))

# NovaStar SDK DLL
novastar_dll_path = sdk_base / 'ViplexCore3.6.3.0101.CTM21.11.1_x64' / 'bin' / 'viplexcore.dll'
if novastar_dll_path.exists():
    binaries.append((str(novastar_dll_path), '.'))

# HDMI DLL (optional)
hdmi_dll_path = Path('hdmi_interface.dll')
if hdmi_dll_path.exists():
    binaries.append((str(hdmi_dll_path), '.'))

# Collect data files
datas = []

# Icon file
icon_path = Path('resources/app.ico')
if icon_path.exists():
    datas.append((str(icon_path), 'resources'))

# City list files for weather
city_list_path = Path('resources/Reference/resources/weather')
if city_list_path.exists():
    datas.append((str(city_list_path), 'resources/Reference/resources/weather'))

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=[
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'PyQt5.QtWebEngineWidgets',
        'PyQt5.QtWebEngineCore',
        'PyQt5.QtWebEngine',
        'PyQt5.QtMultimedia',
        'PyQt5.QtMultimediaWidgets',
        'PyQt5.sip',
        'cv2',
        'numpy',
        'numpy.core._methods',
        'numpy.lib.format',
        'PIL',
        'PIL._tkinter_finder',
        'requests',
        'cryptography',
        'cryptography.hazmat',
        'cryptography.hazmat.backends',
        'cryptography.hazmat.backends.openssl',
        'ctypes',
        'ctypes.util',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'scipy', 'pandas', 'jupyter'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SLPlayer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(icon_path) if icon_path.exists() else None,
)
