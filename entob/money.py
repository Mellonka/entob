from decimal import Decimal

from entob import Describe, ValueObject


class Money(ValueObject):
    """
    examples:
        Money(amount="35.12", currency="USD")
        Money(amount=100_000, currency="EUR")
    """

    amount = Describe(
        types=Decimal,
        coerce=lambda value: Decimal(value).quantize(
            Decimal("0.01"), rounding="ROUND_HALF_UP"
        ),
        nullable=False,
    )
    currency = Describe(types=str, enums=("RUB", "USD", "EUR"), nullable=False)
