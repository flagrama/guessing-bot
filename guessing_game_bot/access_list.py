"""Contains the AccessList class"""

import os
from . import settings
from .database import DbStreamer, WhitelistUser, BlacklistUser
from .twitch import TwitchAPI

class AccessList():
    """A class for controlling the streamer's whitelist and blacklist"""

    def __init__(self, channel_id, whitelist, blacklist):
        self.__logger = settings.init_logger(__name__)
        self.__channel_id = channel_id
        self.__whitelist = whitelist
        self.__blacklist = blacklist
        self.__twitch = TwitchAPI(os.environ['TWITCH_ID'])

    def user_in_whitelist(self, user_id):
        """Checks if user is in the whitelist.

        Arguments:
            user_id {int} -- The users's Twitch user-id

        Returns:
            WhitelistUser -- A WhitelistUser from the database
        """

        for allowed in self.__whitelist:
            if allowed.user_id == user_id:
                self.__logger.info('User %s is in the whitelist.', user_id)
                return allowed
        self.__logger.info('User %s is not in the whitelist.', user_id)
        return False

    def user_in_blacklist(self, user_id):
        """Checks if user is in the blacklist.

        Arguments:
            user_id {int} -- The users's Twitch user-id

        Returns:
            BlacklistUser -- A BlacklistUser from the database
        """

        for disallowed in self.__blacklist:
            if disallowed.user_id == user_id:
                self.__logger.info('User %s is in the blacklist.', user_id)
                return disallowed
        self.__logger.info('User %s is not in the blacklist.', user_id)
        return False

    def add_user_to_whitelist(self, username):
        """Adds a user to the whitelist

        Arguments:
            username {string} -- A user's Twitch username

        Returns:
            string -- a string meant to be sent to Twitch chat. If a falsy value is returned
            no message is sent to chat.
        """

        message = 'Unable to add user to whitelist'
        user_id = self._get_user_id_from_twitch(username)
        if not user_id:
            return message
        if self.user_in_whitelist(user_id):
            return message
        new_user = WhitelistUser(username=username, user_id=user_id)
        self.__whitelist.append(new_user)
        database = DbStreamer.objects.filter( #pylint: disable=no-member
            channel_id=self.__channel_id).modify(
                whitelist=self.__whitelist)
        database.save()
        message = 'User %s added to whitelist' % username
        self.__logger.info(message)
        return message

    def remove_user_from_whitelist(self, username):
        """Removes a user from the whitelist

        Arguments:
            username {string} -- A users's Twitch username

        Returns:
            string -- a string meant to be sent to Twitch chat. If a falsy value is returned
            no message is sent to chat.
        """

        message = 'Unable to remove user from whitelist'
        user_id = self._get_user_id_from_twitch(username)
        if not user_id:
            return message
        existing_user = self.user_in_whitelist(user_id)
        if not existing_user:
            return message
        self.__whitelist.remove(existing_user)
        database = DbStreamer.objects.filter( #pylint: disable=no-member
            channel_id=self.__channel_id).modify(
                whitelist=self.__whitelist)
        database.save()
        message = 'User %s removed from whitelist' % username
        self.__logger.info(message)
        return message

    def add_user_to_blacklist(self, username):
        """Adds a user to the blacklist

        Arguments:
            username {string} -- A user's Twitch username

        Returns:
            string -- a string meant to be sent to Twitch chat. If a falsy value is returned
            no message is sent to chat.
        """

        message = 'Unable to add user to blacklist'
        user_id = self._get_user_id_from_twitch(username)
        if not user_id:
            return message
        if self.user_in_blacklist(user_id):
            return message
        new_user = BlacklistUser(username=username, user_id=user_id)
        self.__blacklist.append(new_user)
        database = DbStreamer.objects.filter( #pylint: disable=no-member
            channel_id=self.__channel_id).modify(
                whitelist=self.__blacklist)
        database.save()
        message = 'User %s added to blacklist' % username
        self.__logger.info(message)
        return message

    def remove_user_from_blacklist(self, username):
        """Removes a user from the blacklist

        Arguments:
            username {string} -- A users's Twitch username

        Returns:
            string -- a string meant to be sent to Twitch chat. If a falsy value is returned
            no message is sent to chat.
        """

        message = 'Unable to remove user from blacklist'
        user_id = self._get_user_id_from_twitch(username)
        if not user_id:
            return message
        existing_user = self.user_in_blacklist(user_id)
        if not existing_user:
            return message
        self.__blacklist.remove(existing_user)
        database = DbStreamer.objects.filter( #pylint: disable=no-member
            channel_id=self.__channel_id).modify(
                whitelist=self.__blacklist)
        database.save()
        message = 'User %s removed from blacklist' % username
        self.__logger.info(message)
        return message

    def _get_user_id_from_twitch(self, username):
        return self.__twitch.get_user_id(username)
