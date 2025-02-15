import smtplib
import os
import time
from email.message import EmailMessage
from config import SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, TRUST_PEOPLE, ENCRYPTED_FOLDER, OWNER_NAME, OWNER_EMAIL
from modules.countdown import Countdown

class Emailer:
    @staticmethod
    def send_email(recipient, subject, body, attachments=[]):
        msg = EmailMessage()
        msg["From"] = SMTP_USERNAME
        msg["To"] = recipient
        msg["Subject"] = subject
        msg.set_content(body)

        msg.add_alternative(body, subtype="html")

        for file_path in attachments:
            if os.path.exists(file_path):
                with open(file_path, "rb") as f:
                    file_data = f.read()
                    file_name = os.path.basename(file_path)
                    msg.add_attachment(file_data, maintype="application", 
                                     subtype="octet-stream", filename=file_name)

        if not msg.is_multipart():
            print("❌ No valid attachments found, skipping email.")
            return False
    
        server = None
        try:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.connect(SMTP_SERVER, SMTP_PORT)
            server.ehlo()
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
            print(f"📧 Email sent to {recipient}")
            return True
        except smtplib.SMTPAuthenticationError:
            print("❌ SMTP Authentication Error. Please check username and password")
        except smtplib.SMTPServerDisconnected:
            print("❌ SMTP Server Connection Error")
        except smtplib.SMTPException as e:
            print(f"❌ SMTP Error: {str(e)}")
        finally:
            if server:
                try:
                    server.quit()
                except smtplib.SMTPServerDisconnected:
                    pass
        return False

    @staticmethod
    def send_warning_to_owner():
        countdown = Countdown()
        remaining_time = countdown.duration - (time.time() - countdown.last_renewal)
        warning_threshold = countdown.duration * 0.10

        if 0 < remaining_time <= warning_threshold and not countdown.warning_sent:
            subject = "⏳ Warning: Your countdown is about to expire!"
            body = f"""
            <html>
                <body style="font-family: Arial, sans-serif;">
                    <h2 style="color: #D32F2F;">⏳ Your Countdown is Running Out!</h2>
                    <p>Hello <strong>{OWNER_NAME}</strong>,</p>
                    <p>Your countdown timer is about to expire. If you still have access, please renew it now to prevent automatic file sharing.</p>
                    <p>Otherwise, your encrypted files will be sent to your trusted contacts soon.</p>
                    <p>🕒 <strong>Remaining Time:</strong> Less than 10% of your countdown duration.</p>
                    <p>🔗 <a href="https://github.com/SejiL/if-i-die"
                    style="color: #0277BD; text-decoration: none; font-weight: bold;">
                        Manage Your Timer
                    </a></p>
                </body>
            </html>
            """
            email_sent = Emailer.send_email(OWNER_EMAIL, subject, body)
            if email_sent:
                countdown.mark_warning_sent()
                print("⏳ Warning email sent to owner.")
        
    @staticmethod
    def send_expiry_notification_to_trusted_people():
        subject = f"🔒 {OWNER_NAME} has shared encrypted files with you"
        body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <h2 style="color: #D32F2F;">⏳ Countdown Expired - Access Granted</h2>
                <p><strong>{OWNER_NAME}</strong> has encrypted some files for you and set a countdown timer.</p>
                <p>Since the timer has expired, you are receiving these files because you are a trusted person.</p>

                <h3>📌 How to Decrypt the Files?</h3>
                <p>Follow the steps in the project documentation:</p>
                <p>
                    <a href="https://github.com/SejiL/if-i-die?tab=readme-ov-file#workflow-for-trusted-person"
                    style="color: #0277BD; text-decoration: none; font-weight: bold;">
                        🔗 Decryption Guide
                    </a>
                </p>

                <p>If you have any issues, please check the README file or contact other trusted people.</p>

                <p style="margin-top: 20px; font-size: 14px; color: #777;">
                    This is an automated message. Please do not reply.
                </p>
            </body>
        </html>
        """

        any_email_sent = False
        for username, info in TRUST_PEOPLE.items():
            recipient_email = info.get("email")
            archive_file = os.path.join(ENCRYPTED_FOLDER, f"{username}.tar.gz")

            if recipient_email and os.path.exists(archive_file):
                print(f"📤 Sending {archive_file} to {recipient_email}")
                email_sent = Emailer.send_email(recipient_email, subject, body, [archive_file])
                if email_sent:
                    any_email_sent = True
            else:
                print(f"⚠️ No email found for {username} or archive missing.")
        return any_email_sent

    @staticmethod
    def test_email(email):
        subject = "Test Email from if-i-die"
        repo_url = "https://github.com/SejiL/if-i-die"
        body = f"""\
        This is a test email. If you received this, SMTP is working!
        GitHub Repository: {repo_url}
        """
        readme_file = os.path.join("README.md")
        Emailer.send_email(email, subject, body, [readme_file])
