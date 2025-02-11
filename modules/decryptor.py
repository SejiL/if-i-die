from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Util.Padding import unpad
import os
import argparse

class Decryptor:
    def decrypt_all_files(self, private_key_path, encrypted_folder, decrypted_folder):
        """Decrypts all encrypted files in the folder."""
        if not os.path.exists(encrypted_folder):
            raise FileNotFoundError(f"❌ Encrypted folder not found: {encrypted_folder}")

        # Create Decrypt folder if it doesn't exist
        os.makedirs(decrypted_folder, exist_ok=True)

        # List files in the encrypted folder
        for filename in os.listdir(encrypted_folder):
            # Skip AES key files and decrypt only `.enc` files
            if filename.endswith(".enc") and not filename.endswith(".aes_key.enc"):
                try:
                    print(f"✅ Decrypting file: {filename}")
                    self.decrypt_file(filename, private_key_path, encrypted_folder, decrypted_folder)
                except Exception as e:
                    print(f"❌ Failed to decrypt {filename}: {str(e)}")

    def decrypt_file(self, filename, private_key_path, encrypted_folder, decrypted_folder):
        """Decrypts a single encrypted file using the private RSA key."""
        encrypted_file_path = os.path.join(encrypted_folder, filename)
        aes_key_file_path = os.path.join(encrypted_folder, filename.replace(".enc", ".aes_key.enc"))

        if not os.path.exists(encrypted_file_path):
            raise FileNotFoundError(f"❌ Encrypted file not found: {encrypted_file_path}")

        if not os.path.exists(aes_key_file_path):
            raise FileNotFoundError(f"❌ AES key file not found for: {filename}")

        try:
            # Load the encrypted AES key
            with open(aes_key_file_path, 'rb') as f_aes_key:
                encrypted_aes_key = f_aes_key.read()

            # Load the private RSA key
            if not os.path.exists(private_key_path):
                raise FileNotFoundError(f"❌ Private key not found at {private_key_path}")

            with open(private_key_path, 'rb') as f_pem:
                private_rsa_key = RSA.import_key(f_pem.read())

            # Decrypt the AES key using RSA
            cipher_rsa = PKCS1_OAEP.new(private_rsa_key)
            aes_key = cipher_rsa.decrypt(encrypted_aes_key)

            # Load the encrypted file content
            with open(encrypted_file_path, 'rb') as f_enc:
                #iv, tag, ciphertext = [f_enc.read(x) for x in (16, 16, -1)]  # Read IV, tag, and ciphertext
                iv = f_enc.read(16)  # Read IV (first 16 bytes)
                ciphertext = f_enc.read()  # The rest is ciphertext


            # Decrypt the file using AES
            cipher_aes = AES.new(aes_key, AES.MODE_CBC, iv=iv)
            plaintext = unpad(cipher_aes.decrypt(ciphertext), AES.block_size)

            # Save the decrypted file
            decrypted_file_path = os.path.join(decrypted_folder, filename.replace(".enc", ""))
            os.makedirs(decrypted_folder, exist_ok=True)
            with open(decrypted_file_path, 'wb') as f_dec:
                f_dec.write(plaintext)

            print(f"✅ Decrypted file saved to: {decrypted_file_path}")

        except FileNotFoundError as e:
            print(f"❌ Error: {e}")
        except ValueError:
            print("❌ Decryption failed! The file might be corrupted or tampered with.")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
