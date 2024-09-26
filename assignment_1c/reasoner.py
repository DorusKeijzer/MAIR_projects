from typing import List, Dict


class literal:
    def __init__(self, name: str, truth_value):
        self.name = name
        self.truth_value = truth_value

    def __eq__(self, other):
        return self.name == other.name


class rule:
    """Rules are assumed to be in conjunctive normal form: (p ∧ ... ∧ q -> c)"""

    def __init__(self, antecedents: Dict[str, bool], consequent: str):
        self.antecedents = antecedents
        self.consequent = consequent


class inference_engine:
    def __init__(self, rules: List[rule]):
        self.rules = rules

    def inference(self, knowledge: List[literal]) -> List[str]:
        inferred = []
        known = {lit.name: lit.truth_value for lit in knowledge}

        new_inference = True
        while new_inference:
            new_inference = False
            for r in self.rules:
                if r.consequent not in known:
                    # Check if all antecedents are satisfied
                    if all(known.get(ant, False) == val for ant, val in r.antecedents.items()):
                        # Infer the consequent
                        known[r.consequent] = True
                        inferred.append(r.consequent)
                        new_inference = True

        return inferred


if __name__ == "__main__":
    # example
    literals = [
        literal("A", True),
        literal("B", True),
        literal("C", False)
    ]

    rules = [
        rule({"A": True, "B": True}, "D"),
        rule({"D": True, "C": False}, "E"),
        rule({"E": True}, "F")
    ]

    engine = inference_engine(rules)

    inferred_facts = engine.inference(literals)

    print("Inferred facts:", inferred_facts)
