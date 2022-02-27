import re
from typing import Dict, Tuple, Any, Callable, List, Generator, overload, Coroutine


def compare_tuples(t1: Tuple[Any, ...], wild_carded_tuple: Tuple[Any, ...]) -> bool:
    if len(t1) != len(wild_carded_tuple):
        return False
    for i in range(0, len(t1)):
        if not re.match(str(wild_carded_tuple[i]), str(t1[i])):
            return False
    return True


class EdgeMachine:
    def __init__(self, vertex_size: int, init_state: Tuple[Any, ...] = ()):
        self.vertex_size: int = vertex_size
        self.linear_side_effects_dict: Dict[
            Tuple[Tuple[Any, ...], Tuple[Any, ...]],
            List[Callable[[Tuple[Any, ...], Tuple[Any, ...]], bool]],
        ] = {}
        self.async_side_effects_dict: Dict[
            Tuple[Tuple[Any, ...], Tuple[Any, ...]],
            List[
                Callable[
                    [Tuple[Any, ...], Tuple[Any, ...]],
                    Coroutine[Tuple[Any, ...], Tuple[Any, ...], bool],
                ]
            ],
        ] = {}
        self.current_state: Tuple[Any, ...] = init_state
        self.global_effects: List[
            Callable[[Tuple[Any, ...], Tuple[Any, ...]], bool]
        ] = []

    async def add_global_side_effect(
        self, side_effect: Callable[[Tuple[Any, ...], Tuple[Any, ...]], bool]
    ):
        self.global_effects.append(side_effect)

    @overload
    async def add_side_effect(
        self, n1: Tuple[Any, ...], n2: Tuple[Any, ...], side_effect: Any
    ) -> bool:
        return False

    @overload
    async def add_side_effect(
        self,
        n1: Tuple[Any, ...],
        n2: Tuple[Any, ...],
        side_effect: Callable[[Tuple[Any, ...], Tuple[Any, ...]], bool],
    ) -> bool:
        if not (len(n1) == self.vertex_size and len(n2) == self.vertex_size):
            return False
        if not (n1, n2) in self.linear_side_effects_dict:
            self.linear_side_effects_dict[(n1, n2)] = []
        self.linear_side_effects_dict[(n1, n2)].append(side_effect)
        return True

    async def add_side_effect(
        self,
        n1: Tuple[Any, ...],
        n2: Tuple[Any, ...],
        side_effect: Callable[
            [Tuple[Any, ...], Tuple[Any, ...]], Coroutine[Any, Any, bool]
        ],
    ) -> bool:
        if not (len(n1) == self.vertex_size and len(n2) == self.vertex_size):
            return False
        if not (n1, n2) in self.async_side_effects_dict:
            self.async_side_effects_dict[(n1, n2)] = []
        self.async_side_effects_dict[(n1, n2)].append(side_effect)

    async def get_linear_side_effects_from_effects_list(
        self, n1: Tuple[Any, ...], n2: Tuple[Any, ...]
    ) -> Generator[Callable[[Tuple[Any, ...], Tuple[Any, ...]], bool], None, None]:
        for i in self.linear_side_effects_dict:
            if compare_tuples(n1, i[0]) and compare_tuples(n2, i[1]):
                for v in self.linear_side_effects_dict[i]:
                    yield v

    async def get_async_side_effects_from_effects_list(
        self, n1: Tuple[Any, ...], n2: Tuple[Any, ...]
    ) -> Generator[
        Callable[[Tuple[Any, ...], Tuple[Any, ...]], Coroutine[Any, Any, bool]],
        None,
        None,
    ]:
        for i in self.async_side_effects_dict:
            if compare_tuples(n1, i[0]) and compare_tuples(n2, i[1]):
                for v in self.async_side_effects_dict[i]:
                    yield v

    async def change_state(self, new_state: Tuple[Any, ...]) -> bool:
        if len(new_state) != self.vertex_size:
            return False
        async for i in self.get_linear_side_effects_from_effects_list(
            self.current_state, new_state
        ):
            i(self.current_state, new_state)

        async for i in self.get_async_side_effects_from_effects_list(
            self.current_state, new_state
        ):
            await i(self.current_state, new_state)
        for i in self.global_effects:
            i(self.current_state, new_state)
