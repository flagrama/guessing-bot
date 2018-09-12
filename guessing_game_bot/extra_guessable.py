from . import settings

class ExtraGuessable():
    def __init__(self, name, extra_items):
        self.logger = settings.init_logger(__name__)
        self.__name = name
        self.__items = extra_items['items']
        self.__locations = extra_items['locations']

    def get_type(self):
        return self.__name

    def get_count(self):
        return len(self.__items)

    def get_items(self):
        return self.__items

    def get_locations(self):
        return self.__locations

    def get_item(self, item):
        for name, codes in self.__items.items():
            if item in codes:
                self.logger.debug('%s item %s found', self.__name, name)
                return name
        return None

    def get_location(self, location):
        for name, codes in self.__locations.items():
            if location in codes:
                self.logger.debug('%s location %s found', self.__name, name)
                return name
        return None
