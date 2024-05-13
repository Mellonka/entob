import pytest

from mageclass import MageClass, attribute


def test_required_attribute():
    class Person(MageClass):
        first_name = attribute(types=str, required=True)
        second_name = attribute(types=str, required=True)
        middle_name = attribute(types=str)

    persons_without_middle_name = [
        Person(first_name="Tom", second_name="Smith"),
        Person(
            {
                "first_name": "Tom",
                "second_name": "Smith",
            }
        ),
    ]
    persons_without_middle_name.append(Person(persons_without_middle_name[0]))

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

    first_name_required = "Value for attribute first_name is required"
    second_name_required = "Value for attribute second_name is required"

    with pytest.raises(ValueError, match=second_name_required):
        Person(first_name="Tom")
    with pytest.raises(ValueError, match=first_name_required):
        Person(second_name="Tom")
    with pytest.raises(ValueError, match=second_name_required):
        Person(first_name="Tom", middle_name="Jerry")
    with pytest.raises(ValueError, match=second_name_required):
        Person({"first_name": "Tom", "middle_name": "Jerry"})
    with pytest.raises(ValueError, match=first_name_required):
        Person({})
    with pytest.raises(ValueError, match=first_name_required):
        Person()
