from sqlmodel import Field, SQLModel
from typing import Optional
from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    password: str

    def __init__(self, username: str, email: str, password: str):
        """
        Custom initializer to support positional arguments
        used by the CLI initialize command.
        """
        super().__init__(
            username=username,
            email=email,
            password=password_hash.hash(password)
        )