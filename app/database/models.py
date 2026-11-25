from datetime import date
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    plants: list['Plant'] = Relationship(back_populates='category')


class Room(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    plants: list['Plant'] = Relationship(back_populates='room')


class Plant(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    species: str = ''
    category_id: int = Field(foreign_key='category.id')
    room_id: int = Field(foreign_key='room.id')
    watering_days: int = 7
    price: float = 0
    last_watered: date = Field(default_factory=date.today)
    notes: str = ''
    category: Category = Relationship(back_populates='plants')
    room: Room = Relationship(back_populates='plants')
    logs: list['CareLog'] = Relationship(back_populates='plant', cascade_delete=True)


class CareLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    plant_id: int = Field(foreign_key='plant.id', ondelete='CASCADE', index=True)
    action: str
    performed_on: date = Field(default_factory=date.today)
    note: str = ''
    plant: Plant = Relationship(back_populates='logs')
