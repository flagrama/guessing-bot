"""This module holds the ExtraGuessable class"""
from . import settings

class ExtraGuessable():
    """This class tracks extra guessable items."""

    def __init__(self, name, extra_items):
        self.logger = settings.init_logger(__name__)
        self.__name = name
        self.__items = extra_items['items']
        self.__locations = extra_items['locations']

    def get_type(self):
        """Gets the type of item.

        Returns:
            string -- The type of item
        """

        return self.__name

    def get_count(self):
        """Gets the number of items.

        Returns:
            int -- The number of items
        """

        return len(self.__items)

    def get_items(self):
        """Gets the items.

        Returns:
            dict -- The items dictionary
        """

        return self.__items

    def get_locations(self):
        """Gets the locations.

        Returns:
            dict -- The locations dictionary
        """

        return self.__locations

    def get_item(self, item):
        """Gets an item by its codes.

        Arguments:
            item {string} -- The code to search for

        Returns:
            string -- The name of the item
        """

        for name, codes in self.__items.items():
            if item in codes:
                self.logger.debug('%s item %s found', self.__name, name)
                return name
        return None

    def get_location(self, location):
        """Gets a location by its codes.

        Arguments:
            location {string} -- The code to search for

        Returns:
            string -- The name of a location
        """

        for name, codes in self.__locations.items():
            if location in codes:
                self.logger.debug('%s location %s found', self.__name, name)
                return name
        return None
