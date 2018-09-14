import os
from unittest import TestCase
import jstyleson
from guessing_game_bot.guessable import Guessables as GuessableClass
from guessing_game_bot.database import Mode

class GuessableTest(TestCase):
    def __init__(self, methodName):
        TestCase.__init__(self, methodName)
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'items.test.json')
        # TODO: Mock database instead of grabbing from json file
        with open(path) as items:
            self.json = jstyleson.load(items)

    def test_empty_properties(self):
        """Test that class properties are properly instantiated to falsy values"""

        guessables = GuessableClass()
        self.assertFalse(guessables.items)
        self.assertFalse(guessables.modes)

    def test_set_items(self):
        """Test that items property is no longer falsy after being set"""

        active_modes = []
        guessables = GuessableClass()
        guessables.items = (self.json['items'], active_modes)
        self.assertTrue(guessables.items)

    def test_set_modes(self):
        """Test that modes property is no longer falsy after being set"""

        mode_name = 'egg'
        mode_items = ['Child Trade']
        mode = Mode(mode_name, *mode_items)
        modes = [mode]
        guessables = GuessableClass(modes=modes)
        self.assertTrue(guessables.modes)

    def test_all_set_items(self):
        """Test that items is parsed to the correct values after being set"""

        active_modes = []
        guessables = GuessableClass()
        guessables.items = (self.json['items'], active_modes)
        self.assertTrue(guessables.items)
        self.assertIsInstance(guessables.items, dict)
        self.assertIn('Bow', guessables.items)
        self.assertListEqual(guessables.items['Bow'], ['bow'])
        self.assertIn('Stone of Agony', guessables.items)
        self.assertListEqual(guessables.items['Stone of Agony'],
                             ['agony', 'stoneofagony', 'stone', 'pieseed'])
        self.assertIn('Child Trade', guessables.items)
        self.assertListEqual(guessables.items['Child Trade'],
                             ['childegg', 'kidtrade', 'kidegg', 'weird',
                              'weirdegg', 'childcucco', 'cucco'])
        self.assertIn('Deku Keys', guessables.items)
        self.assertIn('Deku Treasures', guessables.items)
        self.assertIn('Deku Skulls', guessables.items)
        self.assertIn('Gold Skulltula Tokens', guessables.items)
        self.assertIn('Freebie Label', guessables.items)
        self.assertIn('Free Prize', guessables.items)
        self.assertIn('Forest Boss Key Badge', guessables.items)
        self.assertIn('Heart Container', guessables.items)

    def test_all_set_items_with_mode_in_constructor(self):
        """
        Test that items is parsed to the correct values after being set
        and the instance provided modes
        """

        mode_name = 'egg'
        mode_items = ['Child Trade']
        mode = Mode(mode_name, mode_items)
        modes = [mode]
        active_modes = []
        guessables = GuessableClass(modes=modes)
        guessables.items = (self.json['items'], active_modes)
        self.assertIsInstance(guessables.items, dict)
        self.assertIn('Bow', guessables.items)
        self.assertListEqual(guessables.items['Bow'], ['bow'])
        self.assertIn('Stone of Agony', guessables.items)
        self.assertListEqual(guessables.items['Stone of Agony'],
                             ['agony', 'stoneofagony', 'stone', 'pieseed'])
        self.assertNotIn('Child Trade', guessables.items)
        self.assertIn('Deku Keys', guessables.items)
        self.assertIn('Deku Treasures', guessables.items)
        self.assertIn('Deku Skulls', guessables.items)
        self.assertIn('Gold Skulltula Tokens', guessables.items)
        self.assertIn('Freebie Label', guessables.items)
        self.assertIn('Free Prize', guessables.items)
        self.assertIn('Forest Boss Key Badge', guessables.items)
        self.assertIn('Heart Container', guessables.items)

    def test_all_set_items_with_unknown_current_modes(self):
        """
        Test that items is parsed to the correct values after being set
        and provided modes
        """

        mode_name = 'egg'
        active_modes = [mode_name]
        guessables = GuessableClass()
        guessables.items = (self.json['items'], active_modes)
        self.assertIsInstance(guessables.items, dict)
        self.assertIn('Bow', guessables.items)
        self.assertListEqual(guessables.items['Bow'], ['bow'])
        self.assertIn('Stone of Agony', guessables.items)
        self.assertListEqual(guessables.items['Stone of Agony'],
                             ['agony', 'stoneofagony', 'stone', 'pieseed'])
        self.assertIn('Child Trade', guessables.items)
        self.assertListEqual(guessables.items['Child Trade'],
                             ['childegg', 'kidtrade', 'kidegg', 'weird',
                              'weirdegg', 'childcucco', 'cucco'])
        self.assertIn('Deku Keys', guessables.items)
        self.assertIn('Deku Treasures', guessables.items)
        self.assertIn('Deku Skulls', guessables.items)
        self.assertIn('Gold Skulltula Tokens', guessables.items)
        self.assertIn('Freebie Label', guessables.items)
        self.assertIn('Free Prize', guessables.items)
        self.assertIn('Forest Boss Key Badge', guessables.items)
        self.assertIn('Heart Container', guessables.items)

    def test_all_set_items_with_mode_in_current_modes(self):
        """
        Test that items is parsed to the correct values after being set
        and provided modes and the instance provided modes
        """

        mode_name = 'egg'
        mode_items = ['Child Trade']
        mode = Mode(mode_name, *mode_items)
        modes = [mode]
        active_modes = [mode_name]
        guessables = GuessableClass(modes=modes)
        guessables.items = (self.json['items'], active_modes)
        self.assertIsInstance(guessables.items, dict)
        self.assertIn('Bow', guessables.items)
        self.assertListEqual(guessables.items['Bow'], ['bow'])
        self.assertIn('Stone of Agony', guessables.items)
        self.assertListEqual(guessables.items['Stone of Agony'],
                             ['agony', 'stoneofagony', 'stone', 'pieseed'])
        self.assertIn('Child Trade', guessables.items)
        self.assertListEqual(guessables.items['Child Trade'],
                             ['childegg', 'kidtrade', 'kidegg', 'weird',
                              'weirdegg', 'childcucco', 'cucco'])
        self.assertIn('Deku Keys', guessables.items)
        self.assertIn('Deku Treasures', guessables.items)
        self.assertIn('Deku Skulls', guessables.items)
        self.assertIn('Gold Skulltula Tokens', guessables.items)
        self.assertIn('Freebie Label', guessables.items)
        self.assertIn('Free Prize', guessables.items)
        self.assertIn('Forest Boss Key Badge', guessables.items)
        self.assertIn('Heart Container', guessables.items)

    def test_parse_item(self):
        """Test that item in items can be retrieved"""

        active_modes = []
        guessables = GuessableClass()
        self.assertFalse(guessables.get_item('bow'))
        guessables.items = (self.json['items'], active_modes)
        self.assertTrue(guessables.get_item('bow'))
        self.assertIn(guessables.get_item('bow'), guessables.items)
        self.assertEqual(guessables.get_item('bow'), 'Bow')
        self.assertFalse(guessables.get_item('sm64'))
