import unittest

from multiprocessing import Queue, Manager

from complete_simultaneus_random_strategy import CompleteSimultaneusRandomStrategy
from uwb_tag import UWBTag
from uwb_device import UWBDevice
from queuer import Queuer

class TestCompleteSimultaneusRandomStrategy(unittest.TestCase):
    def setUp(self) -> None:
        print("Testing complete simultaneus random strategy")
        anchor_1 = UWBDevice(None, None, "AA")
        anchor_2 = UWBDevice(None, None, "BB")
        anchor_3 = UWBDevice(None, None, "CC")
        anchor_4 = UWBDevice(None, None, "FF")
        tags_dict = {"DD": UWBTag("192.168.0.112", 7, "DD", [anchor_1, anchor_2, anchor_3, anchor_4]), "EE": UWBTag("192.168.0.113", 7, "EE", [anchor_1, anchor_2, anchor_3, anchor_4])}
        self.tags_managed = Manager().dict(tags_dict)
        self.queuer = Queuer(CompleteSimultaneusRandomStrategy(), queue_lower_limit=6, queue_upper_limit=9)


    def test_prepare_queue(self):
        q = Queue()

        self.queuer.encode_queue(self.tags_managed)
        self.queuer.fill_queue(q)
        self.assertEqual(q.qsize(), 6)

        tag_messages ={
            "DD": [],
            "EE": []
        }

        while not q.empty():
            message_encoded, ip, target_port = q.get()

            self.assertIsInstance(message_encoded, bytes)
            self.assertIsInstance(ip, str)
            self.assertIsInstance(target_port, int)

            message_decoded = message_encoded.decode('utf-8')

            tag_messages[message_decoded].append(message_decoded)

        self.assertEqual(len(tag_messages["DD"]), 3)
        self.assertEqual(len(tag_messages["EE"]), 3)

        self.assertEqual(tag_messages["DD"].count("AA"), 1)
        self.assertEqual(tag_messages["DD"].count("BB"), 1)
        self.assertEqual(tag_messages["DD"].count("CC"), 1)
        self.assertEqual(tag_messages["DD"].count("FF"), 1)

        self.assertEqual(tag_messages["EE"].count("AA"), 1)
        self.assertEqual(tag_messages["EE"].count("BB"), 1)
        self.assertEqual(tag_messages["EE"].count("CC"), 1)
        self.assertEqual(tag_messages["EE"].count("FF"), 1)

        