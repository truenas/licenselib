__all__ = ('proactive_support_allowed')

from license import ContractType


def proactive_support_allowed(ctype: str) -> bool:
    """Check if `ctype` is entitled to proactive support."""
    return ctype.lower() in (
        ContractType.gold.name,
        ContractType.silver.name,
        ContractType.silverinternational.name,
    )
