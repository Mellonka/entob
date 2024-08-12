from abc import ABC, abstractmethod
from typing import Any, Callable, Generic, TypeVar

T = TypeVar("T")

Args = tuple[Any, ...]
Kwargs = dict[str, Any]
ProvidingFunc = Callable[..., T]


class BaseProvider(Generic[T], ABC):
    providing_func: ProvidingFunc[T]
    args: Args
    kwargs: Kwargs

    def __init__(self, providing_func: ProvidingFunc[T], *args, **kwargs):
        self.providing_func = providing_func
        self.args = args
        self.kwargs = kwargs

    def collect_params(self) -> tuple[Args, Kwargs]:
        args = []
        for arg in self.args:
            if isinstance(arg, BaseProvider):
                arg = arg.provide()
            args.append(arg)

        kwargs = {}
        for name, value in self.kwargs.items():
            if isinstance(value, BaseProvider):
                value = value.provide()
            kwargs[name] = value

        return tuple(args), kwargs

    @abstractmethod
    def provide(self):
        raise NotImplementedError


class Singleton(BaseProvider[T]):
    _obj: T

    def provide(self) -> T:
        if "_obj" not in self.__dict__:
            args, kwargs = self.collect_params()
            self._obj = self.providing_func(*args, **kwargs)

        return self._obj


class Factory(BaseProvider[T]):
    def provide(self) -> T:
        args, kwargs = self.collect_params()
        return self.providing_func(*args, **kwargs)


class Class(BaseProvider[type[T]]):
    def __init__(self, cls: type[T]):
        super().__init__(lambda: cls)

    def provide(self) -> type[T]:
        return self.providing_func()
