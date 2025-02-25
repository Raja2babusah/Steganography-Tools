import unittest
import cv2
import numpy as np
import os
from steganography import encode, decode  # Assuming your script is named steganography.py

class TestSteganography(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """ Create a temporary image for testing """
        cls.test_image_path = "test_image.png"
        cls.encoded_image_path = "test_image_encoded.png"

        # Create a simple test image (100x100 white image)
        test_image = np.full((100, 100, 3), 255, dtype=np.uint8)
        cv2.imwrite(cls.test_image_path, test_image)

    @classmethod
    def tearDownClass(cls):
        """ Clean up test files after all tests """
        if os.path.exists(cls.test_image_path):
            os.remove(cls.test_image_path)
        if os.path.exists(cls.encoded_image_path):
            os.remove(cls.encoded_image_path)

    def test_encode_decode(self):
        """ Test encoding and decoding of a secret message """
        secret_message = "Hello, Steganography!"
        
        # Encode the message
        encoded_image = encode(self.test_image_path, secret_message, n_bits=2)
        cv2.imwrite(self.encoded_image_path, encoded_image)

        # Decode the message
        decoded_message = decode(self.encoded_image_path, n_bits=2)

        self.assertEqual(secret_message, decoded_message, "Decoded message does not match the original")

    def test_insufficient_space(self):
        """ Test encoding a message that is too large for the image """
        large_message = "A" * (100 * 100 * 3 * 2 // 8 + 10)  # Exceed image capacity

        with self.assertRaises(ValueError):
            encode(self.test_image_path, large_message, n_bits=2)

    def test_image_integrity(self):
        """ Ensure the image format is preserved after encoding """
        secret_message = "Test"
        encoded_image = encode(self.test_image_path, secret_message, n_bits=2)
        cv2.imwrite(self.encoded_image_path, encoded_image)

        # Load the original and encoded images
        original = cv2.imread(self.test_image_path)
        encoded = cv2.imread(self.encoded_image_path)

        self.assertEqual(original.shape, encoded.shape, "Encoded image shape does not match the original")

if __name__ == "__main__":
    unittest.main()
