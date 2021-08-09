# ClusterBot
This is a Slack bot that sends messages from your Python scripts to Slack.

## Installation
If you want to use ClusterBot on the Sprekelerlab cluster to
communicate with the Sprekelerlab Slack, follow
the instruction on this page. If you want to install the ClusterBot on a
different computer, follow [these instructions](https://github.com/sprekelerlab/slack-clusterbot/wiki/Installation).

### Install Python package
Install this Python package in the Python environment you want to use it in
on the Sprekelerlab cluster. Activate the your correct conda environment (if
you are using conda) before installing this package:
```
pip install slack-clusterbot
```

Create the config file `~/.slack-clusterbot` on the cluster with the following
content:
```ini
[BOT]
# Custom system config file
system_config_file = /cognition/home/local/.slack-clusterbot

[USER]
# User information (if `id` and `name` are given, `id` is used)
name = Denis Alevi
#id = ...
```
Change the `name` or `id` option under the `[USER]` section to your full Slack
name or Slack ID. You can find both in your Sprekelerlab Slack profile.


## Usage

Have a look at and run the [example_script.py](example_script.py) to see if
everything works. In the following the different methods are explained in more
detail.

### Sending a message
With the following snippet, `ClusterBot` will send "Hello world!" and "Hello
again!" as two separate messages to the user specified in the config file (see
above).
```python
from clusterbot import ClusterBot

bot = ClusterBot()
bot.send("Hello world!")
bot.send("Hello again!")
```

### Replying to a message (opening a Thread)
With this snippet, you can send multiple messages in one thread, meaning
that the second and third message will be send as a reply to the first one.
```python
from clusterbot import ClusterBot

bot = ClusterBot()
message_id = bot.send("Hello world!")
bot.reply(message_id, "Hello again!")
bot.reply(message_id, "Hello once more!")
```

### Sending a message to someone else
You can write to someone else than specified in your config file by passing
the ``user_name`` or ``user_id`` parameter to your ``send()`` or ``reply``
calls:
```python
from clusterbot import ClusterBot

bot = ClusterBot()
message_id = bot.send("Hello world!", user_name='Denis Alevi')
bot.reply(message_id, "Hello world!", user_name='Denis Alevi')
```
This will send a message and a threaded reply to Denis Alevi.

### Editing a previously sent message
You can edit previously sent messages as follows:

```python
from clusterbot import ClusterBot

bot = ClusterBot()
message_id = bot.send("Hello world!", user_name='Denis Alevi')
bot.update(message_id, "An update!", user_name='Denis Alevi')
```

### Uploading files to a chat
You can also send files (e.g. images, PDFs, etc) via:

```python
from clusterbot import ClusterBot

bot = ClusterBot()
message_id = bot.upload(file_name="<path_to_file>",
                        message="Uploading Figure",
                        user_name="Denis Alevi")
# Or as send it as a response to a previous message
message_id = bot.upload(file_name="<path_to_file>",
                        message="Uploading Figure",
                        reply_to=message_id,
                        user_name="Denis Alevi")
```

### Progress Bars

We also support simple progress bars:

```python
from clusterbot import ClusterBot

bot = ClusterBot()
# Initialize a progress bar that counts up to 10
bot.init_pbar(max_value=10,
              user_name="Denis Alevi")
# Update the progress bar by an increment of 1
bot.update_pbar(user_name="Denis Alevi")
# Or directly set the value to a value
bot.update_pbar(current_value=5,
                user_name="Denis Alevi")
```

### Deleting a Message

You can also delete a previously send message:

```python
from clusterbot import ClusterBot

bot = ClusterBot()
message_id = bot.send("Hello world!", user_name='Denis Alevi')
bot.delete(message_id, user_name='Denis Alevi')
```

### Logging
If you want your Python script to inform you about sent Slack messages, you
can activate the logger:
```python
from clusterbot import activate_logger

activate_logger()
```
``activate_logger`` takes a optional argument ``loglevel``. The default is
`"INFO"`. If you set it to `"DEBUG"`, you will get debug information about
e.g. loaded config files etc.


### Configuration

For authentication, the cluster uses a token that is stored in
`/cognition/home/local/.slack-clusterbot` and that all members of the
cognition group have read access to. This token is autmatocially used if you
set up you use the configuration file shown above. Please do no
distribute the token as it grants read and write access to our Slack.

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
- **system_config_file**: Location of the system config file. Default is
  `/etc/slack-clusterbot`. This option can also be changed in your
  user_config_file.
- **user_config_file**: Location of the user config file. Default is
  `~/.slack-clusterbot`. This option can not be changed in you
  user_config_file.

In general, you can store the `user_name`, `user_id`, `slack_token` and
`system_config_file` in your config files. See the
[config_template](config_template) for details.
