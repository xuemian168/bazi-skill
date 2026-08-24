import unittest

from classics.normalize import normalize


class NormalizeTest(unittest.TestCase):
    def test_strips_all_whitespace_including_fullwidth(self):
        self.assertEqual(normalize("能知 衰旺　之真机\t"), "能知衰旺之真机")

    def test_strips_spec_punctuation(self):
        self.assertEqual(
            normalize("能知衰旺之真机，其于三命之奥，思过半矣。"),
            "能知衰旺之真机其于三命之奥思过半矣",
        )

    def test_strips_ascii_punctuation(self):
        self.assertEqual(normalize("甲木,乙木.丙火!"), "甲木乙木丙火")

    def test_keeps_cjk_and_digits(self):
        self.assertEqual(normalize("十干12支"), "十干12支")

    def test_does_not_convert_traditional_to_simplified(self):
        self.assertNotEqual(normalize("學"), normalize("学"))

    def test_empty_input(self):
        self.assertEqual(normalize(""), "")


if __name__ == "__main__":
    unittest.main()
