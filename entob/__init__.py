import os
from abc import ABC
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
)

from entob.provider import BaseProvider
from entob.util import isinstance_with_generic


class ValueObject(ABC):
    _modified: Set[str]

    def __init__(
        self, data: Union[None, Dict[str, Any], "ValueObject"] = None, **kwargs
    ):
        self._modified = set()

        data = data or {}
        data = data.to_dict() if isinstance(data, ValueObject) else data
        data.update(kwargs)

        env_vars = self.env_vars()
        for env_var in env_vars.values():
            env_var.set_env_var(self)

        for field in self.fields():
            if field in env_vars and field not in data:
                continue
            value = data.get(field, None)
            setattr(self, field, value)

        for dependency in self.dependencies().values():
            dependency.inject(self)

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

    @classmethod
    def env_vars(cls) -> dict[str, "Env"]:
        return {
            field: value
            for field, value in cls.__dict__.items()
            if isinstance(value, Env)
        }

    @classmethod
    def dependencies(cls) -> dict[str, "Dependency"]:
        return {
            field: value
            for field, value in cls.__dict__.items()
            if isinstance(value, Dependency)
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


T = TypeVar("T")


class Describe(Generic[T]):
    types: Tuple[Type[T], ...]
    default: Union[None, T, Callable[..., T]] = None
    nullable: bool = False
    enums: Union[None, List, Tuple, Set] = None
    validate: Optional[Callable[..., bool]] = None
    coerce: Optional[Callable[..., T]] = None
    readonly: bool = False

    def __init__(
        self,
        *,
        types: Union[Type[T], Tuple[Type[T], ...]],
        default: Union[None, T, Callable[..., T]] = None,
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
            and not isinstance_with_generic(default, self.types)
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

    def __set__(self, instance: ValueObject, value: T):
        class_name = instance.__class__.__name__

        if value is None and self.default is not None:
            value = self.default() if callable(self.default) else self.default
            if not isinstance_with_generic(value, self.types):
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

        if not isinstance_with_generic(value, self.types):
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

    def __get__(self, instance: ValueObject | None, owner) -> T:
        if instance is None:
            return self  # type: ignore

        if self.name not in instance.__dict__:
            raise AttributeError(
                f"Attribute {self.__class__.__name__}.{self.name} is required"
            )

        return instance.__dict__[self.name]


class Env(Describe[T]):
    env_var: str

    def __init__(
        self,
        env_var: str,
        *,
        types: type[T] | Tuple[type[T], ...] = str,  # type: ignore
        default: None | T | Callable[[], T] = None,
        nullable: bool = False,
        enums: None | List | Tuple | Set = None,
        validate: Callable[[T], bool] | None = None,
        coerce: Callable[[Any], T] | None = None,
        readonly: bool = False,
    ):
        self.env_var = env_var
        super().__init__(
            types=types,
            default=default,
            nullable=nullable,
            enums=enums,
            validate=validate,
            coerce=coerce,
            readonly=readonly,
        )

    def set_env_var(self, instance: ValueObject):
        value = os.environ.get(self.env_var)
        setattr(instance, self.name, value)


class Dependency(Generic[T]):
    provider: BaseProvider[T]

    def __init__(self, provider: BaseProvider[T]):
        self.provider = provider

    def __set_name__(self, owner, name):
        self.name = name

    def inject(self, instance: ValueObject):
        setattr(instance, self.name, self.provider.provide())

    def __get__(self, instance: ValueObject | None, owner) -> T:
        if instance is None:
            return self  # type: ignore

        if self.name not in instance.__dict__:
            raise AttributeError(
                f"Dependency {self.__class__.__name__}.{self.name} is required"
            )

        return instance.__dict__[self.name]


__version__ = "0.1.0"
__all__ = ["ValueObject", "Describe"]
