from setuptools import setup

APP = ['MacWinMan.py']
OPTIONS = {
    'includes': [
        'rumps',
        'subprocess',
        'AppKit',
        'pynput',
        'pynput.keyboard',
        'pynput.keyboard._darwin',
        'pynput.mouse',
        'pynput.mouse._darwin',
        'pynput._util',
        'pynput._util.darwin',
        'pkg_resources',
        'jaraco.text',
    ],
    'iconfile': 'icon.icns',
    'resources': ['icon.icns'],
    'plist': {
        'LSBackgroundOnly': False,
    },
}

setup(
    app=APP,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)