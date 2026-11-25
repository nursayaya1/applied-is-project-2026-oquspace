"""Exercise real Streamlit widgets against the running local FastAPI server."""
import json
import os
from pathlib import Path
import requests
from streamlit.testing.v1 import AppTest

os.environ.setdefault('BACKEND_URL','http://127.0.0.1:8010')
base=os.environ['BACKEND_URL']
checks=[]

def record(name, condition):
    assert condition, name
    checks.append({'check':name,'result':'passed'})

def find(items, label):
    return next(item for item in items if item.label==label)

at=AppTest.from_file(str(Path(__file__).resolve().parents[1]/'app/frontend/ui.py'), default_timeout=20).run()
record('Обзор загружается без исключений', not at.exception)
find(at.radio,'Навигация').set_value('Моя коллекция').run()
record('Коллекция загружается',not at.exception)
# Both forms are rendered inside tabs; the first name input is the add form.
find(at.text_input,'Название *').set_value('Проверка интерфейса')
find(at.text_input,'Вид растения').set_value('UI test')
find(at.button,'Добавить растение').click().run()
rows=requests.get(base+'/plants',params={'search':'Проверка интерфейса'},timeout=10).json()
record('POST из формы создаёт растение',len(rows)==1)
pid=rows[0]['id']
try:
    find(at.text_input,'Поиск по названию').set_value('Проверка интерфейса').run()
    record('Поиск возвращает одну запись',any('Найдено растений: 1' in c.value for c in at.caption))
    find(at.selectbox,'Выберите растение').set_value(pid).run()
    # The edit form is second in the widget tree.
    [x for x in at.text_input if x.label=='Название *'][1].set_value('Пилея после изменения')
    find(at.button,'Сохранить изменения').click().run()
    record('PATCH из формы сохраняет изменение',requests.get(f'{base}/plants/{pid}',timeout=10).json()['name']=='Пилея после изменения')
    find(at.radio,'Навигация').set_value('Календарь ухода').run()
    record('Календарь загружается',not at.exception)
    find(at.radio,'Навигация').set_value('Журнал').run()
    find(at.selectbox,'Растение').set_value(pid)
    find(at.selectbox,'Действие').set_value('Осмотр')
    find(at.text_input,'Заметка').set_value('Проверка формы журнала')
    find(at.button,'Записать уход').click().run()
    record('Форма журнала сохраняет уход',any(x['plant_id']==pid for x in requests.get(base+'/care-logs',timeout=10).json()))
    find(at.radio,'Навигация').set_value('О проекте').run()
    record('Страница автора загружается',not at.exception)
    find(at.radio,'Навигация').set_value('Моя коллекция').run()
    find(at.selectbox,'Выберите растение').set_value(pid).run()
    find(at.checkbox,'Удалить растение и все записи ухода').check().run()
    find(at.button,'Удалить растение').click().run()
    record('DELETE из интерфейса удаляет запись',requests.get(f'{base}/plants/{pid}',timeout=10).status_code==404)
    record('Интерфейс завершил сценарий без исключений',not at.exception)
finally:
    requests.delete(f'{base}/plants/{pid}',timeout=10)

Path('docs/verification-ui.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(checks,ensure_ascii=False,indent=2))
