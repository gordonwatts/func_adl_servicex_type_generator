from typing import Iterable, TypeVar

R = TypeVar("R")


class FADLStream(Iterable[R]):
    """Typing class to add `func_adl` stream operators to iterables

    This allows type checking and predictive engines to figure out what is available to
    the user when working with sequences and writing func adl.
    """

    def First(self) -> R:
        "Returns the first element in the sequence"
        ...

    def Count(self) -> int:
        "Return the number of elements in a sequence"
        ...
