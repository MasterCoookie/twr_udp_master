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
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result[0], 7, delta=0.05)
        self.assertAlmostEqual(result[1], 3, delta=0.05)
        self.assertAlmostEqual(result[2], 5, delta=0.05)
    
    def test_trilaterate_3d_4dists_random_2(self):
        anchor_1 = [2, 2, 2, 1.87]
        anchor_2 = [0, 0, 1, 1.87]
        anchor_3 = [3, 3, 3, 3.24]
        anchor_4 = [3, 4, 5, 4.74]

        result = trilaterate_3d_4dists([anchor_1, anchor_2, anchor_3, anchor_4])
        print(result)
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result[0], 1, delta=0.05)
        self.assertAlmostEqual(result[1], .5, delta=0.05)
        self.assertAlmostEqual(result[2], 2.5, delta=0.05)

    def test_trilaterate_3d_4dists_random_3(self):
        anchor_1 = [2, 2, 2, 1.87]
        anchor_2 = [0, 0, 1, 1.87]
        anchor_3 = [3, 3, 3, 3.24]
        anchor_4 = [0, 0, .5, 3.24]

        result = trilaterate_3d_4dists([anchor_1, anchor_2, anchor_3, anchor_4])
        print(result)
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result[0], 1, delta=0.05)
        self.assertAlmostEqual(result[1], .5, delta=0.05)
        self.assertAlmostEqual(result[2], 2.5, delta=0.05)

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

    def test_polynomial_regression(self):
        point_1 = [0, 0, 0, 0]
        point_2 = [1, 1, 1, 100]
        point_3 = [2, 2, 2, 200]

        result = polyfit_3d([point_1, point_2, point_3])
        print(result)
        self.assertAlmostEqual(result[0], 3, delta=0.05)
        self.assertAlmostEqual(result[1], 3, delta=0.05)
        self.assertAlmostEqual(result[2], 3, delta=0.05)


if __name__ == "__main__":
    unittest.main()
