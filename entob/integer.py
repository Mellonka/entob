from typing import Callable

from entob import Describe


class BoundedInteger(Describe):
    def __init__(
        self,
        minimum: int | float = float("-inf"),
        maximum: int | float = float("+inf"),
        readonly: bool = False,
        coerce: Callable = int,
    ):
        self.minimum = minimum
        self.maximum = maximum
        super().__init__(
            types=int,
            nullable=False,
            validate=lambda value: self.minimum <= value <= self.maximum,
            coerce=coerce,
            readonly=readonly,
        )


class NonNegativeInteger(BoundedInteger):
    def __init__(self, readonly: bool = False, coerce: Callable = int):
        super().__init__(minimum=0, readonly=readonly, coerce=coerce)


class PositiveInteger(BoundedInteger):
    def __init__(self, readonly: bool = False, coerce: Callable = int):
        super().__init__(minimum=1, readonly=readonly, coerce=coerce)


class NegativeInteger(BoundedInteger):
    def __init__(self, readonly: bool = False, coerce: Callable = int):
        super().__init__(maximum=-1, readonly=readonly, coerce=coerce)


class NonPositiveInteger(BoundedInteger):
    def __init__(self, readonly: bool = False, coerce: Callable = int):
        super().__init__(maximum=0, readonly=readonly, coerce=coerce)
