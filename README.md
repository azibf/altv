[![GitHub](https://img.shields.io/badge/license-MIT-blue)](/LICENSE) 
[![GitHub](https://img.shields.io/badge/requirements-up--to--date-green)](/requirements.txt)
# Pool master
## Содержание проекта

* [Общее описание](#Общее-описание)
* [Структура проекта](#Структура-проекта)
* [Описание технологий](#Описание-технологий)
* [Контакты](#Контакты)

## Общее описание
Данный проект решает проблему импортозамещения проприетарных гипервизоров иностранной разработки, путем написания собственного аналога, основной идеей которого является простота развёртывания и использования.


## Структура проекта
```
├─── api.py - функционал общение с Proxmox
├─── urls.py - веб обертка
├─── data 
│     ├──db_session.py - связь с БД
│     ├──models.py - моддели объектов БД
│
├───static
│
└───templates
        ├── add.html
        ├── base.html
        ├── edit.html
        ├── index.html
        ├── login.html
        ├── pool.html
        ├── pools.html
```
## Описание технологий

Для реализации проекта использовались следующие технологии:
* **Flask** - это фреймворк для создания веб-приложений на языке программирования Python, использующий набор инструментов Werkzeug, а также шаблонизатор Jinja2.
* **SQLAchemy** -  это программное обеспечение с открытым исходным кодом для работы с базами данных при помощи языка SQL.
* **Proxmoxer** - это оболочка вокруг REST API Proxmox v2, которая позволяет программно создавать, удалять и управлять экземплярами управляемых виртуальных машин и контейнеров.
    
## Контакты
Telegram @a_z_i_b_f
