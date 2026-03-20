import logging
import os
import subprocess
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Union

from scraper.logging_utils import log_event


class EmailSender:
    """Send emails with optional HTML file attachments via sendmail."""

    def __init__(
        self,
        sender: str,
        recipients: Union[str, List[str]],
        subject: str,
        sendmail_path: str = "/usr/sbin/sendmail",
    ):
        self.sender = sender
        self.recipients = [recipients] if isinstance(recipients, str) else list(recipients)
        self.subject = subject
        self.sendmail_path = sendmail_path

    def send(
        self,
        body_text: str | None = None,
        html_attachment_path: str | None = None,
    ) -> bool:
        if not self.recipients:
            log_event(logging.INFO, "email_skipped_no_recipients", subject=self.subject)
            return False

        message = self._build_message(body_text=body_text, html_attachment_path=html_attachment_path)
        return self._send_via_sendmail(message)

    def _build_message(
        self,
        body_text: str | None = None,
        html_attachment_path: str | None = None,
    ) -> MIMEMultipart:
        message = MIMEMultipart("mixed")
        message["Subject"] = self.subject
        message["From"] = self.sender
        message["To"] = ", ".join(self.recipients)

        if body_text is None and html_attachment_path:
            body_text = "Please see the attached HTML report."
        if body_text:
            message.attach(MIMEText(body_text, "plain"))

        if html_attachment_path:
            self._attach_html_file(message, html_attachment_path)

        return message

    def _attach_html_file(self, message: MIMEMultipart, path: str) -> None:
        filename = os.path.basename(path)
        with open(path, "r", encoding="utf-8") as handle:
            html_content = handle.read()

        attachment = MIMEBase("text", "html")
        attachment.set_payload(html_content.encode("utf-8"))
        encoders.encode_base64(attachment)
        attachment.add_header("Content-Disposition", "attachment", filename=filename)
        message.attach(attachment)

        log_event(
            logging.INFO,
            "email_html_attached",
            filename=filename,
            size_bytes=len(html_content),
        )

    def _send_via_sendmail(self, message: MIMEMultipart) -> bool:
        try:
            process = subprocess.Popen(
                [self.sendmail_path, "-t", "-oi"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            _, stderr = process.communicate(message.as_bytes())

            if process.returncode != 0:
                log_event(
                    logging.ERROR,
                    "email_send_failed",
                    returncode=process.returncode,
                    stderr=stderr.decode(),
                    recipients=self.recipients,
                    subject=self.subject,
                )
                return False

            log_event(logging.INFO, "email_sent", recipients=self.recipients, subject=self.subject)
            return True
        except Exception as exc:
            log_event(logging.ERROR, "email_send_exception", error=str(exc), subject=self.subject)
            return False
