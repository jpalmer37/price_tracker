import json
import logging
import os
import subprocess
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Union


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
        self.recipients = (
            [recipients] if isinstance(recipients, str) else list(recipients)
        )
        self.subject = subject
        self.sendmail_path = sendmail_path

    def send(
        self,
        body_text: str | None = None,
        html_attachment_path: str | None = None,
    ) -> bool:
        """Send an email, optionally attaching an HTML file.

        Parameters
        ----------
        body_text : str, optional
            Plain-text body of the email.
        html_attachment_path : str, optional
            Path to an HTML file to attach.

        Returns
        -------
        bool
            True if sendmail exited successfully, False otherwise.
        """
        msg = MIMEMultipart("mixed")
        msg["Subject"] = self.subject
        msg["From"] = self.sender
        msg["To"] = ", ".join(self.recipients)

        if body_text is None and html_attachment_path:
            body_text = "Please see the attached HTML report."
        if body_text:
            msg.attach(MIMEText(body_text, "plain"))

        if html_attachment_path:
            self._attach_html_file(msg, html_attachment_path)

        return self._send_via_sendmail(msg)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _attach_html_file(msg: MIMEMultipart, path: str) -> None:
        """Read an HTML file from disk and attach it to *msg*."""
        filename = os.path.basename(path)
        with open(path, "r", encoding="utf-8") as fh:
            html_content = fh.read()

        attachment = MIMEBase("text", "html")
        attachment.set_payload(html_content.encode("utf-8"))
        encoders.encode_base64(attachment)
        attachment.add_header(
            "Content-Disposition", "attachment", filename=filename
        )
        msg.attach(attachment)

        logging.debug(json.dumps({
            "event_type": "email_html_attached",
            "filename": filename,
            "size_bytes": len(html_content),
        }))

    def _send_via_sendmail(self, msg: MIMEMultipart) -> bool:
        """Dispatch the composed message through the local sendmail binary."""
        try:
            process = subprocess.Popen(
                [self.sendmail_path, "-t", "-oi"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            _, stderr = process.communicate(msg.as_bytes())

            if process.returncode != 0:
                logging.error(json.dumps({
                    "event_type": "email_send_failed",
                    "returncode": process.returncode,
                    "stderr": stderr.decode(),
                }))
                return False

            logging.info(json.dumps({
                "event_type": "email_sent",
                "recipients": self.recipients,
                "subject": self.subject,
            }))
            return True

        except Exception as exc:
            logging.error(json.dumps({
                "event_type": "email_send_exception",
                "error": str(exc),
            }))
            return False
