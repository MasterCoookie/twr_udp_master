import unittest

from positioning_functions import *


class TestTrilaterate(unittest.TestCase):
    def setUp(self) -> None:
        return super().setUp()
    
    def test_trilaterate_3d_4dists_random(self):
        anchor_1 = [3, 4, 5, 4.12]
        anchor_2 = [2, 2, 2, 5.91]
        anchor_3 = [3, 3, 3, 4.47]
        anchor_4 = [0, 0, 1, 8.6]

        result = trilaterate_3d_4dists([anchor_1, anchor_2, anchor_3, anchor_4])
        print(result)
        self.assertAlmostEqual(result[0], 7, delta=0.05)
        self.assertAlmostEqual(result[1], 3, delta=0.05)
        self.assertAlmostEqual(result[2], 5, delta=0.05)

    def test_trilaterate_3d_4dists_zeros(self):
        anchor_1 = [1, 0, 0, 1.41]
        anchor_2 = [0, 1, 1, 1]
        anchor_3 = [1, 0, 1, 1]
        anchor_4 = [1, 1, 1, 1.41]

        result = trilaterate_3d_4dists([anchor_1, anchor_2, anchor_3, anchor_4])
        print(result)
        self.assertAlmostEqual(result[0], 0, delta=0.05)
        self.assertAlmostEqual(result[1], 0, delta=0.05)
        self.assertAlmostEqual(result[2], 1, delta=0.05)


if __name__ == "__main__":
    unittest.main()
