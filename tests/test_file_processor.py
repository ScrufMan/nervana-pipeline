import os
import unittest

from file_processor import File
from lingua import Language


class TestFileProcessor(unittest.TestCase):
    def test_object_creates_full_path(self):
        cwd = os.getcwd()
        full_path = os.path.join(cwd, "sample_files", "sample.pdf")

        file = File(full_path)

        self.assertIsNotNone(file)
        self.assertEqual(file.path, full_path)

    def test_object_creates_relative_path(self):
        relative_path = "sample_files/sample.pdf"

        file = File(relative_path)

        self.assertIsNotNone(file)
        self.assertEqual(file.path, relative_path)

    def test_file_data_valid(self):
        file = File("sample_files/sample.pdf")

        self.assertEqual(file.filename, "sample")
        self.assertEqual(file.extension, ".pdf")

    def test_plaintext_extraction_valid(self):
        file = File("sample_files/sample.pdf")

        expected_value = """
































 A Simple PDF File 
 This is a small demonstration .pdf file - 

 just for use in the Virtual Mechanics tutorials. More text. And more 
 text. And more text. And more text. And more text. 

 And more text. And more text. And more text. And more text. And more 
 text. And more text. Boring, zzzzz. And more text. And more text. And 
 more text. And more text. And more text. And more text. And more text. 
 And more text. And more text. 

 And more text. And more text. And more text. And more text. And more 
 text. And more text. And more text. Even more. Continued on page 2 ...



 Simple PDF File 2 
 ...continued from page 1. Yet more text. And more text. And more text. 
 And more text. And more text. And more text. And more text. And more 
 text. Oh, how boring typing this stuff. But not as boring as watching 
 paint dry. And more text. And more text. And more text. And more text. 
 Boring.  More, a little more text. The end, and just as well. 


"""

        file.extract_plaintext()

        self.assertEqual(file.plaintext, expected_value)

    def test_language_detection_english(self):
        file = File("sample_files/sample.pdf")

        file.extract_plaintext()
        file.detect_language()

        self.assertEqual(file.lang, Language.ENGLISH)
