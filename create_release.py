import PyInstaller.__main__

PyInstaller.__main__.run([
    'lists_compiler.py',
    '--onefile',
    '--add-data', "./cards.collectible.json:.",
    '-n lists_compiler.exe'
])

PyInstaller.__main__.run([
    'smn_helper.py',
    '--onefile',
    '--add-data', "./cards.collectible.json:.",
    '-n smn_helper.exe'
])