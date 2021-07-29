from setuptools import setup

setup(
    name='socomote',
    version='0.0.1',
    packages=['socomote'],
    install_requires=[
        "soco >= 0.23.2",
        "getkey >= 0.6.5"
    ],
    description="Application for remote control of Sonos systems",
    author="Theo Dickson",
    author_email="tmsdickson@gmail.com",
    license='MIT',
)