from typing import Optional
from tortoise.exceptions import ConfigurationError
from tortoise.fields.base import Field
from tortoise.validators import MaxLengthValidator


class BinaryField(Field[bytes], bytes):
    def __init__(self, max_length: int, **kwargs) -> None:
        if int(max_length) < 1:
            raise ConfigurationError("'max_length' must be >= 1")
        self.max_length = int(max_length)
        super().__init__(**kwargs)
        self.validators.append(MaxLengthValidator(self.max_length))

    @property
    def constraints(self) -> dict:
        return {
            "max_length": self.max_length,
        }

    def to_db_value(
        self, value: Optional[bytes], instance: Optional[bytes]
    ) -> Optional[str]:
        return value and str(value)

    @property
    def SQL_TYPE(self) -> str:
        return f"VARBINARY({self.max_length})"
