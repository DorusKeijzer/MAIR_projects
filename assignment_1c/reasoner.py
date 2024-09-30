from typing import List, Dict


class Literal:
    def __init__(self, name: str, truth_value):
        self.name = name
        self.truth_value = truth_value

    def __eq__(self, other):
        return self.name == other.name and self.truth_value == other.truth_value

    def __repr__(self):
        return f"{self.name} = {self.truth_value}"


class Rule:
    """Rules are in conjunctive normal form: (p ∧ ... ∧ q -> c)"""

    def __init__(self, antecedents: Dict[str, any], consequent: str, consequent_value, explanation: str):
        self.antecedents = antecedents  # Dict of property names and their expected values
        self.consequent = consequent
        self.consequent_value = consequent_value
        self.explanation = explanation  # Explanation string


class InferenceEngine:
    def __init__(self, rules: List[Rule]):
        self.rules = rules

    def inference(self, knowledge: List[Literal]) -> (Dict[str, any], Dict[str, str]):
        inferred = {}
        explanations = {}
        known = {lit.name: lit.truth_value for lit in knowledge}
        contradictions = {}

        while True:
            new_inference = False
            for r in self.rules:
                # Check if all antecedents are satisfied
                antecedents_satisfied = all(
                    known.get(ant) == val for ant, val in r.antecedents.items()
                )
                if antecedents_satisfied:
                    if r.consequent not in known:
                        # Infer the consequent
                        known[r.consequent] = r.consequent_value
                        inferred[r.consequent] = r.consequent_value
                        # Record explanation
                        explanations[r.consequent] = r.explanation
                        new_inference = True
                    else:
                        # Check for contradiction
                        if known[r.consequent] != r.consequent_value and known[r.consequent] != 'contradictory':
                            known[r.consequent] = 'contradictory'
                            inferred[r.consequent] = 'contradictory'
                            explanations[r.consequent] = f"Contradiction detected for {
                                r.consequent}"
                            contradictions[r.consequent] = True
                            new_inference = True
            if not new_inference:
                break
        return inferred, explanations


# Inference rules
rules = [
    Rule(
        {'pricerange': 'cheap', 'food_quality': 'good'},
        'touristic',
        True,
        "Cheap price and good food make it appealing to tourists."
    ),
    Rule(
        {'food': 'romanian'},
        'touristic',
        False,
        "Romanian food is not commonly sought by tourists."
    ),
    Rule(
        {'crowdedness': 'busy'},
        'assigned_seats',
        True,
        "Busy restaurants need assigned seats to manage guests."
    ),
    Rule(
        {'length_of_stay': 'long'},
        'children',
        False,
        "Long stays are not suitable for children."
    ),
    Rule(
        {'crowdedness': 'busy'},
        'romantic',
        False,
        "Busy environments are not conducive to romance."
    ),
    Rule(
        {'length_of_stay': 'long'},
        'romantic',
        True,
        "Long stays are ideal for romantic experiences."
    ),
]
