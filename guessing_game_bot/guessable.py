"""The module for the Guessables class"""
from .database import Mode
from .extra_guessable import ExtraGuessable
from . import settings

class Guessables():
    """This class tracks all the guessable items"""

    def __init__(self, modes=None, extra=None):
        if modes is None:
            modes = []
        if extra is None:
            extra = {}
        self.logger = settings.init_logger(__name__)
        self.__items = None
        self.__modes = None
        self.items = ({}, [])
        self.modes = modes
        self.extras = []
        self.extra_item_types = []
        if extra is None:
            extra = {}
        if not isinstance(extra, dict):
            raise TypeError("extra must be set to a dict")
        for key in extra:
            self.extras += [ExtraGuessable(key, extra[key])]
            self.extra_item_types += [key]
        self.logger.debug('Extra items set')

    @property
    def modes(self):
        return self.__modes

    @modes.setter
    def modes(self, modes):
        if not isinstance(modes, list):
            raise TypeError("modes must be set to a list")
        for mode in modes:
            if not isinstance(mode, Mode):
                raise TypeError("modes within list must set to a Mode")
        self.__modes = modes
        self.logger.debug('Modes set')

    @property
    def items(self):
        return self.__items

    @items.setter
    def items(self, val):
        try:
            items, modes = val
        except ValueError:
            message = "Pass an iterable with two items"
            self.logger.error(message)
            raise ValueError(message)
        if not isinstance(items, dict):
            raise TypeError("items must be a dict")
        else:
            self.__items = self.__parse_items(items, modes)
            self.logger.debug('Items set')

    def __get_extra_items(self, extra_items_type):
        for extra_items in self.extras:
            if extra_items_type == extra_items.get_type():
                return extra_items.get_items()
        return None

    def get_item(self, guess):
        """Retrieves an item from the item list by code

        Arguments:
            guess {string} -- The code of an itemm

        Returns:
            string -- The name of an item
        """

        for name, codes in self.__items.items():
            if guess in codes:
                self.logger.debug('Item %s found', name)
                return name
        return None

    def __check_item_allowed(self, guess_item, modes):
        for mode in self.__modes:
            for items in mode.items:
                if items in guess_item and mode.name not in modes:
                    self.logger.debug('Item %s not allowed in set modes %s', guess_item, modes)
                    return False
        return True

    def __parse_items(self, items, modes):
        parsed_items = {}
        for item, codes in items.items():
            if not self.__check_item_allowed(item, modes):
                continue
            parsed_items[item] = codes
            self.logger.debug('Item %s with codes %s found', item, codes)
        return parsed_items
