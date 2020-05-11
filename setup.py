from setuptools import setup, find_packages

setup(
    name='EnergyApp-CLI',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        energyapp=cli.cli:cli
    ''',
)