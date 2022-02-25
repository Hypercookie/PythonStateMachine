from Node import Node
from statypy.StateMachine import StateMachine


def c(n1: Node, n2: Node) -> bool:
    print("%s -> %s" % (n1.state_list, n2.state_list))
    return True


def julia_got_home(n1: Node, n2: Node) -> bool:
    print("Julia got home")
    return True


def julia_came_home_and_is_alone(n1: Node, n2: Node) -> bool:
    print("Julia is home alone")
    return True


def jannes_got_home(n1: Node, n2: Node) -> bool:
    print("Jannes got home")
    return True


def jannes_came_home_and_is_alone(n1: Node, n2: Node) -> bool:
    print("Jannes is home alone")
    return True


k = StateMachine(2, ["julia_home", "jannes_home", "julia_away", "jannes_away"], False,
                 init_state=("julia_away", "jannes_away"))
k.attach_global_side_effect(c)
k.attach_side_effect(("!julia_home", "*"), ("julia_home", "*"), julia_got_home)
k.attach_side_effect(("!julia_home", "*"), ("julia_home", "!jannes_home"), julia_came_home_and_is_alone)
k.attach_side_effect(("*", "!jannes_home"), ("*", "jannes_home"), jannes_got_home)
k.attach_side_effect(("*", "!jannes_home"), ("!julia_home", "jannes_home"), jannes_came_home_and_is_alone)

k.update_states(("julia_home", "jannes_away"))
k.update_states(("julia_away", "jannes_away"))
k.update_states(("julia_home", "jannes_home"))
k.update_states(("julia_home", "jannes_home"))
