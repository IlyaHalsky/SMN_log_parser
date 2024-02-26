import PyInstaller.__main__

PyInstaller.__main__.run([
    'smn_logs.py',
    '--onefile',
    '--clean',
    '--distpath','./release',
    '--specpath','./release',
    '-n smn_1.0.exe'
])