# If I Die

**If I Die** is a Python-based open-source project designed to ensure that your important files and messages are securely sent to a trusted person if you are unable to renew a countdown timer. This project encrypts your files with a trusted person's public SSH key, and if the timer expires, the encrypted files are sent via email. The recipient can decrypt the files using their private SSH key.

- [Features](#features)
- [How It Works](#how-it-works)
- [Security Considerations](#security-considerations)
- [Installation](#installation)
- [Workflow for User](#workflow-for-user)
- [Alternative Manual Method After Encryption](#alternative-manual-method-after-encryption)
- [Workflow for Trusted Person](#workflow-for-trusted-person)
- [Encryption and Decryption Process](#encryption-and-decryption-process)
- [Acknowledgments](#acknowledgments)

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
### 1. Prepare Configuration File
Copy the example configuration file to config.yaml
   ```bash
   cp config.yaml.example config.yaml
   ```
   Then, open `config.yaml` and update the required values, such as trusted person's email and SSH public key.

### 2. Encrypt Files
Encrypt all files in the `files/input` folder by creating a separate folder for each trusted person. The folder name must match the name specified in `config.yaml`. For example:
   ```bash
   files/input/sajjad/
   files/input/alice/
   ```
   To encrypt files for all trusted persons, run:
   ```bash
   python main.py encrypt
   ```
   Each person's files will be encrypted using their respective public SSH key. The encrypted files may be stored as a compressed `.tar.gz` archive in the `files/encrypted` directory.

### 3. Test Email Configuration
To test whether the SMTP settings in `config.yaml` are correctly configured, use the following command:
   ```bash
   python main.py email-test --email your-email@example.com
   ```
   This will attempt to send a test email to the specified address to verify that the email-sending functionality is working properly.

### 4. Countdown Timer
- **Renew Countdown Timer**: To manually renew the countdown timer, use the following command:
   ```bash
   python main.py countdown renew
   ```
   This will extend the countdown based on the `countdown_days` value set in `config.yaml`.

- **Check Countdown Status & Expiry**: To check whether the countdown timer has expired and take necessary actions, use:
   ```bash
   python main.py countdown check-expiry
   ```
   - If the timer **has expired**, the encrypted files will be sent to each trusted person via email.
   - If the timer is **about to expire**, the system will calculate **10% of the total countdown time** and send a reminder email to the project owner (defined in `config.yaml`), prompting them to run `renew` before expiration.
   - You can run `check-expiry` at any time to see how much time is left before expiration. The output will show the remaining **days**, **hours**, **minutes**, and **seconds** until the countdown ends.

### 5. Setup Automatic Countdown Check
To automatically check the countdown status every minute, you can add the following line to your crontab (`/etc/crontab`):
   ```bash
   * * * * * your-username cd /absolute/path/to/if-i-die && /absolute/path/to/python main.py countdown check-expiry >> /var/log/if-i-die.log 2>&1
   ```
   Make sure to:
   1. Replace `your-username` with your actual username
   2. Replace `/absolute/path/to/if-i-die` with the full path to the project directory
   3. Replace `/absolute/path/to/python` with the path to your Python executable (you can find it using `which python`)
   4. The log file `/var/log/if-i-die.log` will help you monitor the script's execution
   - You can also use `crontab -e` to add this entry to your user's crontab instead of the system-wide `/etc/crontab`.

## Alternative Manual Method After `Encryption`
If you prefer not to use the automatic email functionality of the project, you can manually schedule the delivery of the encrypted files.

After encrypting the files, you can upload each trusted person’s encrypted `.tar.gz` archive to your personal email account (e.g., Gmail) and schedule an email to be sent to them at a later date.

In the email body, you can include instructions on how to decrypt the files using information from this `README.md` or provide a direct link to the repository:

https://github.com/SejiL/if-i-die?tab=readme-ov-file#workflow-for-trusted-person

This ensures that your trusted person can manually access and decrypt the files when needed.

This method provides an alternative way to securely store and send the files outside the project's automated process.

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

## Acknowledgments
Parts of this project, including documentation and code improvements, were developed with the assistance of AI language models:
- ChatGPT (chatgpt.com)
- Claude (claude.ai)

We believe in transparency and acknowledge the role of AI assistance in improving this open-source project.