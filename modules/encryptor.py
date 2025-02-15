from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Util.Padding import pad
import os
import subprocess
import tarfile
import shutil
from config import TRUST_PEOPLE, INPUT_FOLDER, ENCRYPTED_FOLDER, PEM_FOLDER

class Encryptor:
    # Convert SSH public key to PEM format
    def convert_ssh_to_pem(self, ssh_key, key_name):
        try:
            pem_key_path = os.path.join(PEM_FOLDER, f"{key_name}.pem")
            os.makedirs(PEM_FOLDER, exist_ok=True)
            
            ssh_key_path = os.path.join(PEM_FOLDER, f"{key_name}_temp_ssh_key.pub")
            with open(ssh_key_path, 'w') as f:
                f.write(ssh_key)
                
            result = subprocess.run(
                f"ssh-keygen -f {ssh_key_path} -e -m PEM > {pem_key_path}",
                shell=True,
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                raise Exception(f"Key conversion error: {result.stderr}")
            
            return pem_key_path
        except OSError as oe:
            print(f"❌ System Error: {str(oe)}")
            raise
        except subprocess.SubprocessError as se:
            print(f"❌ ssh-keygen execution error: {str(se)}")
            raise
        finally:
            if os.path.exists(ssh_key_path):
                os.remove(ssh_key_path)

    # Compress and cleanup the encrypted files
    def compress_and_cleanup(self, key_name):
        user_folder = os.path.join(ENCRYPTED_FOLDER, key_name)
        archive_path = os.path.join(ENCRYPTED_FOLDER, f"{key_name}.tar.gz")

        if os.path.exists(user_folder):
            with tarfile.open(archive_path, "w:gz") as tar:
                tar.add(user_folder, arcname=key_name)

            shutil.rmtree(user_folder)

            file_size = os.path.getsize(archive_path)  # Get the compressed file size
            print(f"✅ Compressed file created: {archive_path} ({file_size / 1024 / 1024:.2f} MB)")
            if file_size > 25 * 1024 * 1024:  # 25MB limit
                print(f"❌ File size exceeds 25MB. Process stopped for {key_name}.")
                os.remove(archive_path)  # Remove the large file
                raise Exception(f"❌ Compressed file for {key_name} is too large ({file_size / 1024 / 1024:.2f} MB). Process aborted.")

            print(f"✅ Compressed and cleaned up: {archive_path}")

    # Encrypt all files in the input folder
    def encrypt_all_files(self):
        for key_name in TRUST_PEOPLE.keys():
            user_input_folder = os.path.join(INPUT_FOLDER, key_name)
                
            if not os.path.exists(user_input_folder) or not os.path.isdir(user_input_folder):
                print(f"⚠️ No input folder found for {key_name}, skipping.")
                continue

            input_files = os.listdir(user_input_folder)

            if not input_files:
                print(f"⚠️ No files found in {user_input_folder}, skipping.")
                continue

            for filename in input_files:
                print(f"✅ Encrypting file: {filename} for {key_name}")
                try:
                    self.encrypt_file(filename, key_name)
                except Exception as e:
                    print(f"❌ Failed to encrypt {filename} for {key_name}: {str(e)}")

            self.compress_and_cleanup(key_name)

    # Encrypt a single file
    def encrypt_file(self, filename, key_name):
        input_file = os.path.join(INPUT_FOLDER, key_name, filename)

        if not os.path.exists(input_file):
            raise FileNotFoundError(f"❌ File not found: {input_file}")

        pem_key_path = os.path.join(PEM_FOLDER, f"{key_name}.pem")
        if not os.path.exists(pem_key_path):
            print(f"✅ Converting SSH public key for {key_name} to PEM format.")
            pem_key_path = self.convert_ssh_to_pem(TRUST_PEOPLE[key_name]['ssh_public_key'], key_name)

        aes_key = get_random_bytes(32)
        cipher_aes = AES.new(aes_key, AES.MODE_CBC)

        with open(input_file, 'rb') as f:
            plaintext = f.read()

        padded_data = pad(plaintext, AES.block_size)
        ciphertext = cipher_aes.encrypt(padded_data)

        encrypted_file_path = os.path.join(ENCRYPTED_FOLDER, key_name, f"{filename}.enc")
        os.makedirs(os.path.dirname(encrypted_file_path), exist_ok=True)
        with open(encrypted_file_path, 'wb') as f_enc:
            f_enc.write(cipher_aes.iv + ciphertext)

        print(f"✅ AES Encrypted file: {encrypted_file_path}")

        with open(pem_key_path, 'rb') as f_pem:
            rsa_key = RSA.import_key(f_pem.read())
        cipher_rsa = PKCS1_OAEP.new(rsa_key)
        encrypted_aes_key = cipher_rsa.encrypt(aes_key)

        aes_key_file_path = os.path.join(ENCRYPTED_FOLDER, key_name, f"{filename}.aes_key.enc")
        with open(aes_key_file_path, 'wb') as f_aes_key:
            f_aes_key.write(encrypted_aes_key)

        print(f"✅ Encrypted AES key for {key_name}: {aes_key_file_path}")
