import pytest
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select
from app.main import app
from app.database.db import get_session
from app.database.models import Category, Room, CareLog


@pytest.fixture
def client():
    engine = create_engine('sqlite://', connect_args={'check_same_thread':False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        session.add(Category(name='Лиственные'))
        session.add(Room(name='Гостиная'))
        session.commit()
    def override():
        with Session(engine) as session:
            yield session
    app.dependency_overrides[get_session] = override
    # No lifespan: fixture owns its isolated database, seed must not touch the real one.
    yield TestClient(app)
    app.dependency_overrides.clear()
    engine.dispose()


@pytest.fixture
def payload():
    return {'name':'Монстера','category_id':1,'room_id':1,'price':6500,'watering_days':7}


def test_get_empty(client):
    response=client.get('/plants')
    assert response.status_code==200
    assert response.json()==[]


def test_create_and_get(client,payload):
    response=client.post('/plants',json=payload)
    assert response.status_code==201
    assert response.json()['id']==1
    assert client.get('/plants/1').json()['name']=='Монстера'


@pytest.mark.parametrize('change',[{'name':''},{'name':'  '},{'price':-1},{'watering_days':0},{'category_id':999},{'room_id':999},{'id':88},{'last_watered':'2999-01-01'}])
def test_invalid_create(client,payload,change):
    assert client.post('/plants',json=payload|change).status_code==422
    assert client.get('/plants').json()==[]


def test_partial_update(client,payload):
    client.post('/plants',json=payload)
    response=client.patch('/plants/1',json={'price':7000})
    assert response.status_code==200
    assert response.json()['price']==7000
    assert response.json()['name']==payload['name']


@pytest.mark.parametrize('change',[{'name':None},{'price':-1},{'category_id':900},{'watering_days':91}])
def test_invalid_patch(client,payload,change):
    client.post('/plants',json=payload)
    assert client.patch('/plants/1',json=change).status_code==422
    assert client.get('/plants/1').json()['price']==payload['price']


def test_search_and_range(client,payload):
    client.post('/plants',json=payload)
    assert len(client.get('/plants',params={'search':'МОНСТ'}).json())==1
    assert client.get('/plants',params={'min_price':7000}).json()==[]
    assert client.get('/plants',params={'max_price':100}).json()==[]
    assert client.get('/plants',params={'category_id':999}).json()==[]
    assert client.get('/plants',params={'search':"' OR 1=1 --"}).json()==[]
    assert client.get('/plants',params={'min_price':10,'max_price':5}).status_code==422


def test_care_and_cascade_delete(client,payload):
    client.post('/plants',json=payload)
    assert client.post('/plants/1/care',json={'action':'Полив'}).status_code==201
    assert client.get('/plants/1').json()['last_watered']==str(date.today())
    assert len(client.get('/care-logs').json())==1
    assert client.delete('/plants/1').status_code==204
    assert client.get('/care-logs').json()==[]
    assert client.get('/plants/1').status_code==404
    assert client.patch('/plants/1',json={'name':'Фикус'}).status_code==404
    assert client.delete('/plants/1').status_code==404
    assert client.post('/plants/1/care',json={'action':'Полив'}).status_code==404


def test_reference_routes(client):
    assert client.get('/').json()['status']=='ok'
    assert len(client.get('/categories').json())==1
    assert len(client.get('/rooms').json())==1
    assert client.get('/openapi.json').status_code==200
