try:
    from setuptools import setup
    extra = {
        'entry_points': {
            'console_scripts': ['shellther = shellther.scripts.run:main'],
        },
    }
except ImportError:
    from distutils.core import setup
    extra = {'scripts': ["bin/shellther"]}

REQUIREMENTS = [i.strip() for i in open("requirements.txt").readlines()]

setup(
    name="shellther",
    version="0.0.1",
    description="Shell logger and sync to Etherpad",
    long_description="Shell logger and sync to Etherpad",
    install_requires=REQUIREMENTS,
    author="Software Carpentry",
    # url="https://github.com/c-martinez/shellther/",
    packages=["shellther", "shellther.scripts", "shellther.engines"],
    classifiers=[
        "Programming Language :: Python",
    ],
    **extra)
