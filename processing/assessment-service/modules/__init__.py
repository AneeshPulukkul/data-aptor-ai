"""Assessment modules for DataAptor AI."""

from .quality import assess_quality
from .accessibility import assess_accessibility
from .governance import assess_governance
from .ai_compatibility import assess_ai_compatibility
from .diversity import assess_diversity

__all__ = [
    "assess_quality",
    "assess_accessibility",
    "assess_governance",
    "assess_ai_compatibility",
    "assess_diversity"
]
