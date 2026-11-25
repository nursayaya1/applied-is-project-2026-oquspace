import html
import os
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

BASE_URL = os.getenv('BACKEND_URL', 'http://127.0.0.1:8000').rstrip('/')
ASSETS = Path(__file__).parent / 'assets'
st.set_page_config(page_title='Jasyl · Мой зелёный дом', page_icon='🌿', layout='wide')
st.markdown('''<style>
.block-container{max-width:1250px;padding-top:4.5rem;padding-bottom:3rem}
h1,h2,h3{letter-spacing:-.035em} h1{font-size:2.8rem!important}
[data-testid="stSidebar"]{background:#113d2c;color:#f5fff6}
[data-testid="stSidebar"] *{color:inherit}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p{color:#d4e6da}
[data-testid="stSidebar"] hr{border-color:#547463}
[data-testid="stMetric"]{background:white;border:1px solid #dde7df;border-radius:18px;padding:20px}
[data-testid="stVerticalBlockBorderWrapper"]>div{border-radius:18px}
.eyebrow{font-size:14px;letter-spacing:.13em;text-transform:uppercase;color:#5b7866;margin-bottom:12px}
.hero{padding:32px 38px;background:#dcebdc;border-radius:24px;margin:18px 0 26px}
.hero h1{margin:0;max-width:680px;line-height:1.1;color:#123f2b}
.hero p{font-size:18px;color:#466553;max-width:650px;margin-bottom:0}
.brand{font-size:38px;font-weight:750;letter-spacing:-2px;margin-top:10px}
.badge{display:inline-block;padding:5px 11px;border-radius:30px;background:#e8f1e9;color:#286243;font-size:14px}
.due{background:#fff0d9;color:#8a5718}
.plant-name{font-size:24px;font-weight:650;margin:8px 0 2px}
.muted{color:#688073;font-size:15px}
button{min-height:42px!important} [data-testid="stForm"]{background:white;border-radius:18px}
@media(max-width:640px){.hero{padding:24px}.hero h1{font-size:2rem!important}.block-container{padding-top:4rem}}
</style>''', unsafe_allow_html=True)


def api(method, path, **kwargs):
    try:
        response = requests.request(method, BASE_URL + path, timeout=12, **kwargs)
        response.raise_for_status()
        return response.json() if response.content else True
    except requests.HTTPError as error:
        try:
            detail = error.response.json().get('detail')
            if isinstance(detail, list):
                detail = '; '.join(f"{e['loc'][-1]}: {e['msg']}" for e in detail)
        except ValueError:
            detail = 'Сервер не смог обработать запрос'
        st.error(f'Не удалось сохранить изменения: {detail}')
    except requests.RequestException:
        st.error('Не удалось подключиться к серверу. Проверьте, запущен ли Backend, и обновите страницу.')
    return None


def saved(message):
    st.session_state['notice'] = message
    st.rerun()


def due_in(plant):
    return (date.fromisoformat(plant['last_watered']) + timedelta(days=plant['watering_days']) - date.today()).days


with st.sidebar:
    st.markdown('<div class="brand">🌿 Jasyl</div>', unsafe_allow_html=True)
    st.caption('Мой зелёный дом')
    st.divider()
    page = st.radio('Навигация', ['Обзор', 'Моя коллекция', 'Календарь ухода', 'Журнал', 'О проекте'], label_visibility='collapsed')
    st.divider()
    st.markdown('**Растите вместе**\n\nНемного заботы каждый день — и дома становится зеленее.')
    st.caption('Нұрсая Жұматай · ИС 24 а1')

if 'notice' in st.session_state:
    st.success(st.session_state.pop('notice'))

categories = api('GET', '/categories')
rooms = api('GET', '/rooms')
plants = api('GET', '/plants')
if categories is None or rooms is None or plants is None:
    if st.button('Повторить подключение'):
        st.rerun()
    st.stop()
cats = {c['id']: c['name'] for c in categories}
room_names = {r['id']: r['name'] for r in rooms}


