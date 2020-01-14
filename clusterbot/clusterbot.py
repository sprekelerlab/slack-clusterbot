"""
Definition of the ClusterBot class.
"""

import os
import logging
import configparser
import slack
from slack.errors import SlackApiError


logger = logging.getLogger(__name__)


class ClusterBot(object):
    """
    With ClusterBot you can send messages from your Python scripts to Slack.
    """

    def __init__(self, user_name=None, user_id=None, slack_token=None,
                 user_config_file='~/.slack-clusterbot',
                 system_config_file='/etc/slack-clusterbot'):
        """
        Parameters
        ----------
        user_name : str
            Who to send the messages to. This needs to be the full name used in
            your Slack profile.
        user_id : str
            Who to send the message to. This is your Slack user ID, which can
            be found in your profile settings. Your ID does not change while
            your username can (if you change it). If both, user_id and
            user_name are given, the user_id is used.
        slack_token : str
            The ``Bot User OAuth Access Token`` used to grant permissions to
            interact with Slack.
        user_config_file : str
            Location of the system config file. Default is
            ``/etc/slack-clusterbot``.
        system_config_file : str
            Location of the user config file. Default is
            ``~/.slack-clusterbot``.
        """
        self.user_id = user_id
        self.user_name = user_name
        self.slack_token = slack_token
        self.user_config_file = user_config_file
        self.system_config_file = system_config_file
        self.config = configparser.ConfigParser()
        self.client = None
        self.conversation = None

        self._load_configs()
        self._connect_to_slack()
        self._check_user_exists()


    def _load_configs(self):
        # read system config first
        loaded = self.config.read([os.path.expanduser(self.system_config_file),
                                   os.path.expanduser(self.user_config_file)])
        if not loaded:
            logger.info(f"No configuration file found. Searched places: "
                         f"{self.system_config_file} and "
                         f"{self.user_config_file}.")
        else:
            for i, file in enumerate(loaded):
                if i == 0:
                    msg = f"Loading configuration from {file}."
                else:
                    msg = f"Updating configuration from {file}."
                logger.info(msg)

        exc_msg = (f"Pass it during class initialization or save it in one of "
                   f"the config files: {self.user_config_file} or "
                   f"{self.system_config_file}.")

        # load Slack token
        if self.slack_token is not None:
            logger.info("Slack token given in class instantiation.")
        else:
            try:
                self.slack_token = self._get_config_value('SLACK', 'token')
            except KeyError as err:
                raise AttributeError("No Slack token given. Ask the user who "
                                     "installed ClusterBot in your Slack "
                                     "workspace to give you the `Bot User "
                                     "OAuth Access Token`. It can be found at "
                                     f"https://api.slack.com/apps. {exc_msg}")

        # load user_id and/or user_name
        if self.user_id is not None:
            logger.info(f"Using user ID `{self.user_id}` given during class "
                         "initialization.")
        elif self.user_name is not None:
            logger.info(f"Using user_name `{self.user_name}` given during class "
                         "initialization.")

        if self.user_id is None and self.user_name is None:
            try:
                # use `id` from [USER] if given
                self.user_id = self._get_config_value('USER', 'id')
                logger.info(f"Loaded user ID `{self.user_id}` from config.")
            except KeyError:
                try:
                    # if `id` not given, find id from `name`
                    self.user_name = self._get_config_value('USER', 'name')
                    logger.info(f"Loaded username `{self.user_name}` from "
                                 "config.")
                except KeyError:
                    raise AttributeError("Need user ID or name for Slack "
                                         "communication. {exc_msg}")


    def _get_config_value(self, section, key):
        """
        Get config value from config file and fail with useful error message if
        config value is not found.
        """
        try:
            section_config = self.config[section]
        except KeyError:
            raise KeyError(f"Couldn't find section [{section}] in loaded config "
                           f"files.")

        try:
            value = section_config[key]
        except KeyError:
            raise KeyError(f"Couldn't find `{key}` in section [{section}] in "
                           f"loaded config files.")

        return value


    def _connect_to_slack(self):
        self.client = slack.WebClient(self.slack_token)
        self.client.auth_test()


    def _check_user_exists(self):

        if self.client is None:
            raise RuntimeError("Missing the webclient. Call _connect_to_slack() "
                               "first.")

        # get list of users in Slack team
        users_list = self.client.users_list()

        # if user_id is given, check if it is in the Slack workspace
        user_exists = False
        if self.user_id is not None:
            for member in users_list["members"]:
                if self.user_id == member['id']:
                    #user_object = member
                    user_exists = True

            if not user_exists:
                raise AttributeError(f"Couldn't find user with ID {user_id} in Slack team.")

        # if no user_id is given but a user_name, find ID from user_names in workspace
        else:
            # multiple users can have the same name (TODO: is real_name not unique?)
            matching_users = 0
            for member in users_list["members"]:
                membername = member['profile']['real_name']
                if self.user_name == membername:
                    self.user_id = member['id']
                    matching_users += 1

            if matching_users == 0:
                raise AttributeError(f"Couldn't find user with full name '{user_name}' in "
                                     f"Slack team.")
            elif matching_users > 1:
                raise AttributeError(f"Found multiple users with full name "
                                     f"'{user_name}' in Slack team. Please provide a "
                                     f"user ID in one of the configuration files. You can "
                                     f"find your ID in your Slack profile settings.")

    def _open_conversation(self):
        if self.client is None:
            raise RuntimeError("Missing the webclient. Call _connect_to_slack() "
                               "first.")

        self.conversation = self.client.conversations_open(users=self.user_id)


    def send(self, message):
        """
        Send ``message`` to Slack via ClusterBot.
        """

        if self.conversation is None:
            self._open_conversation()

        self.client.chat_postMessage(
            channel=self.conversation['channel']['id'],
            text=message
        )
