import unittest

from classics.normalize import normalize


class NormalizeTest(unittest.TestCase):
    def test_strips_all_whitespace_including_fullwidth(self):
        self.assertEqual(normalize("能知 衰旺　之真机	"), "能知衰旺之真机")

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

    def test_strips_curly_quotes(self):
        # Regression test for Unicode curly quotes (U+201C, U+201D, U+2018, U+2019)
        # These are common in PDF-extracted text and Chinese typesetting
        self.assertEqual(normalize("“能知衰旺”之真机"), "能知衰旺之真机")
        self.assertEqual(normalize("“其于三命”之奥"), "其于三命之奥")
        self.assertEqual(normalize("‘十干’与‘十支’"), "十干与十支")


if __name__ == "__main__":
    unittest.main()