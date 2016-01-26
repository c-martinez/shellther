try:
    from setuptools import setup
    extra = {
        'entry_points': {
            'console_scripts': ['shelter = shelter.scripts.run:main'],
        },
    }
except ImportError:
    from distutils.core import setup
    extra = {'scripts': ["bin/shelter"]}

REQUIREMENTS = [i.strip() for i in open("requirements.txt").readlines()]

setup(
    name="shelter",
    version="0.0.1",
    description="Shell logger and sync to Etherpad",
    long_description="Shell logger and sync to Etherpad",
    install_requires=REQUIREMENTS,
    author="Software Carpentry",
    # url="https://github.com/c-martinez/sc-shell/",
    packages=["shelter", "shelter.scripts", "shelter.engines"],
    classifiers=[
        "Programming Language :: Python",
    ],
    **extra)
