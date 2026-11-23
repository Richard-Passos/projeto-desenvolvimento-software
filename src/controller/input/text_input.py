from typing import Protocol

from model.text_limits import TextLimits


class TextInput(Protocol):
    """What the InputController needs from the text box (the View).

    The TextBoxView fits it as it is. Depending on this and not on the
    pygame class keeps the controller free of pygame (and easy to test).
    """

    def text(self) -> str: ...

    def set_text(self, value: str) -> None: ...

    def is_generated(self) -> bool:
        """True while the text box exists on screen."""
        ...

    def limits(self) -> TextLimits: ...
