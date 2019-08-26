import os
import unittest

from fgdtools import FgdParse


class ParseTestCase(unittest.TestCase):
    def setUp(self):
        return

    def tearDown(self):
        return

    def test_bms(self):
        fgd = FgdParse('tests/fgds/bms/bms.fgd')
        self.assertTrue(fgd)

    def test_cs(self):
        fgd = FgdParse('tests/fgds/cs/halflife-cs.fgd')
        self.assertTrue(fgd)

    def test_csgo(self):
        fgd = FgdParse('tests/fgds/csgo/csgo.fgd')
        self.assertTrue(fgd)

    def test_cstrike(self):
        fgd = FgdParse('tests/fgds/css/cstrike.fgd')
        self.assertTrue(fgd)

    def test_dod(self):
        fgd = FgdParse('tests/fgds/dod/halflife-DOD2-expert.fgd')
        self.assertTrue(fgd)

    def test_dods(self):
        fgd = FgdParse('tests/fgds/dods/dod.fgd')
        self.assertTrue(fgd)

    def test_ep1(self):
        fgd = FgdParse('tests/fgds/ep1/cstrike.fgd')
        self.assertTrue(fgd)
        fgd = FgdParse('tests/fgds/ep1/dod.fgd')
        self.assertTrue(fgd)
        fgd = FgdParse('tests/fgds/ep1/halflife2.fgd')
        self.assertTrue(fgd)
        fgd = FgdParse('tests/fgds/ep1/hl2mp.fgd')
        self.assertTrue(fgd)
        fgd = FgdParse('tests/fgds/ep1/portal.fgd')
        self.assertTrue(fgd)
        fgd = FgdParse('tests/fgds/ep1/sdk.fgd')
        self.assertTrue(fgd)
        fgd = FgdParse('tests/fgds/ep1/tf.fgd')
        self.assertTrue(fgd)

    def test_garrysmod(self):
        fgd = FgdParse('tests/fgds/garrysmod/garrysmod.fgd')
        self.assertTrue(fgd)

    def test_hl(self):
        fgd = FgdParse('tests/fgds/hl/halflife.fgd')
        self.assertTrue(fgd)

    def test_hldc(self):
        fgd = FgdParse('tests/fgds/hldc/dmc.fgd')
        self.assertTrue(fgd)

    def test_hl2(self):
        fgd = FgdParse('tests/fgds/hl2/halflife2.fgd')
        self.assertTrue(fgd)

    def test_left4dead(self):
        fgd = FgdParse('tests/fgds/left4dead/left4dead.fgd')
        self.assertTrue(fgd)

    def test_left4dead2(self):
        fgd = FgdParse('tests/fgds/left4dead2/left4dead2.fgd')
        self.assertTrue(fgd)

    def test_orangebox(self):
        fgd = FgdParse('tests/fgds/orangebox/cstrike.fgd')
        self.assertTrue(fgd)
        fgd = FgdParse('tests/fgds/orangebox/dod.fgd')
        self.assertTrue(fgd)
        fgd = FgdParse('tests/fgds/orangebox/halflife2.fgd')
        self.assertTrue(fgd)
        fgd = FgdParse('tests/fgds/orangebox/hl2mp.fgd')
        self.assertTrue(fgd)
        fgd = FgdParse('tests/fgds/orangebox/portal.fgd')
        self.assertTrue(fgd)
        fgd = FgdParse('tests/fgds/orangebox/sdk.fgd')
        self.assertTrue(fgd)
        fgd = FgdParse('tests/fgds/orangebox/tf.fgd')
        self.assertTrue(fgd)

    def test_portal(self):
        fgd = FgdParse('tests/fgds/portal/portal.fgd')
        self.assertTrue(fgd)

    def test_portal2(self):
        fgd = FgdParse('tests/fgds/portal2/portal2.fgd')
        self.assertTrue(fgd)

    def test_ricochet(self):
        fgd = FgdParse('tests/fgds/ricochet/ricochet.fgd')
        self.assertTrue(fgd)

    def test_swarm(self):
        fgd = FgdParse('tests/fgds/swarm/swarm.fgd')
        self.assertTrue(fgd)

    def test_tf(self):
        fgd = FgdParse('tests/fgds/tf/tf.fgd')
        self.assertTrue(fgd)

    def test_tfc(self):
        fgd = FgdParse('tests/fgds/tfc/tf15f.fgd')
        self.assertTrue(fgd)

    def test_notfound(self):
        self.assertRaises(IOError, FgdParse,
                          'tests/fgds/not_a_file.fgd')
