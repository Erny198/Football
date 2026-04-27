# Архитектура v0.2

```text
Telegram Coach Bot
│
├── База знаний
│   ├── principles.json
│   ├── exercises.json
│   ├── cases.json
│   └── training_templates.json
│
├── Сценарии
│   ├── /training
│   ├── /case
│   ├── /pre_match
│   ├── /post_match
│   └── /export
│
├── Хранилище
│   ├── JSONStorage — MVP
│   └── PostgreSQLStorage — planned
│
└── Railway
    └── long polling worker
```

## Принцип работы

Бот не ставит оценки. Он помогает тренеру:

1. сформулировать цель;
2. выбрать режим;
3. подобрать упражнение;
4. определить, на что смотреть;
5. зафиксировать вывод;
6. выбрать следующий шаг.

## Хранилище

В v0.2 используется JSON-файл. Для production рекомендуется PostgreSQL.
