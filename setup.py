from setuptools import setup

##TODO: UPDATE VERSION ON BUILD
setup(name='trakt_downloader',
      version='0.7',
      description="Ever remember a film and want to watch it right away? Well that used to be difficult. Until now.",
      url='https://github.com/TheSelectiveOppidan/trakt-downloader',
      author='The Selective Oppidan',
      author_email='theselectiveoppidan@gmail.com',
      license='MIT',
      packages=['trakt_downloader'],
      entry_points={
            'console_scripts': ['trakt-pull=trakt_downloader.trakt_pull:go']
      },
      install_requires=[
          'sqlalchemy',
          'deluge-client'
      ],
      zip_safe=False,
      python_requires='>=3.6')