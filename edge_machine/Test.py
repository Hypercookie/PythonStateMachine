import asyncio
from typing import Tuple, Any

from edge_machine.EdgeMachine import EdgeMachine


async def c(n1: Tuple[Any, ...], n2: Tuple[Any, ...]) -> bool:
    print(str(n1) + " -> " + str(n2))
    return True


def t(n1: Tuple[Any, ...], n2: Tuple[Any, ...]) -> bool:
    print("Special")
    return True


async def main():
    q = EdgeMachine(2, ("Karl", "Otto"))
    await q.add_side_effect(("Karl", "Otto"), (".*", "Karl"), c)
    await q.add_global_side_effect(t)
    await q.change_state(("Otto", "Karl"))
    await q.change_state(("Karl", "Karl"))
    await q.change_state(("Karl", "Otto"))


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
