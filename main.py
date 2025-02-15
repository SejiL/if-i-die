import argparse
from modules.encryptor import Encryptor
from modules.decryptor import Decryptor
from modules.countdown import Countdown
from modules.emailer import Emailer

def main():
    parser = argparse.ArgumentParser(description="Main utility for encryption, decryption, countdown timer")
    parser = argparse.ArgumentParser(
        description="Main utility for encryption, decryption, countdown timer - GitHub Repository: https://github.com/SejiL/if-i-die"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Encryption
    subparsers.add_parser("encrypt", help="Encrypt files in the input folder")
    
    # Decryption
    decrypt_parser = subparsers.add_parser("decrypt", help="Decrypt encrypted files.")
    decrypt_parser.add_argument("--key", type=str, required=True, help="Path to the private SSH key")
    decrypt_parser.add_argument("--input", type=str, required=True, help="Path to the folder containing encrypted files")
    decrypt_parser.add_argument("--output", type=str, required=True, help="Path to the folder to save decrypted files")

    # Countdown
    countdown_parser = subparsers.add_parser("countdown", help="Manage the countdown timer")
    countdown_subparsers = countdown_parser.add_subparsers(dest="countdown_command")
    
    # Renew countdown
    countdown_subparsers.add_parser("renew", help="Renew the countdown timer")

    # Check and send email if expired
    check_email_parser = countdown_subparsers.add_parser("check-expiry", help="Check countdown and send email if expired")

    # Check Email settings
    email_parser = subparsers.add_parser("email-test", help="Test email settings")
    email_parser.add_argument("--email", type=str, required=True, help="Your Email Address")

    args = parser.parse_args()

    if args.command == "encrypt":
        encryptor = Encryptor()
        encryptor.encrypt_all_files()

    elif args.command == "decrypt":
        decryptor = Decryptor()
        decryptor.decrypt_all_files(
            private_key_path=args.key,
            encrypted_folder=args.input,
            decrypted_folder=args.output
        )

    elif args.command == "countdown":
        if args.countdown_command == "renew":
            countdown = Countdown()
            countdown.renew()
            print(countdown.time_left())
        
        elif args.countdown_command == "check-expiry":
            countdown = Countdown()
            Emailer.send_warning_to_owner()
            if countdown.has_expired():
                if countdown.should_send_notification():
                    print("⏳ Countdown expired! Sending emails to trusted people...")
                    emailer = Emailer()
                    emails_sent = emailer.send_expiry_notification_to_trusted_people()
                    if emails_sent:
                        countdown.mark_notification_sent()
                    else:
                        print("⚠️ No emails were successfully sent, keeping notification status unchanged.")
                else:
                    print("⚠️ Countdown expired but notification cooldown is active.")
            else:
                print("✅ Countdown is still active.")
                print(countdown.time_left())
                
        else:
            countdown_parser.print_help()
            exit(1)

    elif args.command == "email-test":
        emailer = Emailer()
        emailer.test_email(email=args.email)

    else:
        parser.print_help()
        exit(1)

if __name__ == "__main__":
    main()

