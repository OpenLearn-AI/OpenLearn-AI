"""Eval evaluators for the OpenLearn AI eval harness.

Each evaluator subclasses ``BaseEvaluator`` and is registered in ``REGISTRY``
so the CLI (``python -m app.eval``) can look it up by name.
"""

from __future__ import annotations

import abc


class BaseEvaluator(abc.ABC):
    """Abstract base class that every evaluator must implement."""

    @abc.abstractmethod
    def evaluate(self, entry: dict) -> bool:
        """Evaluate a single dataset entry.

        Args:
            entry: A dict loaded from the JSON dataset.

        Returns:
            ``True`` if the entry passes evaluation, ``False`` otherwise.

        Raises:
            Any exception is treated as a failure by the harness.
        """


class DummyEvaluator(BaseEvaluator):
    """Validates that each dataset entry has the expected schema.

    Passes when the entry contains non-empty ``question`` and
    ``expected_answer`` string fields.  This evaluator is intentionally
    simple — it proves the harness works end-to-end without requiring
    an LLM call.
    """

    def evaluate(self, entry: dict) -> bool:
        question = entry.get("question")
        expected_answer = entry.get("expected_answer")

        if not isinstance(question, str) or not question.strip():
            return False
        if not isinstance(expected_answer, str) or not expected_answer.strip():
            return False

        return True


# ---------------------------------------------------------------------------
# Evaluator registry — maps CLI name → evaluator class.
# To add a new evaluator, subclass BaseEvaluator and add it here.
# ---------------------------------------------------------------------------
REGISTRY: dict[str, type[BaseEvaluator]] = {
    "dummy": DummyEvaluator,
}
