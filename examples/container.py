from entob import Dependency, Env, ValueObject
from entob.provider import Factory, Singleton


class PostgresConfig(ValueObject):
    user = Env("POSTGRES_USER", default="test")
    password = Env("POSTGRES_PASSWORD", default="test")
    host = Env("POSTGRES_HOST", default="test")
    port = Env("POSTGRES_PORT", types=int, coerce=int, default=1234)
    name = Env("POSTGRES_DB", default="test")


class Engine:
    def __init__(
        self, user: str, password: str, host: str, port: int, name: str
    ) -> None:
        print("Engine создан")


class Session:
    def __init__(self, engine: Engine) -> None:
        print("Session создан")


class PostgresDependencies:
    config = PostgresConfig()
    engine = Singleton(
        Engine, config.user, config.password, config.host, config.port, config.name
    )
    session = Factory(Session, engine)


class Worker(ValueObject):
    session = Dependency(PostgresDependencies.session)


worker1 = Worker()
worker2 = Worker()
worker3 = Worker()
worker4 = Worker()

"""
Вывод пуст
"""


worker1.session
worker2.session
worker3.session
worker4.session

"""
Вывод:
Engine создан
Session создан
Session создан
Session создан
Session создан
"""
