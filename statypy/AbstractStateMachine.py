from itertools import product
from typing import Callable, Any

from Edge import Edge
from Node import Node


def tuple_matches(t1: tuple, match: tuple) -> bool:
    if len(t1) != len(match):
        return False
    else:
        for i in range(0, len(t1)):
            if str(match[i])[0] == "!" and str(t1[i]) == str(match[i])[1::]:
                return False
            if not (str(t1[i]) == str(match[i]) or str(match[i]) == "*") and str(match[i])[0] != "!":
                return False

        return True


class AbstractStateMachine:
    def __init__(self, num_attr: int, allow_self_transition=False):
        self.num_attr: int = num_attr
        self.nodes: list[Node] = []
        self.edges: list[Edge] = []
        self.mapping_nodes: dict[tuple:Node] = {}
        self.current_state: tuple = ()
        self.allow_self_transition: bool = allow_self_transition
        self.compute_graph()

    def compute_graph(self) -> None:
        permutation_list: list[tuple[int]] = list(product([0, 1], repeat=self.num_attr))
        self.compute_from_permutation_list(permutation_list)

    def compute_from_permutation_list(self, permutation_list: list[tuple[Any]]):
        self.nodes: list[Node] = [Node(i) for i in permutation_list]
        self.edges: list[Edge] = [
            Edge(i, j)
            for i in self.nodes
            for j in self.nodes
            if (not i.compare(j.state_list)) or self.allow_self_transition
        ]
        self.mapping_nodes: dict[tuple:Node] = {i.state_list: i for i in self.nodes}
        self.current_state: tuple = self.nodes[0].state_list

    def attach_side_effect(
            self, t1: tuple, t2: tuple, transition_function: Callable[[Node, Node], bool]
    ) -> bool:
        if len(t1) != self.num_attr or len(t2) != self.num_attr:
            return False
        else:
            edges: list[Edge] = self.get_edges_from_wildcard(t1, t2)
            for e in edges:
                e.transition_functions.append(transition_function)
            return True

    def get_edges_from_wildcard(self, t1: tuple, t2: tuple) -> list[Edge]:
        q = []
        for edge in self.edges:
            if tuple_matches(edge.n1.state_list, t1) and tuple_matches(edge.n2.state_list, t2):
                q.append(edge)
        return q  # [i for i in self.edges if tuple_matches(i.n1.state_list, t1) and tuple_matches(i.n2.state_list, t2)]

    def attach_global_side_effect(
            self, transition_function: Callable[[Node, Node], bool]
    ) -> bool:
        for edge in self.edges:
            edge.transition_functions.append(transition_function)
        return True

    def get_edge_by_tuple_pair(self, t1: tuple, t2: tuple) -> Edge:
        if not (len(t1) != self.num_attr or len(t2) != self.num_attr):
            node: Node = self.mapping_nodes.get(t1)
            edge: Edge = node.outgoing_map.get(t2)
            return edge

    def update_states(self, new_state: tuple) -> bool:
        if len(new_state) == self.num_attr and (
                new_state != self.current_state or self.allow_self_transition
        ):
            edge: Edge = self.get_edge_by_tuple_pair(self.current_state, new_state)
            r: bool = edge.transition()
            self.current_state: tuple = new_state
            return r
        return False
