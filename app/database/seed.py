from datetime import date, timedelta
from sqlmodel import Session, select
from app.database.db import engine, init_db
from app.database.models import Category, Room, Plant, CareLog


def seed():
    init_db()
    with Session(engine) as session:
        if session.exec(select(Category)).first():
            return
        categories = [Category(name=n) for n in ['Лиственные', 'Суккуленты', 'Цветущие']]
        rooms = [Room(name=n) for n in ['Гостиная', 'Спальня', 'Кухня']]
        session.add_all(categories + rooms)
        session.flush()
        data = [
            ('Монстера', 'Monstera deliciosa', 0, 0, 7, 6500, 8),
            ('Фикус', 'Ficus elastica', 0, 1, 7, 4900, 3),
            ('Эхеверия', 'Echeveria elegans', 1, 2, 14, 1800, 5),
            ('Спатифиллум', 'Spathiphyllum', 2, 0, 5, 4200, 5),
            ('Алоэ', 'Aloe vera', 1, 2, 14, 2500, 2),
        ]
        for name, species, cat, room, days, price, ago in data:
            plant = Plant(name=name, species=species, category_id=categories[cat].id,
                          room_id=rooms[room].id, watering_days=days, price=price,
                          last_watered=date.today()-timedelta(days=ago))
            session.add(plant)
            session.flush()
            session.add(CareLog(plant_id=plant.id, action='Полив', performed_on=plant.last_watered,
                                note='Первичная запись коллекции'))
        session.commit()


if __name__ == '__main__':
    seed()
    print('Jasyl: база данных подготовлена')
