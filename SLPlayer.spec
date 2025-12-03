# -*- mode: python ; coding: utf-8 -*-
import glob
from pathlib import Path

block_cipher = None

novastar_dlls = []
for dll in glob.glob('publish/novastar_sdk/*.dll'):
    novastar_dlls.append((dll, 'publish/novastar_sdk'))

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=novastar_dlls,
    datas=[
        ('resources/app.ico', 'resources'),
        ('publish/huidu_sdk', 'publish/huidu_sdk'),
        ('publish/novastar_sdk', 'publish/novastar_sdk'),
    ],
    hiddenimports=[
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'PyQt5.QtMultimedia',
        'PyQt5.QtMultimediaWidgets',
        'requests',
        'requests_toolbelt',
        'sdk.Device',
        'sdk.Program',
        'sdk.File',
        'sdk.common.Config',
        'sdk.common.HttpApi',
        'sdk.common.BaseClient',
        'sdk.data.ProgramNode',
        'sdk.data.area.AreaNode',
        'sdk.data.area.ContentNode',
        'sdk.data.area.DialClockNode',
        'sdk.data.area.DigitalClockNode',
        'sdk.data.area.DynamicNode',
        'sdk.data.area.ImageNode',
        'sdk.data.area.TextNode',
        'sdk.data.area.VideoNode',
        'sdk.data.other.Border',
        'sdk.data.other.ClockParam',
        'sdk.data.other.Effect',
        'sdk.data.other.FileInfo',
        'sdk.data.other.Font',
        'sdk.data.other.PlayControl',
        'sdk.data.task.PeriodicTaskInfo',
        'sdk.data.task.ScheduledTaskInfo',
        'sdk.deviceTask.PeriodicTask',
        'sdk.deviceTask.PushStatusTask',
        'sdk.deviceTask.ScheduledTask',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SLPlayer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/app.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SLPlayer',
)

