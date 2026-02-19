# Модель салона красоты

Система автоматизации работы салона красоты, реализованная на Python с соблюдением принципов ООП, чистой архитектуры, стандартов PEP8, аннотации типов.

## Архитектура проекта

Проект разделен на слои: сущности (entities), исключения (exceptions), интерфейс (interface) и инфраструктура данных (utils).

---

### Основные сущности

* салон красоты - класс `Salon`
* клиент - `Client`
* мастер - `Master`
* услуги - `Service`, `CosmeticProcedure`, `HairService`
* ресурсы в инвентаре - `InventoryItem`
* косметика - `Cosmetics`
* парикмахерское оборудование - `HairdressingEquipment`
* стойка ресепшн - `Reception`
* бронирование - `Booking`

### Реализованные поведения
* операция записи на услуги
* операция проведения косметических процедур
* операция стрижки и укладки волос
* операция продажи косметических средств
* операция оплаты услуг

### Описание классов

**Salon**: Центральный узел системы. Агрегирует списки персонала, услуг и инвентаря. Отвечает за координацию высокоуровневых операций.

#### Слой управления (Management)
* **Reception**: Класс-контроллер. Управляет финансовым балансом и реестром бронирований. Инкапсулирует логику записи клиентов.
* **Booking**: Сущность, связывающая клиента, мастера и конкретную услугу. Хранит статус выполнения записи.
* **Master**: Представляет сотрудника. Содержит данные о квалификации и специализации (`MastersSpecialization`).
* **Client**: Клиент салона красоты.

#### Слой инвентаря (Inventory)
* **InventoryItem**: Базовый класс для материальных ресурсов. Определяет методы управления количеством.
* **Cosmetics**: Косметика, имеющая цену. Используется в косметических процедурах.
* **HairdressingEquipment**: Парикмахерское оборудование для стрижки и укладки волос.

#### Слой услуг (Services)
* **Service**: Определяет интерфейс выполнения услуги и требования к ресурсам.
* **HairService / CosmeticProcedure**: Конкретные реализации услуг, потребляющие соответствующие ресурсы из инвентаря.

* **SalonDataManager**: Реализует сохранение состояния всего салона в JSON-файл и восстановление связей между объектами при загрузке.

* **Exceptions**: Описывают исключения для обработки ошибочных ситуаций

* **Interface**: в `cli.py` описан пользовательский интерфейс командной строки

* **Utils**: В данной директории находится `data_manager.py` с классом DataManager, реализующий сохранение состояния системы. Также здесь хранятся валидаторы данных и классы `enum` для реализации системы специализаций сотрудников и статуса бронирований. 
---

Менеджер может:
* увольнять\нанимать\просматривать персонал
* отменять\создавать\отмечать выполненным бронирование
* продавать косметику\пополнять инвентарь салона
* добавить\удалить предоставляемые сервисы
* просматривать историю бронирований

### Интерфейс

Система предлагает интерфейс командной строки CLI:
```
--- MAIN MENU ---
1. Staff Management
2. Inventory & Sales
3. Booking Management
4. Service Management
5. Finance & History
0. Exit
```

Пример управления персоналом:
```
Welcome to 'BEST SALON' Salon Management System!

--- MAIN MENU ---
1. Staff Management
2. Inventory & Sales
3. Booking Management
4. Service Management
5. Finance & History
0. Exit
Select an option: 1

--- STAFF MANAGEMENT ---
1. Show Staff List
2. Hire New Master
3. Fire Master
0. Back to Main Menu
Select an action: 1

Our Team:
- Master Andrew (Specialization: Hair styling master)
- Master Liz (Specialization: Cosmetics master)

--- STAFF MANAGEMENT ---
1. Show Staff List
2. Hire New Master
3. Fire Master
0. Back to Main Menu
Select an action: 2
Enter master's name: John
Enter master's age: 25

Available Specializations:
1. Cosmetics master
2. Hair cutting master
3. Hair styling master
Select specialization (number): 2
Master John has been successfully hired!
```

Пример продажи косметики:

```
--- MAIN MENU ---
1. Staff Management
2. Inventory & Sales
3. Booking Management
4. Service Management
5. Finance & History
0. Exit
Select an option: 2

--- INVENTORY ---
1. View Products
2. Sell Product
3. Restock / Add New Item
0. Back to Main Menu
Action: 1

--- SALON INVENTORY REPORT ---
[Cosmetic] Toner | Stock: 7 | Price: 15.0BYN
[Cosmetic] Serum | Stock: 8 | Price: 20.0BYN
[Equipment] Scissors | Stock: 4
[Equipment] Hair Dryer | Stock: 2

--- INVENTORY ---
1. View Products
2. Sell Product
3. Restock / Add New Item
0. Back to Main Menu
Action: 2
Enter product name: Serum
Enter quantity to sell: 3
Sold Serum with 3 item(s)
Current Salon Balance: 560.0BYN

--- INVENTORY ---
1. View Products
2. Sell Product
3. Restock / Add New Item
0. Back to Main Menu
Action: 1

--- SALON INVENTORY REPORT ---
[Cosmetic] Toner | Stock: 7 | Price: 15.0BYN
[Cosmetic] Serum | Stock: 5 | Price: 20.0BYN
[Equipment] Scissors | Stock: 4
[Equipment] Hair Dryer | Stock: 2
```

### Тесты

Система протестирована набором тестов с помощью библиотеки `pytest`:
<img width="962" height="546" alt="image" src="https://github.com/user-attachments/assets/2fd976cb-a839-40db-8621-77d4f342a225" />
