import settings
from mode import Mode

class Guessable():
    def __init__(self, *blacklist, modes, extra):
        self.logger = settings.init_logger(__name__)
        self.items = ([],[])
        self.modes = modes
        if not isinstance(extra, dict):
            raise TypeError("extra must be set to a dict")
        self.blacklist = []
        self.types = []
        for item in blacklist:
            if item:
                self.blacklist += [item]
        self.logger.debug('Blacklist set')
        for key, value in extra.items():
            self.types += [key]
            setattr(self, key, value)
        self.logger.debug('Extras set')

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
        else:
            self.__items = self.parse_items(items, modes)
            self.logger.debug('Items set')

    def _check_item_allowed(self, item, modes):
        if self.blacklist:
            if any(skip in item for skip in self.blacklist):
                self.logger.debug('Item %s not allowed', item)
                return False
        for mode in self.modes:
            for items in mode.items:
                if items in item and mode.name not in modes:
                    self.logger.debug('Item %s not allowed in set modes %s', item, modes)
                    return False
        return True

    def get_item(self, guess):
        for name, codes in self.items.items():
            if guess in codes:
                self.logger.debug('Item %s found', name)
                return name
        return None

    def parse_items(self, items, modes):
        """Searches for a item with the value of guess in its codes entry."""
        parsed_items = {}
        for item in items:
            if 'name' in item:
                if not self._check_item_allowed(item['name'], modes):
                    continue
            if 'codes' in item:
                codes = []
                for code in item['codes'].split(','):
                    codes += [code]
                parsed_items[item['name']] = codes
                self.logger.debug('Item %s with codes %s found', item['name'], codes)
            elif 'stages' in item:
                codes = []
                for stage in item['stages']:
                    if 'codes' in stage:
                        if any(code in stage['codes'].split(',') for code in codes):
                            continue
                        for code in stage['codes'].split(','):
                            codes += [code.strip()]
                parsed_items[item['name']] = codes
                self.logger.debug('Item %s with codes %s found', item['name'], codes)
        return parsed_items
