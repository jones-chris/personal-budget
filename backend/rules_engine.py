import logging
from typing import List, Dict, Callable

from config import Rule
from models import Transaction

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


class RulesEngine:

    """
    Given a list of rules and a transactions, this method updates the transaction category_id if it matches
    a rule.  This function stops when it finds the first rule that matches the transaction.  If no rules match, then
    the transaction category_id is not changed.
    """
    @staticmethod
    def apply_rules(rules: List[Rule], transaction: Transaction) -> None:
        for rule in rules:
            if RulesEngine.is_match(transaction.payee, rule):
                transaction.category_id = rule.category_id
                break  # Stop on the first matching rule.

    @staticmethod
    def is_match(payee: str, rule: Rule) -> bool:
        matching_functions: Dict[Rule.MatchingOperator, Callable[[str], bool]] = {
            Rule.MatchingOperator.IS:
                lambda s: s == rule.matching_text,
            Rule.MatchingOperator.IS_NOT:
                lambda s: s != rule.matching_text,
            Rule.MatchingOperator.CONTAINS:
                lambda s: s.__contains__(rule.matching_text),
            Rule.MatchingOperator.STARTS_WITH:
                lambda s: s.startswith(rule.matching_text),
            Rule.MatchingOperator.ENDS_WITH:
                lambda s: s.endswith(rule.matching_text)
        }

        try:
            func = matching_functions[rule.matching_operator]
        except KeyError as e:
            logger.error(f'Did not find matching function for {rule.matching_operator}')
            raise e

        return func(payee)
