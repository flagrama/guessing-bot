import jstyleson
import settings

class Guessable():
    def __init__(self, *blacklist, modes, extra):
        self.logger = settings.init_logger(__name__)
        with open('items.json') as items:
            self.items = jstyleson.load(items)
        self.logger.debug('Items loaded')
        self.blacklist = []
        self.modes = modes
        for item in blacklist:
            self.blacklist += [item]
        self.logger.debug('Blacklist set')
        for key, value in extra.items():
            setattr(self, key, value)
        self.logger.debug('Extras set')

    @property
    def modes(self):
        return self.__modes

    @modes.setter
    def modes(self, modes):
        if not isinstance(modes, list):
            raise TypeError("Modes must be set to a list")
        self.__modes = modes
        self.logger.debug('Modes set')

    def _check_items_allowed(self, item, modes):
        if any(skip in item for skip in self.blacklist):
            return False
        for mode in self.modes:
            if mode.name not in modes and item in mode.items:
                return False
        return True

    def parse_item(self, guess, modes):
        """Searches for a item with the value of guess in its codes entry."""
        for item in self.items:
            if 'name' in item:
                if not self._check_items_allowed(item['name'], modes):
                    self.logger.debug('Item %s not allowed in set modes %s', item['name'], modes)
                    continue
            if 'codes' in item:
                for code in item['codes'].split(','):
                    if guess in [code.strip()]:
                        self.logger.debug('Item %s found', item['name'])
                        return item['name']
            elif 'stages' in item:
                codes = []
                for stage in item['stages']:
                    if 'codes' in stage:
                        if any(code in stage['codes'].split(',') for code in codes):
                            continue
                        for code in stage['codes'].split(','):
                            codes += [code.strip()]
                if guess in codes:
                    self.logger.debug('Item %s found', item['name'])
                    return item['name']
        return None
