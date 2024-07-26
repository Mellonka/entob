from copy import deepcopy

import pytest

from entob import Describe, ValueObject


def test_required():
    class Person(ValueObject):
        first_name = Describe(types=str)
        second_name = Describe(types=str)
        middle_name = Describe(types=str, nullable=True)

    persons_without_middle_name = [
        Person(first_name="Tom", second_name="Smith"),
        Person(
            {
                "first_name": "Tom",
                "second_name": "Smith",
            }
        ),
    ]
    persons_without_middle_name.append(deepcopy(persons_without_middle_name[0]))

    persons_with_middle_name = [
        Person(first_name="Tom", second_name="Smith", middle_name="Jerry"),
        Person(
            {
                "first_name": "Tom",
                "second_name": "Smith",
                "middle_name": "Jerry",
            }
        ),
        Person(
            {
                "first_name": "Tom",
                "second_name": "Smith",
            },
            middle_name="Jerry",
        ),
    ]

    all_persons = persons_without_middle_name + persons_with_middle_name
    assert all(person.first_name == "Tom" for person in all_persons)
    assert all(person.second_name == "Smith" for person in all_persons)
    assert all(person.middle_name is None for person in persons_without_middle_name)
    assert all(person.middle_name == "Jerry" for person in persons_with_middle_name)

    with pytest.raises(ValueError):
        Person(first_name="Tom")
    with pytest.raises(ValueError):
        Person(second_name="Tom")
    with pytest.raises(ValueError):
        Person(first_name="Tom", middle_name="Jerry")
    with pytest.raises(ValueError):
        Person({"first_name": "Tom", "middle_name": "Jerry"})
    with pytest.raises(ValueError):
        Person({})
    with pytest.raises(ValueError):
        Person()


def test_readonly():
    class Person(ValueObject):
        first_name = Describe(types=str)
        last_name = Describe(types=str, readonly=True)

    person = Person(first_name="Tom", last_name="Jerry")
    person.first_name = "Spike"

    with pytest.raises(AttributeError):
        person.last_name = "John"


def test_types():
    class Person(ValueObject):
        age = Describe(types=int)

    with pytest.raises(TypeError):
        Person(age="Tom")

    with pytest.raises(TypeError):
        Person(age=1.0)

    with pytest.raises(TypeError):
        Person(age=[])


def test_nullable():
    class Person(ValueObject):
        age = Describe(types=int)

    with pytest.raises(ValueError):
        Person(age=None)
    with pytest.raises(ValueError):
        Person()
    with pytest.raises(ValueError):
        Person({"age": None})
