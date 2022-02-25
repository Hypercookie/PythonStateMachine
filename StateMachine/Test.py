from StateMachine import AbstractStateMachine
from Node import Node


def c(n1: Node, n2: Node) -> bool:
    print("%s -> %s" % (n1.state_list, n2.state_list))
    return True


def special(n1: Node, n2: Node) -> bool:
    print("Special")
    return True


k = AbstractFiniteStateMachine(2, ["Hello", True, False, "Bye"], False)
k.attach_global_side_effect(c)
k.attach_side_effect(("Hello", True), ("Bye", False), special)
k.update_states(("Hello", True))
k.update_states(("Bye", False))
