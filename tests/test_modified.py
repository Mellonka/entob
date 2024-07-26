from entob import Describe, ValueObject


def test_simple():
    class Person(ValueObject):
        first_name = Describe(types=str)
        second_name = Describe(types=str)
        middle_name = Describe(types=str, nullable=True)

    tom = Person(first_name="Tom", second_name="Smith")
    assert tom.modified_fields == set()

    tom.first_name = "Jerry"
    assert tom.modified_fields == {"first_name"}

    tom.middle_name = "Mouse"
    assert tom.modified_fields == {"first_name", "middle_name"}

    tom.set_modified("second_name")
    assert tom.modified_fields == {"first_name", "middle_name", "second_name"}
