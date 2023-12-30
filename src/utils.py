"""
Utilities for Gmail Scrapers
"""
import base64
import quopri
from datetime import datetime

import chardet


def decode_raw_msg(msg_raw: str, verbose: bool = False):
    # Decode the base64url encoded string
    msg = base64.urlsafe_b64decode(msg_raw.encode("ASCII"))
    # Decode quoted-printable encoding
    # This step is necessary since the email body is quoted-printable encoded
    # Verified from the email's Content-Transfer-Encoding header
    msg = quopri.decodestring(msg)

    # Detect any other encoding (utf-8, Windows-1252, etc.)
    detected_encoding = chardet.detect(msg)["encoding"]
    if verbose:
        print(f"🗝️ Detected encoding - {detected_encoding}")
    # Decode using the detected encoding
    msg = msg.decode(detected_encoding)
    return msg


def epoch2datetime(epoch_ms):
    epoch_ms = int(epoch_ms)
    return datetime.utcfromtimestamp(epoch_ms / 1000.0)
