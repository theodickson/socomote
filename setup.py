import os
from pathlib import Path

from setuptools import setup
from setuptools.command.install import install

class Install(install):

    def run(self):
        socomote_home = Path(
            os.environ.get('SOCOMOTE_HOME', '~/socomote')
        ).expanduser()
        socomote_home.mkdir(parents=True, exist_ok=True)

        config_file = socomote_home / "config.yaml"
        master_zone_file = socomote_home / "master_zone.yaml"

        if config_file.exists():
            # todo - verify config in case of upgrade
            pass
        else:
            # todo - copy default config
            pass

        if not master_zone_file.exists():
            pass

        super().run()

setup(
    name='socomote',
    version='0.0.2',
    packages=['socomote'],
    install_requires=[
        "pyyaml",
        "soco >= 0.23.2",
        "getkey >= 0.6.5"
    ],
    description="Application for remote control of Sonos systems",
    author="Theo Dickson",
    author_email="tmsdickson@gmail.com",
    license='MIT',
    cmdclass={
        'install': Install
    }
)