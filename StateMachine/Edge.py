from functools import reduce
from typing import Callable

import Node


class Edge:
    def __init__(self, n1: Node, n2: Node, transition_functions=None):
        if transition_functions is None:
            transition_functions = []
        self.n1: Node = n1
        self.n2: Node = n2
        self.transition_functions: list[
            Callable[[Node, Node], bool]
        ] = transition_functions
        self.n1.add_outgoing(self)

    def transition(self) -> bool:
        return reduce(
            lambda a, b: a and b,
            [f(self.n1, self.n2) for f in self.transition_functions],
        )
