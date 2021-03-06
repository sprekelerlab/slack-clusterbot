import setuptools

# read __version__ from clusterbot/version.py
exec(open('clusterbot/version.py').read())

setuptools.setup(
    name='slack-clusterbot',
    version=__version__,
    author='Denis Alevi',
    author_email='mail@denisalevi.com',
    description="Send messages from your Python scripts to Slack.",
    url='https://github.com/sprekelerlab/slack-clusterbot',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)'
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires='slackclient'
)
