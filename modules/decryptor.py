import tarfile
import os
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Util.Padding import unpad

class Decryptor:
    # Decrypt all files in the encrypted folder
    def decrypt_all_files(self, private_key_path, encrypted_folder, decrypted_folder):
        if not os.path.exists(encrypted_folder):
            raise FileNotFoundError(f"❌ Encrypted folder not found: {encrypted_folder}")

        os.makedirs(decrypted_folder, exist_ok=True)

        for filename in os.listdir(encrypted_folder):
            if filename.endswith(".tar.gz"):
                print(f"📦 Extracting {filename} ...")

                with tarfile.open(os.path.join(encrypted_folder, filename), "r:gz") as tar:
                    tar.extractall(path=decrypted_folder)

                print(f"✅ Extracted {filename} to {decrypted_folder}")

        self.decrypt_user_files(private_key_path, decrypted_folder)

    # Decrypt all files in the decrypted folder
    def decrypt_user_files(self, private_key_path, decrypted_folder):
        for root, _, files in os.walk(decrypted_folder):
            for filename in files:
                if filename.endswith(".enc") and not filename.endswith(".aes_key.enc"):
                    try:
                        print(f"✅ Decrypting file: {filename}")
                        self.decrypt_file(filename, private_key_path, root)
                    except Exception as e:
                        print(f"❌ Failed to decrypt {filename}: {str(e)}")

    # Decrypt a single file
    def decrypt_file(self, filename, private_key_path, folder_path):
        encrypted_file_path = os.path.join(folder_path, filename)
        aes_key_file_path = os.path.join(folder_path, filename.replace(".enc", ".aes_key.enc"))

        if not os.path.exists(encrypted_file_path) or not os.path.exists(aes_key_file_path):
            print(f"❌ Encrypted file or key missing: {filename}")
            return

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
                iv = f_enc.read(16)  # Read IV (first 16 bytes)
                ciphertext = f_enc.read()  # The rest is ciphertext

            # Decrypt the file using AES
            cipher_aes = AES.new(aes_key, AES.MODE_CBC, iv=iv)
            plaintext = unpad(cipher_aes.decrypt(ciphertext), AES.block_size)

            # Save the decrypted file
            decrypted_file_path = os.path.join(folder_path, filename.replace(".enc", ""))
            with open(decrypted_file_path, 'wb') as f_dec:
                f_dec.write(plaintext)

            print(f"✅ Decrypted file saved to: {decrypted_file_path}")
        
        except FileNotFoundError as fnf:
            print(f"❌ Private key not found: {str(fnf)}")
        except Exception as e:
            print(f"❌ RSA Private Key Import Error: {str(e)}")
