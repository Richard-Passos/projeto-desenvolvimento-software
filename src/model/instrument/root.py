# TODO name, image translation logic and tests
class Instrument:
    def __init__(self, id: int) -> None:
        self._id = id

    def id(self) -> int:
        return self._id

    def name(self) -> str:
        return f'Name of {self._id}'

    def image(self) -> str:
        return f'Image of {self._id}'