def card(plant):
    with st.container(border=True):
        picture = ASSETS / f"plant-{(plant['category_id']-1)%3}.png"
        if picture.exists():
            st.image(str(picture), width='stretch')
        st.markdown(f'<div class="plant-name">{html.escape(plant["name"])}</div><div class="muted">{html.escape(plant["species"])}</div>', unsafe_allow_html=True)
        days = due_in(plant)
        label = 'Пора полить' if days <= 0 else f'Полив через {days} дн.'
        st.markdown(f'<p><span class="badge {"due" if days <= 0 else ""}">{label}</span></p>', unsafe_allow_html=True)
        st.caption(f'{room_names[plant["room_id"]]} · каждые {plant["watering_days"]} дн.')
        if st.button('Отметить полив', key=f'water-{plant["id"]}', width='stretch'):
            if api('POST', f'/plants/{plant["id"]}/care', json={'action':'Полив'}):
                saved(f'{plant["name"]}: полив записан')


def plant_form(existing=None):
    p = existing or {}
    with st.form('edit' if existing else 'add', clear_on_submit=not existing):
        a, b = st.columns(2)
        name = a.text_input('Название *', p.get('name',''), max_chars=80)
        species = b.text_input('Вид растения', p.get('species',''), max_chars=120)
        cat_ids, room_ids = list(cats), list(room_names)
        cat = a.selectbox('Категория', cat_ids, index=cat_ids.index(p.get('category_id',cat_ids[0])), format_func=cats.get)
        room = b.selectbox('Комната', room_ids, index=room_ids.index(p.get('room_id',room_ids[0])), format_func=room_names.get)
        days = a.number_input('Интервал полива, дней', 1, 90, p.get('watering_days',7))
        price = b.number_input('Стоимость, ₸', 0.0, 10000000.0, float(p.get('price',0)), step=100.0)
        watered = a.date_input('Последний полив', date.fromisoformat(p['last_watered']) if existing else date.today(), max_value=date.today())
        notes = st.text_area('Заметки', p.get('notes',''), max_chars=2000)
        submit = st.form_submit_button('Сохранить изменения' if existing else 'Добавить растение', type='primary')
        if submit:
            if not name.strip():
                st.error('Введите название растения')
            else:
                payload = dict(name=name, species=species, category_id=cat, room_id=room, watering_days=days,
                               price=price, last_watered=watered.isoformat(), notes=notes)
                result = api('PATCH' if existing else 'POST', f'/plants/{p["id"]}' if existing else '/plants', json=payload)
                if result:
                    saved('Изменения сохранены' if existing else 'Растение добавлено в коллекцию')


if page == 'Обзор':
    st.markdown('<div class="eyebrow">Ваша домашняя оранжерея</div><div class="hero"><h1>Больше зелени.<br>Меньше забот.</h1><p>Все ваши растения, привычки ухода и маленькие зелёные победы — в одном месте.</p></div>', unsafe_allow_html=True)
    a,b,c = st.columns(3)
    a.metric('Растений в коллекции', len(plants))
    b.metric('Ждут полива', sum(due_in(p)<=0 for p in plants))
    c.metric('Комнат с растениями', len({p['room_id'] for p in plants}))
    st.subheader('Сегодня в вашем саду')
    st.caption('Начните с растений, которым сейчас нужно внимание.')
    featured = sorted(plants, key=due_in)[:3]
    for col, plant in zip(st.columns(3), featured):
        with col:
            card(plant)
    if not plants:
        st.info('Коллекция пока пуста. Добавьте первое растение в разделе «Моя коллекция».')

