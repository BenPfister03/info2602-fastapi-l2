import typer
from app.database import create_db_and_tables, get_session, drop_all
from app.models import User
from sqlmodel import select
from sqlalchemy.exc import IntegrityError

cli = typer.Typer(help="User management CLI commands")


@cli.command()
def initialize():
    """
    Initialize the database by dropping all tables,
    recreating them, and inserting a default user.
    """
    with get_session() as db:
        drop_all()
        create_db_and_tables()

        bob = User("bob", "bob@mail.com", "bobpass")
        db.add(bob)
        db.commit()
        db.refresh(bob)

        print("Database Initialized")


@cli.command()
def get_user(
    username: str = typer.Argument(..., help="Username of the user to retrieve")
):
    """
    Retrieve a single user by username.
    """
    with get_session() as db:
        user = db.exec(select(User).where(User.username == username)).first()
        if not user:
            print(f"{username} not found!")
            return
        print(user)


@cli.command()
def get_all_users():
    """
    Retrieve and display all users in the database.
    """
    with get_session() as db:
        all_users = db.exec(select(User)).all()
        if not all_users:
            print("No users found")
            return

        for user in all_users:
            print(user)


@cli.command()
def find_user(
    query: str = typer.Argument(
        ..., help="Partial username or email to search for"
    )
):
    """
    Find users using a partial match on username or email.
    """
    with get_session() as db:
        users = db.exec(
            select(User).where(
                (User.username.contains(query)) |
                (User.email.contains(query))
            )
        ).all()

        if not users:
            print("No matching users found.")
            return

        for user in users:
            print(user)


@cli.command()
def list_users(
    limit: int = typer.Option(10, help="Number of users to return"),
    offset: int = typer.Option(0, help="Number of users to skip")
):
    """
    List users with pagination support.
    """
    with get_session() as db:
        users = db.exec(
            select(User).offset(offset).limit(limit)
        ).all()

        if not users:
            print("No users found.")
            return

        for user in users:
            print(user)


@cli.command()
def change_email(
    username: str = typer.Argument(..., help="Username of the account"),
    new_email: str = typer.Argument(..., help="New email address")
):
    """
    Update a user's email address.
    """
    with get_session() as db:
        user = db.exec(select(User).where(User.username == username)).first()
        if not user:
            print(f"{username} not found! Unable to update email.")
            return

        user.email = new_email
        db.add(user)
        db.commit()

        print(f"Updated {user.username}'s email to {user.email}")


@cli.command()
def create_user(
    username: str = typer.Argument(..., help="Username for the new user"),
    email: str = typer.Argument(..., help="Email address for the new user"),
    password: str = typer.Argument(..., help="Password for the new user")
):
    """
    Create a new user account.
    """
    with get_session() as db:
        newuser = User(username, email, password)
        try:
            db.add(newuser)
            db.commit()
        except IntegrityError:
            db.rollback()
            print("Username or email already taken!")
        else:
            print(newuser)


@cli.command()
def delete_user(
    username: str = typer.Argument(..., help="Username of the user to delete")
):
    """
    Delete a user by username.
    """
    with get_session() as db:
        user = db.exec(select(User).where(User.username == username)).first()
        if not user:
            print(f"{username} not found! Unable to delete user.")
            return

        db.delete(user)
        db.commit()
        print(f"{username} deleted")


if __name__ == "__main__":
    cli()