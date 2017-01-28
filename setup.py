from setuptools import setup

setup(
    name='street_art_nn',
    packages=['street_art_nn'],
    include_package_data=True,
    install_requires=[
        'flask',
        'geopy'
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
    ],
)