elif page == 'Моя коллекция':
    st.title('Моя коллекция')
    st.caption('У каждого растения — своё место и свой ритм.')
    browse, add, edit = st.tabs(['Все растения', 'Добавить растение', 'Изменить или удалить'])
    with browse:
        a,b,c = st.columns([2,1,1])
        search = a.text_input('Поиск по названию', placeholder='Например, монстера')
        category = b.selectbox('Категория', [None]+list(cats), format_func=lambda k: cats.get(k,'Все категории'))
        room = c.selectbox('Комната', [None]+list(room_names), format_func=lambda k: room_names.get(k,'Все комнаты'))
        with st.expander('Фильтр по стоимости'):
            a,b = st.columns(2)
            low = a.number_input('От, ₸', min_value=0.0, value=0.0)
            high = b.number_input('До, ₸', min_value=0.0, value=10000000.0)
        params = {'search':search,'min_price':low,'max_price':high}
        if category is not None: params['category_id'] = category
        if room is not None: params['room_id'] = room
        filtered = api('GET','/plants',params=params)
        if filtered is not None:
            st.caption(f'Найдено растений: {len(filtered)}')
            view = st.radio('Отображение', ['Карточки','Таблица'], horizontal=True)
            if not filtered:
                st.info('Ничего не найдено. Измените поиск или фильтры.')
            elif view == 'Таблица':
                rows = [{'ID':p['id'],'Название':p['name'],'Вид':p['species'],'Категория':cats[p['category_id']],
                         'Комната':room_names[p['room_id']],'Стоимость, ₸':p['price'],
                         'Полив каждые, дн.':p['watering_days'],'Последний полив':p['last_watered']} for p in filtered]
                st.dataframe(pd.DataFrame(rows), hide_index=True, width='stretch')
                st.download_button('Скачать таблицу CSV', pd.DataFrame(rows).to_csv(index=False).encode('utf-8-sig'), 'jasyl-plants.csv','text/csv')
            else:
                for offset in range(0,len(filtered),3):
                    for col, plant in zip(st.columns(3), filtered[offset:offset+3]):
                        with col: card(plant)
    with add:
        st.subheader('Новый зелёный житель')
        plant_form()
    with edit:
        if plants:
            selected = st.selectbox('Выберите растение', [p['id'] for p in plants], format_func=lambda i: next(f'{p["name"]} · №{i}' for p in plants if p['id']==i))
            current = next(p for p in plants if p['id']==selected)
            plant_form(current)
            st.markdown('#### Удаление растения')
            confirm = st.checkbox('Удалить растение и все записи ухода', key=f'confirm-{selected}')
            if st.button('Удалить растение', disabled=not confirm):
                if api('DELETE',f'/plants/{selected}'):
                    saved('Растение и связанные записи удалены')
        else:
            st.info('Сначала добавьте растение.')

elif page == 'Календарь ухода':
    st.title('Календарь ухода')
    st.caption('План полива рассчитан по последней дате и заданному интервалу.')
    for p in sorted(plants,key=due_in):
        with st.container(border=True):
            a,b,c = st.columns([2,2,1])
            a.markdown(f'**{p["name"]}**')
            a.caption(room_names[p['room_id']])
            days = due_in(p)
            b.write('Сегодня' if days == 0 else f'Просрочен на {-days} дн.' if days < 0 else f'Через {days} дн.')
            b.caption(str(date.fromisoformat(p['last_watered'])+timedelta(days=p['watering_days'])))
            if c.button('Полить',key=f'calendar-{p["id"]}'):
                if api('POST',f'/plants/{p["id"]}/care',json={'action':'Полив'}): saved('Полив записан')
    if not plants: st.info('Добавьте растения, чтобы появился план ухода.')

elif page == 'Журнал':
    st.title('История заботы')
    st.caption('Полив, подкормка, пересадка и наблюдения за вашей коллекцией.')
    if plants:
        with st.form('care'):
            a,b = st.columns(2)
            plant_id = a.selectbox('Растение',[p['id'] for p in plants],format_func=lambda i: next(p['name'] for p in plants if p['id']==i))
            action = b.selectbox('Действие',['Полив','Подкормка','Пересадка','Осмотр'])
            note = st.text_input('Заметка',max_chars=1000)
            if st.form_submit_button('Записать уход',type='primary'):
                if api('POST',f'/plants/{plant_id}/care',json={'action':action,'note':note}): saved('Запись добавлена')
    logs = api('GET','/care-logs')
    if logs:
        names = {p['id']:p['name'] for p in plants}
        st.dataframe(pd.DataFrame([{'Дата':x['performed_on'],'Растение':names.get(x['plant_id'],''),'Действие':x['action'],'Заметка':x['note']} for x in logs]),hide_index=True,width='stretch')
    else: st.info('Пока нет записей об уходе.')

else:
    st.title('О Jasyl')
    st.write('Я создала Jasyl, чтобы удобно хранить сведения о комнатных растениях и планировать уход за ними.')
    st.write('В коллекции можно искать, добавлять, редактировать и удалять растения. В календаре виден ближайший полив, а журнал хранит историю ухода.')
    st.markdown('**Автор:** Нұрсая Жұматай  \n**Группа:** ИС 24 а1')
    st.link_button('Исходный код на GitHub','https://github.com/nursayaya1/applied-is-project-2026-jasyl')
