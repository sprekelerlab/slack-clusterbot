"""
Definition of the ClusterBot class.
"""

import os
import logging
import configparser
import slack
from .progress_bar import ProgressBar


logger = logging.getLogger(__name__)


class ClusterBot(object):
    """
    With ClusterBot you can send messages from your Python scripts to Slack.
    """

    def __init__(
        self,
        user_name=None,
        user_id=None,
        slack_token=None,
        user_config_file=None,
        system_config_file=None,
    ):
        """
        Parameters
        ----------
        user_name : str, optional
            Who to send the messages to. This needs to be the full name used in your
            Slack profile.
        user_id : str, optional
            Who to send the message to. This is your Slack user ID, which can be found
            in your profile settings. Your ID does not change while your username can
            (if you change it). If both, user_id and user_name are given, the user_id is
            used.
        slack_token : str, optional
            The ``Bot User OAuth Access Token`` used to grant permissions to interact
            with Slack.
        user_config_file : str, optional
            Location of the user config file. If None, default location
            (``~/.slack-clusterbot``) is used.
        system_config_file : str, optional
            Location of the system config file. If None, location loaded from user
            config file or default location (``/etc/slack-clusterbot``) is used.
        """
        self.default_user = {"id": user_id, "name": user_name}
        self.slack_token = slack_token

        self.user_config_file = user_config_file
        if self.user_config_file is None:
            # set default
            self.user_config_file = "~/.slack-clusterbot"

        self.system_config_file = system_config_file
        self.system_config_file_as_param = True
        if self.system_config_file is None:
            # set default
            self.system_config_file = "/etc/slack-clusterbot"
            self.system_config_file_as_param = False
        else:
            logger.debug(
                f"Changed system config file to {self.system_config_file} during class "
                f"initialization."
            )

        self.config = configparser.ConfigParser()
        self.client = None
        self.conversations = {}
        self.users_list = None

        self._load_configs()
        self._connect_to_slack()

        # Verify user information with Slack
        u_id, u_name = self._verify_user(
            user_id=self.default_user["id"], user_name=self.default_user["name"]
        )
        self.default_user["id"] = u_id
        self.default_user["name"] = u_name

    def _load_configs(self):
        # Check if system config file was changed in class init or through user
        # config file. If changed in class init, it overwrites user config option.
        if not self.system_config_file_as_param:
            # load user config to see if another system config file is given
            loaded_user_config = self.config.read(
                os.path.expanduser(self.user_config_file)
            )
            if loaded_user_config:
                if self.config.has_option("BOT", "system_config_file"):
                    self.system_config_file = self.config["BOT"]["system_config_file"]
                    logger.debug(
                        f"Changed system config file to {self.system_config_file} "
                        f"through user config file at {self.user_config_file}"
                    )
                # remove config options and reload after system config
                self.config.clear()

        # read system config first
        loaded = self.config.read(
            [
                os.path.expanduser(self.system_config_file),
                os.path.expanduser(self.user_config_file),
            ]
        )
        if not loaded:
            logger.debug(
                f"No configuration file found. Searched places: "
                f"{self.system_config_file} and {self.user_config_file}."
            )
        else:
            for i, file in enumerate(loaded):
                if i == 0:
                    msg = f"Loading configuration from {file}."
                else:
                    msg = f"Updating configuration from {file}."
                logger.debug(msg)

        exc_msg = (
            f"Pass it during class initialization or save it in one of "
            f"the config files: {self.user_config_file} or "
            f"{self.system_config_file}"
        )

        # load Slack token
        if self.slack_token is not None:
            logger.debug("Slack token given in class instantiation.")
        else:
            if self.config.has_option("BOT", "token"):
                self.slack_token = self.config["BOT"]["token"]
            else:
                raise AttributeError(
                    f"No Slack token given. Ask the user who installed ClusterBot in "
                    f"your Slack workspace to give you the `Bot User OAuth Access "
                    f"Token`. It can be found at fhttps://api.slack.com/apps. "
                    f"{exc_msg} as ``token`` option under the ``[BOT]`` section."
                )

        # load default user_id and/or user_name
        if self.default_user["id"] is not None:
            logger.debug(
                f"Using default user ID `{self.default_user['id']}` given during class "
                f"initialization."
            )
        elif self.default_user["name"] is not None:
            logger.debug(
                f"Using default user_name `{self.default_user['name']}` given during "
                f"class initialization. "
            )

        if self.default_user["id"] is None and self.default_user["name"] is None:
            if self.config.has_option("USER", "id"):
                self.default_user["id"] = self.config["USER"]["id"]
                logger.debug(
                    f"Loaded user ID `{self.default_user['id']}` from " "config."
                )
            elif self.config.has_option("USER", "name"):
                # if `id` not given, find id from `name`
                self.default_user["name"] = self.config["USER"]["name"]
                logger.debug(
                    f"Loaded username `{self.default_user['name']}` " "from config."
                )
            else:
                raise AttributeError(
                    f"Need user ID or name for Slack communication. {exc_msg} as "
                    f"``id`` or ``name`` option under the ``[USER]`` section"
                )

    def _connect_to_slack(self):
        self.client = slack.WebClient(self.slack_token)
        self.client.auth_test()

    def _verify_user(self, user_id=None, user_name=None):
        """
        Check if user with user_name or user_id exist and return user_id.
        """

        if user_id is None and user_name is None:
            raise ValueError("Need ``user_id`` or ``user_name``. Both are None.")

        if self.client is None:
            raise RuntimeError(
                "Missing the webclient. Call _connect_to_slack() " "first."
            )

        if self.users_list is None:
            # get list of users in Slack team
            self.users_list = self.client.users_list()

        # if user_id is given, check if it is in the Slack workspace
        user_exists = False
        if user_id is not None:
            for member in self.users_list["members"]:
                if user_id == member["id"]:
                    # user_object = member
                    user_exists = True
                    _user_name = member["profile"]["real_name"]
                    if user_name is not None and user_name != _user_name:
                        logger.warning(
                            f"The user name associated with the given user ID "
                            f"('{_user_name}') is different from the explicitly passed "
                            f"user name ('{user_name}'). Sending message to the former."
                        )
                    user_name = _user_name

            if not user_exists:
                raise AttributeError(
                    f"Couldn't find user with ID ``{user_id}`` " "in Slack team."
                )

        # if no user_id is given but a user_name, find ID from user_names in workspace
        else:
            # multiple users can have the same name (TODO: is real_name not unique?)
            matching_users = 0
            for member in self.users_list["members"]:
                membername = member["profile"]["real_name"]
                if user_name == membername:
                    user_id = member["id"]
                    matching_users += 1

            if matching_users == 0:
                raise AttributeError(
                    f"Couldn't find user with full name '{user_name}' in Slack team."
                )
            elif matching_users > 1:
                raise AttributeError(
                    f"Found multiple users with full name '{user_name}' in Slack team. "
                    f"Please provide a user ID in one of the configuration files. You "
                    f"can find your ID in your Slack profile settings."
                )

        return user_id, user_name

    def _open_conversation(self, user_id):
        if self.client is None:
            raise RuntimeError(
                "Missing the webclient. Call _connect_to_slack() " "first."
            )

        self.conversations[user_id] = self.client.conversations_open(users=user_id)

    def send(self, message, reply_to=None, user_name=None, user_id=None):
        """
        Send ``message`` to Slack via ClusterBot.

        Parameters
        ----------
        message : str
            Message to send.
        reply_to : str, optional
            The ID (``ts`` value) of the message to reply to. This creates a thread (if
            not already created) and replies there. The ID
        user_name : str, optional
            Who to send the message to. This needs to be the full name used in your
            Slack profile. If None and user_id is None, use the default user (loaded
            during class initialization or from your config files).
        user_id : str, optional
            Who to send the message to. This is a Slack user ID, which can be found in
            the profile settings. If both, user_id and user_name are given, the user_id
            is used. If both are None, use the default user (loaded during class
            initialization or from your config files).

        Returns
        -------
        ts : str
            ID of sent message.
        """
        if user_name is None and user_id is None:
            # use default user, ID already check in __init__
            user_name = self.default_user["name"]
            user_id = self.default_user["id"]

        if not user_id in self.conversations:
            # get user ID (and check it is valid)
            user_id, user_name = self._verify_user(user_name=user_name, user_id=user_id)
            self._open_conversation(user_id)

        channel = self.conversations[user_id]["channel"]["id"]

        # TODO test if passing ts=None works as well
        if reply_to is None:
            response = self.client.chat_postMessage(channel=channel, text=message)
            logger.info(f"Sent message to '{user_name}' (ID: '{user_id}'): {message}")
        else:
            response = self.client.chat_postMessage(
                channel=channel, text=message, thread_ts=reply_to
            )
            logger.info(f"Sent reply to '{user_name}' (ID: '{user_id}'): {message}")

        return response.data["ts"]

    def reply(self, ts, message, **kwargs):
        """
        Reply to a message on Slack via ClusterBot.

        Parameters
        ----------
        ts : str
            The ID of the message to reply to. Returned by ``send()`` or ``reply()``.
        message : str
            Message to send.
        kwargs : dict, optional
            Keyword arguments passed to ``send()``. These are ``user_name`` and
            ``user_id`` (optional). See ``send()`` docstring for details.

        Returns
        -------
        ts : str
            ID of sent message.
        """

        return self.send(message, reply_to=ts, **kwargs)

    def upload(self, file_name, message, reply_to=None, user_name=None, user_id=None):
        """
        Upload a file to slack.

        Parameters
        ----------
        file_name : str
            Path to file that will be uploaded to slack.
        ts : str
            The ID of the message to reply to. Returned by ``send()`` or ``reply()``.
        message : str
            Message to send.
        reply_to : str, optional
            The ID (``ts`` value) of the message to reply to. This creates a thread (if
            not already created) and replies there. The ID
        kwargs : dict, optional
            Keyword arguments passed to ``send()``. These are ``user_name`` and
            ``user_id`` (optional). See ``send()`` docstring for details.

        Returns
        -------
        ts : str
            ID of sent message.
        """
        if user_name is None and user_id is None:
            # use default user, ID already check in __init__
            user_name = self.default_user["name"]
            user_id = self.default_user["id"]

        if not user_id in self.conversations:
            # get user ID (and check it is valid)
            user_id, user_name = self._verify_user(user_name=user_name, user_id=user_id)
            self._open_conversation(user_id)

        channel = self.conversations[user_id]["channel"]["id"]
        if reply_to is None:
            response = self.client.files_upload(
                channels=channel, initial_comment=message, file=file_name,
            )
            logger.info(f"Sent file to '{user_name}' (ID: '{user_id}'): {message}")
        else:
            response = self.client.files_upload(
                channels=channel,
                initial_comment=message,
                file=file_name,
                thread_ts=reply_to,
            )
            logger.info(f"Sent file to '{user_name}' (ID: '{user_id}'): {message}")
        f_id = response.data["file"]["ims"][0]
        m_id = response.data["file"]["shares"]["private"][f_id][0]["ts"]
        return m_id

    def update(self, edit_id: str, message: str, user_name=None, user_id=None):
        """
        Upload a file to slack.

        Parameters
        ----------
        message : str
            Message to replace old one with.
        edit_to : str
            The ID (``ts`` value) of the message to edit.
        kwargs : dict, optional
            Keyword arguments passed to ``send()``. These are ``user_name`` and
            ``user_id`` (optional). See ``send()`` docstring for details.

        Returns
        -------
        ts : str
            ID of sent message.
        """
        if user_name is None and user_id is None:
            # use default user, ID already check in __init__
            user_name = self.default_user["name"]
            user_id = self.default_user["id"]

        if not user_id in self.conversations:
            # get user ID (and check it is valid)
            user_id, user_name = self._verify_user(user_name=user_name, user_id=user_id)
            self._open_conversation(user_id)

        channel = self.conversations[user_id]["channel"]["id"]
        _ = self.client.chat_update(channel=channel, ts=edit_id, text=message,)
        logger.info(f"Updated message to '{user_name}' (ID: '{user_id}'): {message}")

    def delete(self, delete_id: str, user_name=None, user_id=None):
        """
        Upload a file to slack.

        Parameters
        ----------
        delete_id : str
            Message to delete.
        kwargs : dict, optional
            Keyword arguments passed to ``send()``. These are ``user_name`` and
            ``user_id`` (optional). See ``send()`` docstring for details.

        Returns
        -------
        ts : str
            ID of sent message.
        """
        if user_name is None and user_id is None:
            # use default user, ID already check in __init__
            user_name = self.default_user["name"]
            user_id = self.default_user["id"]

        if not user_id in self.conversations:
            # get user ID (and check it is valid)
            user_id, user_name = self._verify_user(user_name=user_name, user_id=user_id)
            self._open_conversation(user_id)

        channel = self.conversations[user_id]["channel"]["id"]
        _ = self.client.chat_delete(channel=channel, ts=delete_id,)
        logger.info(f"Deleted message to '{user_name}' (ID: '{user_id}')")

    def init_pbar(self, max_value: int, width=80, ts=None, **kwargs):
        """
        Initialize a progress bar.

        Parameters
        ----------
        max_value : int
            Maximal value that the progress bar counter can take.
        width : int
            The width of the progress bar.
        kwargs : dict, optional
            Keyword arguments passed to ``send()``. These are ``user_name`` and
            ``user_id`` (optional). See ``send()`` docstring for details.
        """
        # TODO: Allow for multiple pbars running at the same time
        self.pbar = ProgressBar(max_value, width=width)
        message = self.pbar.init()
        self.pbar_id = self.send(message, reply_to=ts, **kwargs)

    def update_pbar(self, current_value=None, **kwargs):
        """
        Update an existing progress bar.

        Parameters
        ----------
        update_step : int
            Value by which to increment the progress bar.
        kwargs : dict, optional
            Keyword arguments passed to ``send()``. These are ``user_name`` and
            ``user_id`` (optional). See ``send()`` docstring for details.
        """
        message_new = self.pbar.update(current_value)
        self.update(self.pbar_id, message_new, **kwargs)
