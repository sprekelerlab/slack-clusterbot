import setuptools

# read __version__ from clusterbot/version.py
exec(open('clusterbot/version.py').read())

setuptools.setup(
    name='slack-clusterbot',
    version=__version__,
    author='Denis Alevi',
    author_email='mail@denisalevi.com',
    description="Send messages from your Python scripts to Slack.",
    long_description=("This package sends messages as ``ClusterBot`` from your "
                      "Python scripts to your Slack workspace. Instructions on "
                      "how to set up `ClusterBot` on Slack can be found "
                      "[here](https://github.com/sprekelerlab/slack-clusterbot/wiki/Installation)."),
    long_description_content_type='text/markdown',
    url='https://github.com/sprekelerlab/slack-clusterbot',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent'
    ],
    python_requires='>=3.6',
    install_requires='slackclient'
)
