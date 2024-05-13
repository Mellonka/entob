from abc import ABC
from copy import deepcopy
from enum import Enum
from types import UnionType
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    get_args,
    get_origin,
)


def _isinstance_with_generic(value: Any, types: Union[Type, tuple[Type, ...]]) -> bool:
    if isinstance(types, tuple):
        return any(_isinstance_with_generic(value, type_) for type_ in types)

    base_generic = get_origin(types)

    if base_generic is None:
        return isinstance(value, types)

    if base_generic in [UnionType, Union]:
        return any(_isinstance_with_generic(value, type_) for type_ in get_args(types))

    args = get_args(types)
    if base_generic in (list, set):
        return type(value) == base_generic and all(
            _isinstance_with_generic(item, args) for item in value
        )

    if base_generic == tuple:
        return (
            type(value) == tuple
            and len(value) == len(args)
            and all(
                _isinstance_with_generic(item, arg) for item, arg in zip(value, args)
            )
        )

    raise NotImplementedError(f"Unknown types: {types}")


class MageClass(ABC):
    def __init__(self, row: Union[None, Dict[str, Any], "MageClass"] = None, **kwargs):
        row = row or {}
        if isinstance(row, MageClass):
            row = deepcopy(row.dump())
        row |= kwargs

        for attr_name, attr in self._get_mageattrs().items():
            if attr_name in row:
                setattr(self, attr_name, row[attr_name])
            else:
                attr._init_instance__(self)

    def __getattribute__(self, name: str):
        attr = super().__getattribute__(name)
        if isinstance(attr, Attribute):
            return getattr(self, attr._name)
        return attr

    @classmethod
    def _get_mageattrs(cls) -> Dict[str, "Attribute"]:
        if cls == MageClass or not issubclass(cls, MageClass):
            return {}

        return cls.__base__._get_mageattrs() | {  # type: ignore
            attr_name: attr
            for attr_name, attr in vars(cls).items()
            if isinstance(attr, Attribute)
        }

    def dump(self) -> Dict[str, Any]:
        return {
            attr_name: attr.dump(self) if attr._dump else getattr(self, attr._name)
            for attr_name, attr in self._get_mageattrs().items()
        }


class Attribute:
    def __init__(
        self,
        *,
        types: Union[type, Tuple[type, ...]],
        default: Optional[Callable] = None,
        required: bool = False,
        enums: Union[None, List, Tuple, Enum] = None,
        validate: Optional[Callable[..., bool]] = None,
        cooking: Optional[Callable] = None,
        serialize: Optional[Callable[..., str]] = None,
    ):
        if not isinstance(types, (tuple, list)):
            types = (types,)
        self.types = tuple(types)

        if (
            default is not None
            and not _isinstance_with_generic(default, self.types)
            and not callable(default)
        ):
            raise TypeError(f"default value must be of type {self.types} or callable")
        self.default = default
        self.required = required

        if enums is not None and not isinstance(enums, (tuple, list, Enum)):
            raise TypeError("enums must be a list, tuple or Enum")
        if enums is not None and isinstance(enums, Enum):
            enums = [e.value for e in enums]  # type: ignore
        self.enums = enums

        if validate is not None and not isinstance(validate, Callable):
            raise TypeError("validate must be a callable")
        self.validate = validate

        if cooking is not None and not isinstance(cooking, Callable):
            raise TypeError("cooking must be a callable")
        self.cooking = cooking

        if serialize is not None and not isinstance(serialize, Callable):
            raise TypeError("serialize must be a callable")
        self._dump = serialize

    def __set_name__(self, owner, name):
        self._attr_name = name
        self._name = f"_{name}_value"

    def __set__(self, instance, value):
        if self.cooking and value is not None:
            value = self.cooking(value)

        if self.required and value is None:
            raise ValueError(
                f"{instance.__class__.__name__}: Value for attribute {self._attr_name} is required"
            )

        if value is None:
            setattr(instance, self._name, value)
            return

        if not _isinstance_with_generic(value, self.types):
            raise TypeError(
                f"{instance.__class__.__name__}: Value for attribute {self._attr_name} must be one of {self.types}"
            )

        if self.enums is not None and value not in self.enums:
            raise ValueError(
                f"{instance.__class__.__name__}: Value for attribute {self._attr_name} must be one of {self.enums}"
            )

        if self.validate and not self.validate(value):
            raise ValueError(
                f"{instance.__class__.__name__}: Value for attribute {self._attr_name} is invalid"
            )

        setattr(instance, self._name, value)

    def dump(self, instance):
        if self._dump:
            return self._dump(getattr(instance, self._name))
        return getattr(instance, self._name)

    def _init_instance__(self, instance):
        value = self.default() if callable(self.default) else self.default
        self.__set__(instance, value)


_AttrType = TypeVar("_AttrType")


def attribute(
    types: Union[Type[_AttrType], Tuple[Type[_AttrType], ...]],
    default: Optional[Callable[..., _AttrType]] = None,
    required: bool = False,
    enums: Union[None, List, Tuple, Enum] = None,
    validate: Optional[Callable[..., bool]] = None,
    cooking: Optional[Callable] = None,
    serialize: Optional[Callable[..., str]] = None,
) -> _AttrType:
    return Attribute(
        types=types,
        default=default,
        required=required,
        enums=enums,
        validate=validate,
        cooking=cooking,
        serialize=serialize,
    )  # type: ignore


__version__ = "0.0.1"
__all__ = ["MageClass", "Attribute", "attribute"]
