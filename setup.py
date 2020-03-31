from setuptools import setup

setup(name='trakt_downloader',
      version='0.1',
      description="Ever remember a film and want to watch it right away? Well that used to be difficult. Until now.",
      url='https://github.com/TheSelectiveOppidan/trakt-downloader',
      author='The Selective Oppidan',
      author_email='theselectiveoppidan@gmail.com',
      license='MIT',
      packages=['trakt_downloader'],
      install_requires=[
          'sqlalchemy',
          'deluge-client'
      ],
      zip_safe=False)