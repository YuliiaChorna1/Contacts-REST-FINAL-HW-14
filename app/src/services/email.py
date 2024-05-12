from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.services.auth import auth_service
from src.conf.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=settings.mail_from,
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_FROM_NAME=settings.mail_from_name,
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates',
)


async def send_email(email: EmailStr, username: str, host: str):
    """
    Asynchronously sends an email to a specified recipient with a confirmation link.

    This function creates an email token for the specified recipient, constructs an email message with the token and other details, and then sends the email using the FastMail service. If there are any connection errors during this process, they are caught and printed.

    :param email: The recipient's email address.
    :type email: EmailStr
    :param username: The username of the recipient.
    :type username: str
    :param host: The host URL for the confirmation link.
    :type host: str

    :raises ConnectionErrors: If there are any issues with the connection during the email sending process.

    :return: None
    """
    try:
        token_verification = auth_service.create_email_token({"sub": email})
        message = MessageSchema(
            subject="Confirm your email ",
            recipients=[email],
            template_body={"host": host, "username": username, "token": token_verification},
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="email_template.html")
        print("Email sent")
    except ConnectionErrors as err:
        print(err)

