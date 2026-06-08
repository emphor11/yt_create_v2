from pydantic import BaseModel


class ComponentDefinition(BaseModel):
    component: str
    required_roles: list[str]
    supported_events: list[str]
    constraints: dict[str, str]


class ComponentRegistry:
    def __init__(self) -> None:
        self._components = {
            "SplitComparison": ComponentDefinition(
                component="SplitComparison",
                required_roles=["product_price", "monthly_payment"],
                supported_events=[
                    "reveal_full_price",
                    "reveal_monthly_payment",
                    "attention_shift",
                ],
                constraints={
                    "left_role": "product_price",
                    "right_role": "monthly_payment",
                },
            )
        }

    def has_component(self, component: str) -> bool:
        return component in self._components

    def get_component(self, component: str) -> ComponentDefinition:
        return self._components[component]

    def available_components(self) -> set[str]:
        return set(self._components)
