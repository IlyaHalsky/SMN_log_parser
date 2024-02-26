import PyInstaller.__main__

PyInstaller.__main__.run([
    'lists_compiler.py',
    '--onefile',
    '--clean',
    '--distpath','./release',
    '--specpath','./release',
    '-n lists_compiler.exe'
])