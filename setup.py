from setuptools import setup, find_packages


#install_requires = open('requirements.txt').readlines()

setup(name='moxie-events',
    version='0.1',
    packages=find_packages(),
    description='Events module for Moxie',
    author='Mobile Oxford',
    author_email='mobileoxford@it.ox.ac.uk',
    url='https://github.com/ox-it/moxie-events',
    include_package_data=True,
    setup_requires=["setuptools"],
    #install_requires=install_requires,
    #test_suite="moxie_events.tests",
)
