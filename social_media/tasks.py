import logging
import httpx
from social_media.config import config

logger = logging.getLogger(__name__)


class APIResponseError(Exception):
    pass


async def send_simple_mail(to: str, subject: str, body: str):
    logger.debug(f"Sending email to '{to[:3]}' with subject '{subject[:20]}'")
    async with httpx.AsyncClient() as client:
        end_point = f"https://api.mailgun.net/v3/{config.MAILGUN_DOMAIN}/messages"
        try:
            response = await client.post(
                end_point,
                auth=("api", config.MAILGUN_API_KEY),
                data={
                    "from": f"Noel Yang's Social Media <mailgun@{config.MAILGUN_DOMAIN}>",
                    "to": [to],
                    "subject": subject,
                    "text": body,
                },
            )
            response.raise_for_status()

            logger.debug(response.content)

            return response
        except httpx.HTTPStatusError as err:

            raise APIResponseError(
                f"API request to Mailgun failed with status code {err.response.status_code} and message {err.response.text}"
            ) from err


async def send_user_registration_email(email: str, confirmation_url: str):
    return await send_simple_mail(
        to=email,
        subject="Successfully signed up!",
        body=(
            f"hi {email}! You have successfully signed up to Noel Yang's social media."
            "Please click the link below to confirm your email address:"
            f"{confirmation_url}\n\nThanks"
        ),
    )
