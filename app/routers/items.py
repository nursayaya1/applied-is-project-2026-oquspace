from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlmodel import Session, select
from app.database.db import get_session
from app.database.models import Plant, Category, Room, CareLog
from app.schemas import PlantCreate, PlantUpdate, CareCreate
from datetime import date

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
def list_plants(search: str = Query('', max_length=80), category_id: int | None = None,
                room_id: int | None = None, min_price: float = Query(0, ge=0),
                max_price: float | None = Query(None, ge=0),
                session: Session = Depends(get_session)):
    if max_price is not None and max_price < min_price:
        raise HTTPException(422, 'Максимальная цена меньше минимальной')
    query = select(Plant).where(Plant.price >= min_price)
    if max_price is not None:
        query = query.where(Plant.price <= max_price)
    if category_id is not None:
        query = query.where(Plant.category_id == category_id)
    if room_id is not None:
        query = query.where(Plant.room_id == room_id)
    # Python casefold also handles Cyrillic, unlike SQLite's default lower().
    rows = session.exec(query.order_by(Plant.id)).all()
    term = search.strip().casefold()
    return [p for p in rows if term in p.name.casefold()]


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


@router.patch('/{plant_id}', response_model=Plant)
def update_plant(plant_id: int, data: PlantUpdate, session: Session = Depends(get_session)):
    plant = find_plant(plant_id, session)
    updates = data.model_dump(exclude_unset=True)
    check_references(updates, session)
    plant.sqlmodel_update(updates)
    session.add(plant)
    session.commit()
    session.refresh(plant)
    return plant


@router.delete('/{plant_id}', status_code=204)
def delete_plant(plant_id: int, session: Session = Depends(get_session)):
    session.delete(find_plant(plant_id, session))
    session.commit()
    return Response(status_code=204)


@router.post('/{plant_id}/care', response_model=CareLog, status_code=201)
def add_care(plant_id: int, data: CareCreate, session: Session = Depends(get_session)):
    plant = find_plant(plant_id, session)
    log = CareLog(plant_id=plant_id, **data.model_dump())
    if data.action == 'Полив':
        plant.last_watered = date.today()
        session.add(plant)
    session.add(log)
    session.commit()
    session.refresh(log)
    return log
