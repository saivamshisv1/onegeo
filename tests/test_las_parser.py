import unittest

from app.las_parser import parse_las_text


SAMPLE = """~Version Information
 VERS. 2.0
~Curve Information
 DEPT.M : Depth
 GR.API : Gamma Ray
 RHOB.G/C3 : Density
~A
1000.0 45.2 2.35
1000.5 48.7 2.31
1001.0 -999.25 2.29
"""


class LasParserTests(unittest.TestCase):
    def test_parses_curves_and_rows(self):
        data = parse_las_text(SAMPLE)
        self.assertEqual(data.curves, ["DEPT", "GR", "RHOB"])
        self.assertEqual(len(data.depth), 3)
        self.assertIsNone(data.rows[2]["GR"])


if __name__ == "__main__":
    unittest.main()
