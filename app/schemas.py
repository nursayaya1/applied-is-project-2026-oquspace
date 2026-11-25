from datetime import date
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator


class InputModel(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)


class PlantCreate(InputModel):
    name: str = Field(min_length=1, max_length=80)
    species: str = Field(default='', max_length=120)
    category_id: int = Field(gt=0)
    room_id: int = Field(gt=0)
    watering_days: int = Field(default=7, ge=1, le=90)
    price: float = Field(default=0, ge=0, le=10000000, allow_inf_nan=False)
    last_watered: date = Field(default_factory=date.today)
    notes: str = Field(default='', max_length=2000)

    @field_validator('last_watered')
    @classmethod
    def not_future(cls, value):
        if value > date.today():
            raise ValueError('Дата не может быть в будущем')
        return value


class PlantUpdate(InputModel):
    name: str | None = Field(default=None, min_length=1, max_length=80)
    species: str | None = Field(default=None, max_length=120)
    category_id: int | None = Field(default=None, gt=0)
    room_id: int | None = Field(default=None, gt=0)
    watering_days: int | None = Field(default=None, ge=1, le=90)
    price: float | None = Field(default=None, ge=0, le=10000000, allow_inf_nan=False)
    last_watered: date | None = None
    notes: str | None = Field(default=None, max_length=2000)

    @field_validator('*', mode='before')
    @classmethod
    def reject_null(cls, value):
        if value is None:
            raise ValueError('Переданное поле не может быть null')
        return value

    @field_validator('last_watered')
    @classmethod
    def not_future(cls, value):
        return PlantCreate.not_future(value)


class CareCreate(InputModel):
    action: Literal['Полив', 'Подкормка', 'Пересадка', 'Осмотр']
    note: str = Field(default='', max_length=1000)
