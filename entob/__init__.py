from abc import ABC
from types import UnionType
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    List,
    Optional,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
    get_args,
    get_origin,
)


class ValueObject(ABC):
    _modified: Set[str]

    def __init__(
        self, data: Union[None, Dict[str, Any], "ValueObject"] = None, **kwargs
    ):
        self._modified = set()

        data = data or {}
        data = data.to_dict() if isinstance(data, ValueObject) else data
        data.update(kwargs)

        for field in self.fields():
            value = data.get(field, None)
            setattr(self, field, value)

        self._modified.clear()

    def is_modified(self, field_name) -> bool:
        return field_name in self._modified

    def set_modified(self, field_name) -> None:
        self._modified.add(field_name)

    @property
    def modified_fields(self) -> Set[str]:
        return self._modified

    @classmethod
    def fields(cls) -> Set[str]:
        return {
            field
            for field, value in cls.__dict__.items()
            if isinstance(value, Describe)
        }

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            f"({', '.join(f'{field}={getattr(self, field)!r}' for field in self.fields())})"
        )

    def to_dict(self) -> Dict[str, Any]:
        return {field: getattr(self, field) for field in self.fields()}

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return False

        for field in self.fields():
            if getattr(self, field) != getattr(other, field):
                return False

        return True

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)


ValueTypes = TypeVar("ValueTypes")


def _isinstance_with_generic(
    value: ValueTypes,
    types: Union[Type[ValueTypes], Tuple[Type[ValueTypes], ...]],
) -> bool:
    if isinstance(types, tuple):
        return any(_isinstance_with_generic(value, type_) for type_ in types)

    base_generic = get_origin(types)

    if base_generic is None:
        return isinstance(value, types)

    args = get_args(types)

    if base_generic in (UnionType, Union):
        return any(_isinstance_with_generic(value, type_) for type_ in args)

    if base_generic in (list, set):
        return type(value) is base_generic and all(
            _isinstance_with_generic(item, args)
            for item in value  # type: ignore
        )

    if base_generic is tuple:
        return (
            type(value) is tuple
            and len(value) == len(args)
            and all(
                _isinstance_with_generic(item, arg) for item, arg in zip(value, args)
            )
        )

    raise NotImplementedError(f"Unknown types: {types}")


class Describe(Generic[ValueTypes]):
    types: Tuple[Type[ValueTypes], ...]
    default: Union[None, ValueTypes, Callable[..., ValueTypes]] = None
    nullable: bool = False
    enums: Union[None, List, Tuple, Set] = None
    validate: Optional[Callable[..., bool]] = None
    coerce: Optional[Callable[..., ValueTypes]] = None
    readonly: bool = False

    def __init__(
        self,
        *,
        types: Union[Type[ValueTypes], Tuple[Type[ValueTypes], ...]],
        default: Union[None, ValueTypes, Callable[..., ValueTypes]] = None,
        nullable: bool = False,
        enums: Union[None, List, Tuple, Set] = None,
        validate: Optional[Callable[..., bool]] = None,
        coerce: Optional[Callable] = None,
        readonly: bool = False,
    ):
        if not isinstance(types, (tuple, list)):
            types = (types,)
        self.types = tuple(types)

        if (
            default is not None
            and not callable(default)
            and not _isinstance_with_generic(default, self.types)
        ):
            raise TypeError(f"default value must be of type {self.types} or callable")

        self.default = default
        self.nullable = nullable
        self.readonly = readonly

        if enums is not None and not isinstance(enums, (tuple, list)):
            raise TypeError("enums must be a list, tuple or Enum")

        self.enums = set(enums) if enums else None

        if validate is not None and not callable(validate):
            raise TypeError("validate must be a callable")

        self.validate = validate

        if coerce is not None and not callable(coerce):
            raise TypeError("cooking must be a callable")

        self.coerce = coerce

    def __set_name__(self, owner, name):
        self.name = name

    def __set__(self, instance: ValueObject, value: ValueTypes):
        class_name = instance.__class__.__name__

        if value is None and self.default is not None:
            value = self.default() if callable(self.default) else self.default
            if not _isinstance_with_generic(value, self.types):
                raise TypeError(
                    f"Default value for attribute {class_name}.{self.name} must be one of {self.types}"
                )

        value = self.coerce(value) if self.coerce else value

        if not self.nullable and value is None:
            raise ValueError(
                f"Value for attribute {class_name}.{self.name} is required"
            )

        if self.name in instance.__dict__ and self.readonly:
            raise AttributeError(f"Attribute {class_name}.{self.name} is readonly")

        if value is None:
            instance.set_modified(self.name)
            instance.__dict__[self.name] = value
            return

        if not _isinstance_with_generic(value, self.types):
            raise TypeError(
                f"Value for attribute {class_name}.{self.name} must be one of {self.types}"
            )

        if self.enums is not None and value not in self.enums:
            raise ValueError(
                f"Value for attribute {class_name}.{self.name} must be one of {self.enums}"
            )

        if self.validate and not self.validate(value):
            raise ValueError(f"Value for attribute {class_name}.{self.name} is invalid")

        instance.set_modified(self.name)
        instance.__dict__[self.name] = value

    def __get__(self, instance: ValueObject | None, owner) -> ValueTypes:
        if instance is None:
            return self  # type: ignore

        if self.name not in instance.__dict__:
            raise AttributeError(
                f"Attribute {self.__class__.__name__}.{self.name} is required"
            )

        return instance.__dict__[self.name]


__version__ = "0.1.0"
__all__ = ["ValueObject", "Describe"]
