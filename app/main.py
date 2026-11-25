from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from sqlmodel import Session, select
from app.database.db import get_session
from app.database.seed import seed
from app.database.models import Category, Room, CareLog
from app.routers.items import router


@asynccontextmanager
async def lifespan(app):
    seed()
    yield


app = FastAPI(title='Jasyl API', description='Коллекция растений и журнал ухода', lifespan=lifespan)
app.include_router(router)


@app.get('/')
def status():
    return {'status': 'ok', 'project': 'Jasyl'}


@app.get('/categories', response_model=list[Category])
def categories(session: Session = Depends(get_session)):
    return session.exec(select(Category)).all()


@app.get('/rooms', response_model=list[Room])
def rooms(session: Session = Depends(get_session)):
    return session.exec(select(Room)).all()


@app.get('/care-logs', response_model=list[CareLog])
def care_logs(session: Session = Depends(get_session)):
    return session.exec(select(CareLog).order_by(CareLog.id.desc())).all()
