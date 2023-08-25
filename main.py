from typing import List, Optional

from sqlmodel import Field, Relationship, Session, SQLModel, create_engine, select


class PersonDogLink(SQLModel, table=True):
    person_id: Optional[int] = Field(
        default=None, foreign_key="person.id", primary_key=True
    )
    dog_id: Optional[int] = Field(default=None, foreign_key="dog.id", primary_key=True)
    is_owner: bool = False

    person: "Person" = Relationship(back_populates="dog_links")
    dog: "Dog" = Relationship(back_populates="person_links")


class Person(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)

    dog_links: List[PersonDogLink] = Relationship(back_populates="person")

    def __str__(self) -> str:
        return self.name


class Dog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)

    person_links: List[PersonDogLink] = Relationship(back_populates="dog")

    def owners(self, session: Session) -> List[Person]:
        statement = (
            select(Person)
            .join(PersonDogLink)
            .where(PersonDogLink.dog_id == self.id)
            .where(PersonDogLink.is_owner == True)
        )
        results = session.exec(statement)
        return results.all()


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def main():
    create_db_and_tables()

    with Session(engine) as session:
        # Alice and Bob are married and have a dog named Fido
        alice: Person = Person(name="Alice Smith")
        bob: Person = Person(name="Bob Smith")

        fido: Dog = Dog(name="Fido")

        alice_fido_link: PersonDogLink = PersonDogLink(
            person=alice, dog=fido, is_owner=True
        )
        bob_fido_link: PersonDogLink = PersonDogLink(
            person=bob, dog=fido, is_owner=True
        )

        # Charles is Fido's vet. He has a relationship with Fido, but is not an owner
        charles: Person = Person(name="Dr Charles The Vet")
        charles_fido_link: PersonDogLink = PersonDogLink(
            person=charles, dog=fido, is_owner=False
        )

        session.add(alice)
        session.add(bob)
        session.add(charles)
        session.add(fido)
        session.add(alice_fido_link)
        session.add(bob_fido_link)
        session.add(charles_fido_link)
        session.commit()

        # TASK: Write a function on Dog to return all the owners
        owners: List[Person] = fido.owners(session)

        assert len(owners) == 2
        assert alice in owners
        assert bob in owners
        assert charles not in owners

        for owner in owners:
            print(f"{owner} is an owner of Fido.")


if __name__ == "__main__":
    main()
