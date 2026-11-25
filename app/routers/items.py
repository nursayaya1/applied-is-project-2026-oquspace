from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlmodel import Session, select
from app.database.db import get_session
from app.database.models import Plant, Category, Room
from app.schemas import PlantCreate

router = APIRouter(prefix='/plants', tags=['Растения'])


def find_plant(plant_id, session):
    plant = session.get(Plant, plant_id)
    if plant is None:
        raise HTTPException(404, 'Растение не найдено')
    return plant


def check_references(data, session):
    for field, model in [('category_id', Category), ('room_id', Room)]:
        if field in data and not session.get(model, data[field]):
            raise HTTPException(422, f'Не найдено значение {field}')


@router.get('', response_model=list[Plant])
def list_plants(session: Session = Depends(get_session)):
    return session.exec(select(Plant).order_by(Plant.id)).all()


@router.get('/{plant_id}', response_model=Plant)
def get_plant(plant_id: int, session: Session = Depends(get_session)):
    return find_plant(plant_id, session)


@router.post('', response_model=Plant, status_code=201)
def create_plant(data: PlantCreate, session: Session = Depends(get_session)):
    check_references(data.model_dump(), session)
    plant = Plant.model_validate(data.model_dump())
    session.add(plant)
    session.commit()
    session.refresh(plant)
    return plant
