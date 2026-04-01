import random
import string

_ALPHABET = string.ascii_letters + string.digits
_CODE_LENGTH = 7


def generate_code(length: int = _CODE_LENGTH) -> str:
    return "".join(random.choices(_ALPHABET, k=length))
