"""Habot Connect FZCO - Hiring Project.

Position: Junior Cloud and Development Operations Engineer.
Candidate Full Name: Anuradha.
Candidate Electronic Mail Address: anuradha@tecofize.com.

File purpose: the evaluator of the deconstructed yes or no validation library.

Poka-Yoke rationale for this file
---------------------------------
The evaluator has exactly one decision rule, and it is stated in one line of
code: a submission is accepted when every rule answered yes, and is refused
otherwise. There is no weighting, no threshold and no override, because each of
those is a place where a person could be asked to decide, and a place where a
person can be asked to decide is a place where two people will decide
differently.

The evaluator runs every rule even after the first no. Stopping at the first
failure would give the parent or guardian one correction at a time, which turns
a single form into several rounds of resubmission, and would give an auditor an
incomplete record of why a submission was refused.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

from .rules import DeconstructedYesNoRule, RuleAnswer, build_complete_rule_set


@dataclass(frozen=True)
class DeconstructedYesNoEvaluation:
    """The complete result of evaluating one submission."""

    rule_answers: Tuple[RuleAnswer, ...]
    evaluated_at_instant: datetime

    @property
    def outcome_is_accepted(self) -> bool:
        """Return whether every rule answered yes.

        This is the whole decision. An empty rule set would make this property
        return yes vacuously, so the evaluator refuses to run with an empty rule
        set rather than relying on this property to notice.
        """
        return all(answer.rule_answer_is_yes for answer in self.rule_answers)

    @property
    def refusing_rule_identifiers(self) -> Tuple[str, ...]:
        """Return the identifier of every rule that answered no."""
        return tuple(
            answer.rule_identifier
            for answer in self.rule_answers
            if not answer.rule_answer_is_yes
        )

    @property
    def refusal_reasons(self) -> Tuple[str, ...]:
        """Return the question of every rule that answered no."""
        return tuple(
            answer.rule_question
            for answer in self.rule_answers
            if not answer.rule_answer_is_yes
        )

    def as_warehouse_records(self) -> List[Dict[str, Any]]:
        """Return every answer in the shape of the warehouse repeated record."""
        return [answer.as_warehouse_record() for answer in self.rule_answers]


class DeconstructedYesNoEvaluator:
    """Evaluates a student onboarding payload against the complete rule set."""

    def __init__(self, rules: List[DeconstructedYesNoRule] = None) -> None:
        """Construct the evaluator, refusing an empty rule set."""
        self._rules = build_complete_rule_set() if rules is None else list(rules)

        if len(self._rules) == 0:
            raise ValueError(
                "The evaluator was constructed with an empty rule set. An "
                "empty rule set would accept every submission, so construction "
                "is refused rather than producing a validator that validates "
                "nothing."
            )

    @property
    def rule_count(self) -> int:
        """Return the number of rules that this evaluator applies."""
        return len(self._rules)

    @property
    def rule_identifiers(self) -> Tuple[str, ...]:
        """Return the identifier of every rule, in evaluation order."""
        return tuple(rule.rule_identifier for rule in self._rules)

    def evaluate(
        self,
        payload: Dict[str, Any],
        evaluation_instant: datetime = None,
    ) -> DeconstructedYesNoEvaluation:
        """Answer every rule for one payload and return the complete result."""
        resolved_instant = (
            datetime.now(timezone.utc)
            if evaluation_instant is None
            else evaluation_instant.astimezone(timezone.utc)
        )

        if not isinstance(payload, dict):
            # A payload that is not an object cannot be evaluated field by
            # field. Rather than raising, which an upstream handler might catch
            # and treat as a pass, the evaluator returns a result in which the
            # structural rule has answered no.
            payload = {}

        answers = tuple(rule.answer(payload, resolved_instant) for rule in self._rules)

        return DeconstructedYesNoEvaluation(
            rule_answers=answers,
            evaluated_at_instant=resolved_instant,
        )


def evaluate_student_onboarding_payload(
    payload: Dict[str, Any],
    evaluation_instant: datetime = None,
) -> DeconstructedYesNoEvaluation:
    """Evaluate one payload using the complete rule set.

    This is the function that the transformation stage calls. It exists so that
    the calling code never constructs its own evaluator with its own rule set,
    which would be a route around the library.
    """
    return DeconstructedYesNoEvaluator().evaluate(payload, evaluation_instant)
