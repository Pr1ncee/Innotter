from enum import Enum


class Mode(Enum):
    """
    Represents enumerated mods for accepting or denying follow requests.
    """
    DENY = 0
    ACCEPT = 1
