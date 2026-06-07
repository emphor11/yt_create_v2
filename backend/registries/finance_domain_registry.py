from pydantic import BaseModel


class FinanceMechanism(BaseModel):
    key: str
    label: str
    description: str


class FinanceDomainRegistry:
    def __init__(self) -> None:
        self._mechanisms = {
            "payment_pain_reduction": FinanceMechanism(
                key="payment_pain_reduction",
                label="Payment pain reduction",
                description="Monthly framing makes the purchase feel less painful than the full price.",
            ),
            "affordability_illusion": FinanceMechanism(
                key="affordability_illusion",
                label="Affordability illusion",
                description="A smaller monthly number can hide the real total cost.",
            ),
        }

    def has_mechanism(self, mechanism: str) -> bool:
        return mechanism in self._mechanisms

    def get_mechanism(self, mechanism: str) -> FinanceMechanism:
        return self._mechanisms[mechanism]

    def allowed_mechanisms(self) -> set[str]:
        return set(self._mechanisms)

