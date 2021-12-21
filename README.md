# Сравниваем вакансии программистов

Программа умеет получать данные через API с сайтов [hh.ru](https://hh.ru) и [superjob.ru](https://www.superjob.ru/) и выводить статистику по языкам программирования.
В качестве наиболее популярных языков были взяты: Javascript, Java, Python, Ruby, PHP, C++, C#, Go, Objective-C, Scala, Swift.
Полученная статистика выводится в консоль в виде таблицы. Пример:

HeadHunter Moscow------+------------------+---------------------+------------------+
| Язык программирования | Вакансий найдено | Вакансий обработано | Средняя зарплата |
+-----------------------+------------------+---------------------+------------------+
| javascript            | 1180             | 382                 | 187412           |
| java                  | 1117             | 205                 | 236581           |
| python                | 937              | 204                 | 207980           |
| ruby                  | 66               | 20                  | 244235           |
| php                   | 478              | 206                 | 173642           |
| c++                   | 475              | 122                 | 177834           |
| c#                    | 495              | 108                 | 184969           |
| go                    | 314              | 64                  | 214846           |
| objective-c           | 66               | 19                  | 291823           |
| scala                 | 75               | 12                  | 263727           |
| swift                 | 176              | 53                  | 265941           |
+-----------------------+------------------+---------------------+------------------+

Зарплаты, которые указаны в USD или EUR в рассчет не берутся.
Логика для рассчета ожидаемой зарплаты по вакансии следующая - если указаны оба поля «от» и «до», считаем ожидаемый оклад как среднее. Если только «от», умножаем на 1.2, а если только «до», умножаем на 0.8.
В конечном счете программа выдает среднее по ожидаемым зарплатам.

## Как установить

Для запуска кода у вас уже должен быть установлен Python3.
Используйте в консоли `pip` для установки зависимостей или `pip3`, есть есть конфликт с Python2:
```
pip install -r requirements.txt
```

### Получаем токены для работы с API
Токен вам понадобится только для работы с сайтом SuperJob. 
Для того, чтобы получить токен необходимо перейти на сайт [https://api.superjob.ru/](https://api.superjob.ru/) и зарегистрировать приложение.
В ходе регистрации приложения у вас попросят ввести адрес сайта - можете указать любой произвольный адрес.

Пример токена:
```
v3.r.135692717.094fa1bfa3918b8b080cf48111.cc423ef6b08c6efe141efd5289779fe14cVvolhJZVcfM2A11W8NofzEewF6yvY0o2o8d2UW7Y
```
### Создаем файл .env
Чувствительные данные, такие как токены, хранятся в переменных окружения. Для того, чтобы у вас всё работало необходимо создать файл .env в папке, где лежат скрипты.
Пример заполненного файла .env:
```
SUPERJOB_TOKEN="your token here""
```

## Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).
 
