# IFC-IDS-REPORT

Статическое одностраничное веб-приложение для проверки файлов IFC на соответствие спецификациям IDS с использованием библиотек ifcopenshell и ifctester в браузере. Серверная инфраструктура не требуется.

![screenshot](/screenshot.png)

## Возможности

- Загрузка файлов IFC (.ifc) и IDS (.ids, .xml)
- Выполнение Python-кода в браузере через Pyodide (WebAssembly)
- Генерация отчетов в форматах HTML, JSON, ODS, BCF
- Отображение HTML-отчетов во встроенном iframe
- Скачивание отчетов в выбранном формате
- Сводка результатов валидации (общее количество, пройденные, проваленные спецификации)
- Полностью статическое развертывание (GitHub Pages, Netlify и др.)

## Запуск

1. Клонируйте репозиторий и запустите статический сервер:

```bash
git clone https://github.com/<username>/IFC-IDS-REPORT
cd IFC-IDS-REPORT
python -m http.server 8000
```

2. Откройте `http://localhost:8000`
3. Загрузите файлы IFC и IDS, выполните проверку, просмотрите и скачайте отчет.

## Технологический стек

```
Frontend: HTML, JavaScript, Pyodide (CDN)
Python: ifcopenshell (WASM), ifctester, micropip
Отчеты: HTML/JSON/ODS/BCF (ifctester.reporter)
Размер: ~5 МБ (wheels кэшируются в браузере)
```

## Структура файлов

```
├── index.html     # Основное приложение
├── style.css      # Стили интерфейса
├── main.js        # Логика Pyodide и File API
├── app.py         # Логика валидации на Python
└── README.md
```

## Принцип работы

Приложение использует Pyodide для выполнения Python в браузере, официальные WASM-сборки ifcopenshell и динамическую установку ifctester через micropip. Все вычисления выполняются на стороне клиента без серверной компоненты.

## Лицензия

MIT
