from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Util.Padding import pad
import os
import subprocess
import argparse
from config import TRUST_PEOPLE, INPUT_FOLDER, ENCRYPTED_FOLDER, PEM_FOLDER, DECRYPTED_FOLDER

class Encryptor:
    def convert_ssh_to_pem(self, ssh_key, key_name):
        """Convert the SSH public key to PEM format for a specific user."""
        # Convert SSH key to PEM format using subprocess and ssh-keygen
        pem_key_path = os.path.join(PEM_FOLDER, f"{key_name}.pem")

        # Create PEM folder if it doesn't exist
        os.makedirs(PEM_FOLDER, exist_ok=True)

        # Write the SSH public key to a file
        ssh_key_path = os.path.join(PEM_FOLDER, f"{key_name}_temp_ssh_key.pub")
        with open(ssh_key_path, 'w') as f:
            f.write(ssh_key)

        # Convert SSH public key to PEM
        convert_cmd = f"ssh-keygen -f {ssh_key_path} -e -m PEM > {pem_key_path}"
        subprocess.run(convert_cmd, shell=True, check=True)

        # Remove temporary SSH key file
        os.remove(ssh_key_path)

        print(f"✅ Converted SSH public key for {key_name} to PEM format: {pem_key_path}")
        return pem_key_path

    def encrypt_file(self, filename):
        """Encrypts any file with all trusted PEM keys using hybrid encryption (AES + RSA)."""
        input_file = os.path.join(INPUT_FOLDER, filename)
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"❌ File not found: {input_file}")

        # Encrypt with all trusted keys from config.yaml
        for key_name, key_data in TRUST_PEOPLE.items():
            pem_key_path = os.path.join(PEM_FOLDER, f"{key_name}.pem")
            if not os.path.exists(pem_key_path):
                # Convert SSH public key to PEM format and use as the PEM key for encryption
                print(f"✅ Converting SSH public key for {key_name} to PEM format.")
                pem_key_path = self.convert_ssh_to_pem(key_data['ssh_public_key'], key_name)

            # Step 1: Generate a random AES session key
            aes_key = get_random_bytes(32)  # AES-256
            cipher_aes = AES.new(aes_key, AES.MODE_CBC)

            # Step 2: Read the file and encrypt it using AES
            with open(input_file, 'rb') as f:
                plaintext = f.read()

            # Pad plaintext to make it a multiple of AES block size
            padded_data = pad(plaintext, AES.block_size)

            # Encrypt the padded data
            ciphertext = cipher_aes.encrypt(padded_data)

            # Save the encrypted file (iv + ciphertext)
            encrypted_file_path = os.path.join(ENCRYPTED_FOLDER, key_name, f"{filename}.enc")
            os.makedirs(os.path.dirname(encrypted_file_path), exist_ok=True)
            with open(encrypted_file_path, 'wb') as f_enc:
                f_enc.write(cipher_aes.iv + ciphertext)

            print(f"✅ AES Encrypted file: {encrypted_file_path}")

            # Step 3: Encrypt the AES key using RSA
            with open(pem_key_path, 'rb') as f_pem:
                rsa_key = RSA.import_key(f_pem.read())
            cipher_rsa = PKCS1_OAEP.new(rsa_key)
            encrypted_aes_key = cipher_rsa.encrypt(aes_key)

            # Save the encrypted AES key
            aes_key_file_path = os.path.join(ENCRYPTED_FOLDER, key_name, f"{filename}.aes_key.enc")
            with open(aes_key_file_path, 'wb') as f_aes_key:
                f_aes_key.write(encrypted_aes_key)

            print(f"✅ Encrypted AES key for {key_name}: {aes_key_file_path}")

    def encrypt_all_files(self):
        """Encrypts all files in the input folder with all the PEM keys."""
        input_files = os.listdir(INPUT_FOLDER)

        # Check if there are any input files
        if not input_files:
            print(f"❌ No files found in {INPUT_FOLDER}. Please add files to encrypt.")
            return

        # Encrypt each file in the input folder
        for filename in input_files:
            input_file = os.path.join(INPUT_FOLDER, filename)
            if not os.path.exists(input_file):
                print(f"❌ File not found: {input_file}")
                continue

            print(f"✅ Encrypting file: {filename}")
            try:
                self.encrypt_file(filename)  # Encrypt each file
            except Exception as e:
                print(f"❌ Failed to encrypt {filename}: {str(e)}")

