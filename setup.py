from setuptools import setup

setup(
    name='socomote',
    description="Application for remote control of Sonos systems",
    license='MIT',
    author="Theo Dickson",
    author_email="tmsdickson@gmail.com",
    version='0.0.4',
    packages=['socomote'],
    include_package_data=True,
    install_requires=[
        "pyyaml",
        "soco >= 0.23.2",
        "getkey >= 0.6.5"
    ],
)