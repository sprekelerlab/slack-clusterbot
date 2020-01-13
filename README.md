# ClusterBot
This is a Slack bot that sends messages from your Python scripts to Slack.

## Installation
If you want to use ClusterBot on the Sprekelerlab cluster to
communicate with the Sprekelerlab Slack, follow
the instruction on this page. If you want to install the ClusterBot on a
different computer, follow [these instructions](wiki/Installation).

### Install Python package
Install this Python package in the Python environment you want to use it
   in, on the Sprekelerlab cluster:
  ```
  pip install git+https://github.com/sprekelerlab/slack-clusterbot.git@master
  ```
For communication, you need an authentication token. This token is stored on
the cluster under `/etc/slack-clusterbot` and all members of the cognition
group have read access. This token will be automatically loaded by the Python
package.

## Usage
With the following snippet, `ClusterBot` will send "Hello world!" to Denis
Alevi on Slack.
```python
from clusterbot import ClusterBot

cb = ClusterBot(user_name="Denis Alevi")
cb.print("Hello world!")
```
For authentication, the cluster uses a token that is stored in
`/etc/slack-clusterbot` that all members of the cognition group have read
access to. Please to no distribute the token.

There are a few configuration parameters that can either be passed as
arguments to `ClusterBot(...)` or stored in configuration files (a system
configuration file or a user configuration file). First, the system
configuration file is loaded, then the user configuration file (overwriting
settings from the system configuration file). Arguments passed to `ClusterBot`
overwrite settings from configuration files. These are the class parameters:
- **user_name**: Who to send the messages to. This needs to be the full name
  used in your Slack profile.
- **user_id**: This is your Slack user ID, which can be found in your profile
  settings. Your ID does not change while your username can (if you change
  it). If both, `user_id` and `user_name` are given, the `user_id` is used.
- **slack_token**: The *Bot User OAuth Access Token* used to grant permissions
  to interact with Slack.
- *system_config_file*: Location of the system config file. Default is
  `/etc/slack-clusterbot`.
- *user_config_file*: Location of the user config file. Default is
  `~/.slack-clusterbot`.

You can store the `user_name`, `user_id` and `slack_token` in your user config file.
To do so, create `~/.slack-clusterbot` with the following content:
```ini
[SLACK]
# Authentication token
#token = ...

[USER]
# User information (if `id` and `name` are given, `id` is used)
name = Denis Alevi
#id = ...
```
Now you can use `ClusterBot` without arguments:
```python
from clusterbot import ClusterBot

cb = ClusterBot()
cb.print("Hello world!")
```
This will use the username from the config file and send a message to Denis Alevi.
