import os
import tempfile
import unittest

from scripts.secure_profile_storage import SecureProfileStore, Fernet


@unittest.skipIf(Fernet is None, "cryptography not installed")
class SecureProfileStorageTests(unittest.TestCase):
    def test_roundtrip(self):
        with tempfile.TemporaryDirectory() as td:
            store = SecureProfileStore(enabled=True, storage_dir=td, master_key="test-master-key")
            payload = {"host": "example.local", "user": "operator", "tags": ["lab"]}
            path = store.save_profile("server", "lab1", payload)
            self.assertTrue(os.path.exists(path))
            loaded = store.load_profile("server", "lab1")
            self.assertEqual(loaded, payload)


if __name__ == "__main__":
    unittest.main()
