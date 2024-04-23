import platform

import PyInstaller.__main__

# PyInstaller.__main__.run([
#     'lists_compiler.py',
#     '--onefile',
#     '--add-data', "./cards.collectible.json:.",
#     '-n lists_compiler.exe'
# ])
#
# PyInstaller.__main__.run([
#     'smn_helper.py',
#     '--onefile',
#     '--add-data', "./cards.collectible.json:.",
#     '--add-data', "./rich.wav:.",
#     '-n smn_helper.exe'
# ])
if platform.system() == 'Windows':
    filename = '-n lst_helper.exe'
    arch = []
else:
    filename = '-n lst_helper.mac'
    arch = ['--target-arch universal2']
PyInstaller.__main__.run(
    [
        'lst_helper.py',
        '--onefile',
        '--add-data', "./cards.collectible.json:.",
        filename,
        *arch
    ]
)
