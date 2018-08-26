"""This module provides an interface for running a guessing game."""
import logging

class GuessingGame():
    """This is a class for running a guessing game."""
    def __init__(self):
        """The constructor for GuessingGame class."""
        logging.basicConfig()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        self.commands = ['!guess']

        self.medals = [
            'forest', 'fire', 'water', 'spirit', 'shadow', 'light'
        ]

        self.songs = [
            'lullaby', 'zelda', 'zeldas',
            'saria', 'sarias',
            'epona', 'eponas',
            'sunsong', 'sun', 'suns',
            'songoftime', 'time', 'sot',
            'songofstorms', 'storm', 'storms', 'sos',
            'minuet', 'greenote',
            'bolero', 'rednote',
            'serenade', 'bluenote',
            'requiem', 'orangenote',
            'nocturne', 'purplenote',
            'prelude', 'yellownote'
        ]

    def do_command(self, command):
        """
        The function to parse a command.

        Parameters:
            command (string[]): A list of the command and its arguments
        """
        try:
            command_name = command[0].lower()
            command_value = command[1].lower()

            if command_name == '!guess':
                item = self.parse_item(command_value)
                if not item:
                    self.logger.info('Item %s not found', command_value)
                    return
                self.logger.info('Item %s guessed', item)
        except IndexError:
            self.logger.error('Command missing arguments')

    # Integrate with the database in the future
    @staticmethod
    def parse_item(item):
        """
        Return the internal item name based on user provided string.

        Parameters:
            item (string): A code word for an item name.

        Returns:
            string: A string which contains the internal item name
        """
        if item in ['bow']:
            return 'Bow'
        if item in ['slingshot', 'seedbag']:
            return 'Slingshot'
        if item in ['nut', 'nuts', 'dekunuts']:
            return 'Deku Nuts'
        if item in ['agony', 'stoneofagony', 'stone', 'pieseed']:
            return 'Stone of Agony'
        if item in ['firearrow', 'firearrows', 'farrow', 'farrows']:
            return 'Fire Arrows'
        if item in ['icearrow', 'icearrows', 'iarrow', 'iarrows']:
            return 'Ice Arrows'
        if item in ['lightarrow', 'lightarrows', 'larrow', 'larrows']:
            return 'Light Arrows'
        if item in ['beans', 'magicbeans']:
            return 'Magic Beans'
        if item in ['sticks', 'dekusticks', 'stick', 'dekustick']:
            return 'Deku Sticks'
        if item in ['bombs', 'bombbag', 'bomb']:
            return 'Bomb Bag'
        if item in ['boomerang', 'boomer', 'rang', 'banana']:
            return 'Boomerang'
        if item in ['hookshot', 'hs', 'longshot', 'ls']:
            return 'Hookshot'
        if item in ['bombchu', 'bombchus', 'chus']:
            return 'Bombchus'
        if item in ['lens', 'lensoftruth', 'lot']:
            return 'Lens of Truth'
        if item in ['dinsfire', 'dins', 'din']:
            return 'Din\'s Fire'
        if item in ['faroreswind', 'farores', 'farore', 'fw']:
            return 'Farore\'s Wind'
        if item in ['nayruslove', 'nayrus', 'nayru', 'condom']:
            return 'Nayru\'s Love'
        if item in ['sword1', 'kokirisword']:
            return 'Kokiri Sword'
        if item in ['sword3', 'biggoronsword', 'biggoron', 'bgs']:
            return 'Biggoron Sword'
        if item in ['shield3', 'mirrorshield', 'mirror', 'mshield']:
            return 'Mirror Shield'
        if item in ['gorontunic', 'redtunic']:
            return 'Goron Tunic'
        if item in ['zoratunic', 'bluetunic']:
            return 'Zora Tunic'
        if item in ['ironboots', 'iboots', 'iron', 'irons']:
            return 'Iron Boots'
        if item in ['hoverboots', 'hboots', 'hover', 'hovers']:
            return 'Hover Boots'
        if item in ['hammer', 'megaton', 'megatonhammer']:
            return 'Megaton Hammer'
        if item in ['ocarina', 'fairyocarina', 'flute', 'oot']:
            return 'Ocarina'
        if item in ['bottle', 'rutonote', 'ruto']:
            return 'Bottle'
        if item in [
                'bracelet', 'lift',
                'silvergauntlets', 'lift2', 'silvers', 'silver', 'silvergaunt',
                'goldgauntlets', 'lift3', 'golds', 'golden', 'goldgaunt'
            ]:
            return 'Strength Upgrade'
        if item in ['silverscale', 'scale', 'goldscale', 'scale2']:
            return 'Diving Scale'
        if item in ['wallet']:
            return 'Wallet'
        if item in ['magic', 'doublemagic', 'magic2']:
            return 'Magic'
        if item in ['greenrupee']:
            return 'Validation'
        if item in ['childegg', 'kidtrade', 'kidegg', 'weird', 'weirdegg']:
            return 'Weird Egg'
        if item in [
                'adultegg', 'adulttrade', 'pocketegg',
                'adultcucco', 'pocketcucco',
                'cojiro', 'bluecucco',
                'mushroom', 'oddmushroom',
                'oddpotion', 'oddpoultice', 'potion',
                'saw', 'poachersaw',
                'brokensword',
                'perscription', 'script',
                'frog', 'eyeballfrog', 'eyeball',
                'eyedrops', 'drops',
                'claim', 'claimcheck'
            ]:
            return 'Adult Trade Item'
        return None
