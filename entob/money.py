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


class Wallet(ValueObject):
    """
    examples:
        Wallet(moneys=[{"amount": 35.12, "currency": "USD"}])
        Wallet(moneys=[Money(amount=100_000, currency="EUR")])
    """

    moneys = Describe(
        types=list[Money],
        default=list,
        coerce=lambda value: list(map(Money, value)),
        nullable=False,
    )
