import re
from typing import (
    Dict,
    Tuple,
    Any,
    Callable,
    List,
    Generator,
    overload,
    Coroutine,
    Union,
)

VERTEX_TYPE = Tuple[Any, ...]
LINEAR_SIDE_EFFECT_TYPE = Callable[[VERTEX_TYPE, VERTEX_TYPE], bool]
ASYNC_SIDE_EFFECT_TYPE = Callable[[VERTEX_TYPE, VERTEX_TYPE], Coroutine[Any, Any, bool]]
EDGE_TYPE = Tuple[VERTEX_TYPE, VERTEX_TYPE]


def compare_tuples(t1: VERTEX_TYPE, wild_carded_tuple: VERTEX_TYPE) -> bool:
    if len(t1) != len(wild_carded_tuple):
        return False
    for i in range(0, len(t1)):
        if not re.match(str(wild_carded_tuple[i]), str(t1[i])):
            return False
    return True


class EdgeMachine:
    def __init__(self, vertex_size: int, init_state: VERTEX_TYPE = ()):
        self.vertex_size: int = vertex_size
        self.linear_side_effects_dict: Dict[
            EDGE_TYPE, List[LINEAR_SIDE_EFFECT_TYPE]
        ] = {}
        self.async_side_effects_dict: Dict[EDGE_TYPE, List[ASYNC_SIDE_EFFECT_TYPE]] = {}
        self.current_state: VERTEX_TYPE = init_state
        self.global_effects: List[LINEAR_SIDE_EFFECT_TYPE] = []
        self.async_global_side_effects: List[ASYNC_SIDE_EFFECT_TYPE] = []

    async def add_global_side_effect(self, side_effect: LINEAR_SIDE_EFFECT_TYPE):
        self.global_effects.append(side_effect)

    async def add_global_async_side_effect(self, side_effect: ASYNC_SIDE_EFFECT_TYPE):
        self.async_global_side_effects.append(side_effect)

    async def add_side_effect_to_dict(
        self,
        n1: VERTEX_TYPE,
        n2: VERTEX_TYPE,
        side_effect: Union[ASYNC_SIDE_EFFECT_TYPE, LINEAR_SIDE_EFFECT_TYPE],
        d: dict[
            EDGE_TYPE : List[Union[ASYNC_SIDE_EFFECT_TYPE, LINEAR_SIDE_EFFECT_TYPE]]
        ],
    ) -> bool:
        if not (len(n1) == self.vertex_size and len(n2) == self.vertex_size):
            return False
        if not (n1, n2) in d:
            d[(n1, n2)] = []
        d[(n1, n2)].append(side_effect)
        return True

    async def add_side_effect(
        self, n1: VERTEX_TYPE, n2: VERTEX_TYPE, side_effect: LINEAR_SIDE_EFFECT_TYPE,
    ) -> bool:
        return await self.add_side_effect_to_dict(
            n1, n2, side_effect, self.linear_side_effects_dict
        )

    async def add_async_side_effect(
        self, n1: VERTEX_TYPE, n2: VERTEX_TYPE, side_effect: ASYNC_SIDE_EFFECT_TYPE,
    ) -> bool:
        return await self.add_side_effect_to_dict(
            n1, n2, side_effect, self.async_side_effects_dict
        )

    async def get_linear_side_effects_from_effects_list(
        self, n1: VERTEX_TYPE, n2: VERTEX_TYPE
    ) -> Generator[LINEAR_SIDE_EFFECT_TYPE, None, None]:
        for i in self.linear_side_effects_dict:
            if compare_tuples(n1, i[0]) and compare_tuples(n2, i[1]):
                for v in self.linear_side_effects_dict[i]:
                    yield v

    async def get_async_side_effects_from_effects_list(
        self, n1: VERTEX_TYPE, n2: VERTEX_TYPE
    ) -> Generator[
        ASYNC_SIDE_EFFECT_TYPE, None, None,
    ]:
        for i in self.async_side_effects_dict:
            if compare_tuples(n1, i[0]) and compare_tuples(n2, i[1]):
                for v in self.async_side_effects_dict[i]:
                    yield v

    async def change_state(self, new_state: VERTEX_TYPE) -> bool:
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
        for i in self.async_global_side_effects:
            await i(self.current_state, new_state)
