#!/usr/bin/env python3

from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return 'Official GRUB graphical editor for Soplos Linux'

# Read requirements
def read_requirements():
    req_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(req_path):
        with open(req_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return [
        'PyGObject>=3.36.0',
        'pycairo>=1.16.2',
        'python-xlib>=0.27',
        'polib>=1.1.0',
        'python-dbus>=1.2.16',
        'Pillow>=8.0.0'
    ]

setup(
    name='soplos-grub-editor',
    version='2.0.0',
    description='Official GRUB graphical editor for Soplos Linux',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    author='Sergi Perich',
    author_email='info@soploslinux.com',
    url='https://soplos.org',
    project_urls={
        'Bug Reports': 'https://github.com/SoplosLinux/soplos-grub-editor/issues',
        'Source': 'https://github.com/SoplosLinux/soplos-grub-editor',
        'Documentation': 'https://soplos.org/docs/soplos-grub-editor',
        'Changelog': 'https://github.com/SoplosLinux/soplos-grub-editor/blob/main/CHANGELOG.md',
    },
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'soplos_grub_editor': [
            'translations/locales/*.py',
            'assets/icons/*.png',
            'assets/*.desktop',
            'debian/*.xml',
            'debian/control',
        ],
    },
    install_requires=read_requirements(),
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'soplos-grub-editor=main:main',
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: System :: Boot',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
        'Environment :: X11 Applications :: GTK',
        'Natural Language :: Spanish',
        'Natural Language :: English',
        'Natural Language :: French',
        'Natural Language :: Portuguese',
        'Natural Language :: German',
        'Natural Language :: Italian',
        'Natural Language :: Russian',
        'Natural Language :: Romanian',
    ],
    keywords='grub bootloader configuration linux soplos internationalization i18n',
    zip_safe=False,
    data_files=[
        ('share/applications', ['assets/org.soplos.grubeditor.desktop']),
        ('share/icons/hicolor/128x128/apps', ['assets/icons/org.soplos.grubeditor.png']),
        ('share/metainfo', ['debian/org.soplos.grubeditor.metainfo.xml']),
    ],
)