import unittest
from fgdtools.fgd import *


class FgdTestCase(unittest.TestCase):
    def setUp(self):
        return

    def tearDown(self):
        return

    # FgdEditorData
    def test_editor_data_str(self):
        class_type = 'include'
        data = "something.fgd"
        name = None
        editor_data = FgdEditorData(class_type, data, name)
        self.assertEqual(editor_data.class_type, class_type)
        self.assertEqual(editor_data.data, data)
        self.assertEqual(editor_data.name, name)

    def test_editor_data_tuple(self):
        class_type = 'mapsize'
        data = (-100, 100)
        name = None
        editor_data = FgdEditorData(class_type, data, name)
        self.assertEqual(editor_data.class_type, class_type)
        self.assertEqual(editor_data.data, data)
        self.assertEqual(editor_data.name, name)

    def test_editor_data_dict(self):
        class_type = 'AutoVisGroup'
        data = {'visgroups1': ['1', '2']}
        name = 'Custom'
        editor_data = FgdEditorData(class_type, data, name)
        self.assertEqual(editor_data.class_type, class_type)
        self.assertEqual(editor_data.data, data)
        self.assertEqual(editor_data.name, name)

    def test_editor_data_list(self):
        class_type = 'MaterialExclusion'
        data = ['materialfolder1', 'materialfolder2', 'materialfolder1']
        name = None
        editor_data = FgdEditorData(class_type, data, name)
        self.assertEqual(editor_data.class_type, class_type)
        self.assertEqual(editor_data.data, data)
        self.assertEqual(editor_data.name, name)

    def test_editor_data_str_fgd_str(self):
        class_type = 'include'
        data = "something.fgd"
        name = None
        editor_data = FgdEditorData(class_type, data, name)
        expected = '@include "something.fgd"'
        self.assertEqual(editor_data.fgd_str(), expected)

    def test_editor_data_tuple_fgd_str(self):
        class_type = 'mapsize'
        data = (-100, 100)
        name = None
        editor_data = FgdEditorData(class_type, data, name)
        expected = '@mapsize(-100, 100)'
        self.assertEqual(editor_data.fgd_str(), expected)

    def test_editor_data_dict_fgd_str(self):
        class_type = 'AutoVisGroup'
        data = {'visgroups1': ['1', '2']}
        name = 'Custom'
        editor_data = FgdEditorData(class_type, data, name)
        expected = '@AutoVisGroup = "Custom"\n[\n\t"visgroups1"\n\t[\n\t\t"1"\n\t\t"2"\n\t]\n]'
        self.assertEqual(editor_data.fgd_str(), expected)

    def test_editor_data_list_fgd_str(self):
        class_type = 'MaterialExclusion'
        data = ['materialfolder1', 'materialfolder2', 'materialfolder3']
        name = None
        editor_data = FgdEditorData(class_type, data, name)
        expected = '@MaterialExclusion\n[\n\t"materialfolder1"\n\t"materialfolder2"\n\t"materialfolder3"\n]'
        self.assertEqual(editor_data.fgd_str(), expected)

    def test_editor_data_repr(self):
        class_type = 'AutoVisGroup'
        data = {'visgroups1': ['1', '2']}
        name = 'Custom'
        editor_data = FgdEditorData(class_type, data, name)
        expect = "<FgdEditorData of type 'AutoVisGroup' named 'Custom', [...]>"
        self.assertEqual(repr(editor_data), expect)

    # FgdEntityInput
    def test_input_properties(self):
        name = 'onuser1'
        value_type = 'void'
        description = 'short desc1'
        input = FgdEntityInput(name, value_type, description)
        self.assertEqual(input.name, name)
        self.assertEqual(input.value_type, value_type)
        self.assertEqual(input.description, description)

    def test_input_schema(self):
        name = 'onuser2'
        value_type = 'void'
        description = 'short desc2'
        input = FgdEntityInput(name, value_type, description)
        self.assertEqual(input.schema['name'], name)
        self.assertEqual(input.schema['type'], value_type)
        self.assertEqual(input.schema['description'], description)

    def test_input_fgd_str(self):
        name = 'onuser3'
        value_type = 'void'
        description = 'short desc3'
        input = FgdEntityInput(name, value_type, description)
        expected = 'input onuser3(void) : "short desc3"'
        self.assertEqual(input.fgd_str(), expected)

    def test_input_repr(self):
        name = 'onuser4'
        value_type = 'void'
        description = 'short desc4'
        input = FgdEntityInput(name, value_type, description)
        expected = "<FgdEntityInput {'name': 'onuser4', " + \
                   "'value_type': 'void', " + \
                   "'description': 'short desc4'}>"
        self.assertEqual(repr(input), expected)

    # FgdEntityOutput
    def test_output_properties(self):
        name = 'onuser1'
        value_type = 'void'
        description = 'short desc1'
        output = FgdEntityOutput(name, value_type, description)
        self.assertEqual(output.name, name)
        self.assertEqual(output.value_type, value_type)
        self.assertEqual(output.description, description)

    def test_output_schema(self):
        name = 'onuser2'
        value_type = 'void'
        description = 'short desc2'
        output = FgdEntityOutput(name, value_type, description)
        self.assertEqual(output.schema['name'], name)
        self.assertEqual(output.schema['type'], value_type)
        self.assertEqual(output.schema['description'], description)

    def test_output_fgd_str(self):
        name = 'onuser3'
        value_type = 'void'
        description = 'short desc3'
        output = FgdEntityOutput(name, value_type, description)
        expected = 'output onuser3(void) : "short desc3"'
        self.assertEqual(output.fgd_str(), expected)

    def test_output_repr(self):
        name = 'onuser4'
        value_type = 'void'
        description = 'short desc4'
        output = FgdEntityOutput(name, value_type, description)
        expected = "<FgdEntityOutput {'name': 'onuser4', " + \
                   "'value_type': 'void', " + \
                   "'description': 'short desc4'}>"
        self.assertEqual(repr(output), expected)

    # FgdEntitySpawnflag
    def test_spawnflag_properties(self):
        value = 0
        display_name = 'spawnflag1'
        default_value = False
        spawnflag = FgdEntitySpawnflag(value, display_name, default_value)
        self.assertEqual(spawnflag.value, value)
        self.assertEqual(spawnflag.display_name, display_name)
        self.assertEqual(spawnflag.default_value, default_value)

    def test_spawnflag_schema(self):
        value = 2
        display_name = 'spawnflag2'
        default_value = False
        spawnflag = FgdEntitySpawnflag(value, display_name, default_value)
        self.assertEqual(spawnflag.schema['value'], value)
        self.assertEqual(spawnflag.schema['display_name'], display_name)
        self.assertEqual(spawnflag.schema['default_value'], default_value)

    def test_spawnflag_fgd_str(self):
        value = 1
        display_name = 'spawnflag3'
        default_value = True
        spawnflag = FgdEntitySpawnflag(value, display_name, default_value)
        self.assertEqual(spawnflag.fgd_str(), '1 : "spawnflag3" : 1')

    def test_spawnflag_repr(self):
        value = 1
        display_name = 'spawnflag3'
        default_value = True
        spawnflag = FgdEntitySpawnflag(value, display_name, default_value)
        expected = "<FgdEntitySpawnflag {'value': 1, " + \
                   "'display_name': 'spawnflag3', " + \
                   "'default_value': True}>"
        self.assertEqual(repr(spawnflag), expected)

    # FgdEntityPropertyChoice
    def test_choice_properties(self):
        value = 0
        display_name = 'choice1'
        choice = FgdEntityPropertyChoice(value, display_name)
        self.assertEqual(choice.value, value)
        self.assertEqual(choice.display_name, display_name)

    def test_choice_schema(self):
        value = 2
        display_name = 'choice2'
        choice = FgdEntityPropertyChoice(value, display_name)
        self.assertEqual(choice.schema['value'], value)
        self.assertEqual(choice.schema['display_name'], display_name)

    def test_choice_fgd_str(self):
        value = 1
        display_name = 'choice3'
        choice = FgdEntityPropertyChoice(value, display_name)
        self.assertEqual(choice.fgd_str(), '1 : "choice3"')

        value = "1"
        display_name = 'choice3'
        choice = FgdEntityPropertyChoice(value, display_name)
        self.assertEqual(choice.fgd_str(), '"1" : "choice3"')

    def test_choice_repr(self):
        value = 1
        display_name = 'choice3'
        choice = FgdEntityPropertyChoice(value, display_name)
        expected = "<FgdEntityPropertyChoice {'value': 1, " + \
                   "'display_name': 'choice3'}>"
        self.assertEqual(repr(choice), expected)
