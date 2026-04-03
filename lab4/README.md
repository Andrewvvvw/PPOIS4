# Django веб-интерфейс для управления салоном красоты

Добавлен Django клиент-серверный веб-интерфейс для салона красоты.
Оба интерфейса (CLI и веб) используют общий код:

- `common/salon_core` - сущности, валидация, исключения, сохранение, use-cases.
- `lab4/salon_web` - Django-код поверх `SalonAppService`.

Это гарантирует, что бизнес-правила реализуются один раз и повторно используются в обоих интерфейсах.

## Архитектура

### 1) Общий код (`salon_core`)

- `entities/` - модель (`Salon`, `Booking`, `Master`, инвентарьи сервисы).
- `utils/data_manager.py` - работа с json (`salon_save.json`).
- `application/repositories/`:
  - `SalonRepository` интерфейс для работы с хранилищем
  - `JsonSalonRepository` реализация
- `application/service.py` - `SalonAppService` use-cases:
  - `list_staff`, `hire_master`, `fire_master`
  - `list_inventory`, `sell_product`, `restock_or_create_item`
  - `list_services`, `add_service`, `remove_service`
  - `create_booking`, `execute_booking`, `cancel_booking`
  - `get_balance`, `get_booking_history`, `get_dashboard_stats`

### 2) Веб-интерфейс

Страницы Django, отображаемые сервером:

- `/` дашборд(главная страница)
- `/staff` персонал
- `/inventory` инвентарь
- `/services` услуги
- `/bookings` бронирования
- `/finance` финансы

Каждый метод POST выполняет один use-case в `SalonAppService`.

## совместимость

И CLI и веб-интерфейс на Django используют один json-файл:

- `lab1/src/salon_save.json`

Структура JSON не изменяется и совместима с `SalonDataManager` в CLI.

## Инструкция по запуску

```powershell
cd lab4
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Затем открыть `http://127.0.0.1:8000/`.

## Тесты

```powershell
python manage.py test
```
