import base64

from telethon.crypto import AuthKey
from telethon.sessions import StringSession


def decode_session(session_string):
    """
    Decode a session string into a Telethon session.
    :param session_string:
    :return:
    """
    # Ensure the session starts with the correct version
    if not session_string.startswith("1"):
        raise ValueError("Invalid session version")

    # Remove the version byte and fix padding
    session_data = session_string[1:]
    session_data += "=" * (-len(session_data) % 4)  # Add padding if needed

    # Decode session string
    session_bytes = base64.b64decode(session_data)

    # Extract components
    dc_id = session_bytes[0]
    offset = 1
    if len(session_bytes) == 352:  # IPv4 format
        server_address = ".".join(map(str, session_bytes[offset:offset + 4]))
        offset += 4
    else:  # IPv6 format
        address_length = int.from_bytes(session_bytes[offset:offset + 2], "big")
        offset += 2
        server_address = session_bytes[offset:offset + address_length].decode("utf-8")
        offset += address_length

    port = int.from_bytes(session_bytes[offset:offset + 2], "big")
    offset += 2
    auth_key = session_bytes[offset:]

    # Create Telethon session
    session = StringSession()
    session.set_dc(dc_id, server_address, port)
    session.auth_key = AuthKey(data=auth_key)
    return session
