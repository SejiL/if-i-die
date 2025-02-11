# If I Die

**If I Die** is a Python-based open-source project designed to ensure that your important files and messages are securely sent to a trusted person if you are unable to renew a countdown timer. This project encrypts your files with a trusted person's public SSH key, and if the timer expires, the encrypted files are sent via email. The recipient can decrypt the files using their private SSH key.

- [Features](#features)
- [How It Works](#how-it-works)
- [Security Considerations](#security-considerations)
- [Installation](#installation)
- [Workflow for User](#workflow-for-user)
- [Workflow for Trusted Person](#workflow-for-trusted-person)
- [Encryption and Decryption Process](#encryption-and-decryption-process)

## Features
- **Encrypt necessary files or documents**: Secure your sensitive files by encrypting them with a trusted person's public SSH key.
- **Countdown timer**: Set a countdown timer, and if you are unable to renew it, the project automatically sends encrypted files to your trusted person.
- **Email notifications**: Send encrypted files directly to the trusted person’s email with instructions on how to decrypt them using their private SSH key.
- **Secure and safe**: This system ensures that only the intended trusted person can access the files with their private SSH key.

## How It Works
1. **Prepare your files**: Add the files you want to protect and send.
2. **Choose your trusted person**: Set up your trusted person's public SSH key for encryption.
3. **Set the countdown timer**: Choose how long you want the system to wait before sending your files.
4. **Automatic delivery**: If the timer expires and you haven't renewed it, the system will automatically encrypt your files and send them to your trusted person’s email.

## Security Considerations
This project uses a hybrid encryption mechanism combining RSA and AES encryption.

- **RSA (asymmetric encryption)** is used to encrypt the AES session key with the trusted person's public RSA key. This ensures that only the trusted person with the corresponding private RSA key can decrypt the AES key.
- **AES (symmetric encryption)** is used to encrypt the actual file contents. AES-256 is used with CBC mode, which requires padding and an initialization vector (IV). The IV is stored alongside the encrypted file.
- Since AES-CBC does not provide integrity verification, it is important to ensure the encrypted files are not tampered with before decryption.

This hybrid encryption approach ensures that the AES key remains protected using RSA, while AES provides a fast and secure way to encrypt file contents.

## Installation
To use the project, clone the repository:
```bash
git clone https://github.com/SejiL/if-i-die.git
```

Navigate to the project directory:
```bash
cd if-i-die
```

Install the dependencies:
```bash
pip install -r requirements.txt
```

Make sure to configure the `config.yaml` file with necessary paths and keys before using the tool.
```bash
mv config.yaml.example config.yaml
```

## Workflow for User
1. **Prepare Configuration File**: Copy the example configuration file to config.yaml
   ```bash
   cp config.yaml.example config.yaml
   ```
   Then, open `config.yaml` and update the required values, such as trusted person's email and SSH public key.

2. **Encrypt Files**: Encrypt all files in the `files/input` folder with all available trusted person public keys:
   ```bash
   python main.py encrypt
   ```
3. **Renew Countdown Timer**: If you want to renew the countdown timer manually, you can use the following command:
   ```bash
   python main.py countdown renew
   ```

4. **Check Countdown Status**: To check how much time is left before the countdown expires, use:
   ```bash
   python main.py countdown status
   ```

## Workflow for Trusted Person
1. **Install Dependencies**: After receiving the encrypted files, you need to install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. **Receive Encrypted Files**: You will receive the encrypted files in the folder specified (e.g., via email).

3. **Decrypt Files**: To decrypt the files, use the following command:
   ```bash
   python main.py decrypt --key <path_to_private_ssh_key> --input <path_to_received_encrypted_files> --output <path_to_save_decrypted_files>
   ```
   - `--key`: Path to your private SSH key (e.g., `~/.ssh/id_rsa`).
   - `--input`: Path to the folder where the encrypted files are located.
   - `--output`: Path to the folder where the decrypted files will be saved.
4. **Access Decrypted Files**: After decryption, the decrypted files will be available in the folder specified in the `--target` option.

## Encryption and Decryption Process
This guide explains how to manually encrypt and decrypt files using RSA and AES encryption. It includes the commands to generate keys, encrypt files, and decrypt them on your own system. Follow these steps to understand how the encryption and decryption processes work.

### Encrypting a File:
1. **Convert SSH Public Key to PEM Format**: First, you need to convert your SSH public key to PEM format. This will allow you to encrypt the AES key using the RSA algorithm.
```bash
ssh-keygen -f ~/.ssh/id_rsa.pub -e -m PEM > public_key.pem
```

2. **Generate a Random Initialization Vector (IV)**: Create a random 16-byte initialization vector (IV) that will be used for AES encryption. This ensures that the encryption is secure.
```bash
openssl rand -out iv.bin 16
```

3. **Generate a Random AES Key**: Create a random 32-byte AES key that will be used to encrypt your file.
```bash
openssl rand -out aes_key.bin 32
```

4. **Encrypt the File Using AES (AES-256-CBC)**: Use AES-256-CBC encryption to encrypt your file with the generated AES key and IV. The `-pass` flag uses the AES key file to encrypt the data.
```bash
openssl enc -aes-256-cbc -in my_file.txt -out my_file.txt.enc -pass file:./aes_key.bin -pbkdf2 -iv $(xxd -p -c 16 iv.bin)
```

5. **Encrypt the AES Key Using RSA**: Use the RSA public key to encrypt the AES key. This ensures that only the owner of the private key can decrypt the AES key and access the original file.
```bash
openssl pkeyutl -encrypt -inkey public_key.pem -pubin -in aes_key.bin -out aes_key.enc
```

### Decrypting a File:
1. **Decrypt the AES Key Using Your RSA Private Key**: Use your private RSA key to decrypt the AES key. This step requires the private key associated with the public key used for encryption.
```bash
openssl pkeyutl -decrypt -inkey ~/.ssh/id_rsa -in aes_key.enc -out aes_key.bin
```

2. **Decrypt the File Using AES**: Use the decrypted AES key and the IV (which was used during encryption) to decrypt the file. The `-d` flag in `openssl enc` is used to specify decryption.
```bash
openssl enc -aes-256-cbc -d -in my_file.txt.enc -out my_file.txt.dec -pass file:./aes_key.bin -pbkdf2 -iv $(xxd -p -c 16 iv.bin)
```

### Notes:
- **Security Considerations**: The AES key is used to encrypt the file, and it is encrypted with your RSA public key to ensure that only the owner of the corresponding private key can decrypt it. The IV and AES key are essential for the encryption and decryption process.
- **Customization**: You can modify the filenames and paths in the commands to suit your specific use case.

