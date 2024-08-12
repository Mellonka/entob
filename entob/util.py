from types import UnionType
from typing import Callable, Tuple, Type, TypeVar, Union, get_args, get_origin

T = TypeVar("T")


def validate_collection(validate: Callable[[T], bool]):
    return lambda collection: not any(not validate(e) for e in collection)


def coerce_list(
    coerce: Callable[..., T],
):
    return lambda collection: list(coerce(e) for e in collection)


def isinstance_with_generic(
    value: T,
    types: Union[Type[T], Tuple[Type[T], ...]],
) -> bool:
    if isinstance(types, tuple):
        return any(isinstance_with_generic(value, type_) for type_ in types)

    base_generic = get_origin(types)

    if base_generic is None:
        return isinstance(value, types)

    args = get_args(types)

    if base_generic in (UnionType, Union):
        return any(isinstance_with_generic(value, type_) for type_ in args)

    if base_generic in (list, set):
        return type(value) is base_generic and all(
            isinstance_with_generic(item, args)
            for item in value  # type: ignore
        )

    if base_generic is tuple:
        return (
            type(value) is tuple
            and len(value) == len(args)
            and all(
                isinstance_with_generic(item, arg) for item, arg in zip(value, args)
            )
        )

    raise NotImplementedError(f"Unknown types: {types}")
