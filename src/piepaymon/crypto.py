import logging

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

logger = logging.getLogger(__name__)


def generate_session_key() -> str:
    logger.debug("Generating session key...")

    # Generate private key (2048 bits, exponent=65537)
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    # Get public key in PEM format
    public_key = private_key.public_key()
    pem_key = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8")

    logger.debug("Successfully generated new session key.")
    return pem_key
