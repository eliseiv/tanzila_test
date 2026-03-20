## Быстрый запуск

```
docker compose up --build -d
```

Поднимаются следующие контейнера:

FastAPI App - http://localhost:8000 - Основное приложение
Swagger UI - http://localhost:8000/docs - Документация API Swagger
PostgreSQL - localhost:5433 - База данных приложения
Prometheus - http://localhost:9090 - Сбор и хранение метрик
Grafana - http://localhost:3000 - Дашборды (admin / admin)
Node Exporter - http://localhost:9100 - Системные метрики
Loki - http://localhost:3100 - Хранение логов


## API-эндпоинты

### `GET /`
Перенаправление на Swagger UI (`/docs`).

### `GET /health`
Проверка состояния приложения.
```json
{"status": "healthy"}
```

### `GET /message/{id}`
Получение сообщения из PostgreSQL по ID (1–12).
```json
{"id": 1, "text": "Hello, World! Welcome to the observability demo."}
```

### `POST /process`
Поле `data` валидируется: пустые и состоящие только из пробелов строки отклоняются с `422`.
```json
// Запрос
{"data": "some text"}

// Ответ
{"received": "some text", "status": "processed"}
```

### `GET /metrics`
Экспорт Prometheus-метрик в формате OpenMetrics.

## Метрики

### Кастомные метрики приложения
| `app_request_count_total` | Counter | Счётчик запросов по `endpoint` и `method` |
| `app_request_latency_seconds` | Histogram | Гистограмма latency по `endpoint` |
| `app_log_events_total` | Counter | Счётчик warning-событий приложения по `level` |

### Автоматические метрики (prometheus-fastapi-instrumentator)
| `http_requests_total` | Counter | Общее количество HTTP-запросов по `handler`, `method`, `status` |
| `http_request_duration_seconds` | Histogram | Длительность HTTP-запросов |
| `http_request_size_bytes` | Summary | Размер входящих запросов |
| `http_response_size_bytes` | Summary | Размер ответов |

### Системные метрики (Node Exporter)
| `node_cpu_seconds_total` | Использование CPU по режимам |
| `node_memory_MemTotal_bytes` | Общий объём памяти |
| `node_memory_MemAvailable_bytes` | Доступная память |
| `node_filesystem_avail_bytes` | Свободное дисковое пространство |

## Логирование

Логи выводятся в формате structured JSON через `structlog`.
JSON-формат применяется как к логам приложения, так и к логам `uvicorn`:

```json
{
  "event": "message_retrieved",
  "message_id": 1,
  "latency": 0.0012,
  "logger": "app.routes",
  "level": "info",
  "timestamp": "2026-03-19T12:00:00.000000Z"
}
```

**Pipeline сбора логов:**
1. Приложение пишет JSON-логи в stdout
2. Docker logging driver сохраняет их в json-файлы контейнера
3. Promtail собирает логи через Docker socket, парсит JSON-поля из stdout
4. Логи отправляются в Loki
5. В Grafana доступны через Loki datasource

## Grafana Dashboard

JSON-экспорт дашборда: [`grafana/dashboards/app-dashboard.json`](grafana/dashboards/app-dashboard.json)

Дашборд автоматически загружается через Grafana provisioning и содержит 7 панелей:
| Requests per Second | Prometheus | Графики RPS по endpoint |
| Latency Percentiles | Prometheus | p50 / p95 / p99 гистограмма latency |
| CPU Usage | Node Exporter | Утилизация CPU |
| Memory Usage | Node Exporter | Используемая / общая память |
| Errors & Warnings Counter | Prometheus | Количество 5xx ошибок и warning-событий приложения за час |
| HTTP Requests by Status | Prometheus | Распределение запросов по статус-кодам |
| Application Logs | Loki | Структурированные логи приложения |

## Алерты Prometheus
Файл: [`prometheus/alerts.yml`](prometheus/alerts.yml)

| `HighRequestLatency` | p95 latency > 1 сек в течение 1 мин | warning |
| `HighErrorRate` | 5xx rate > 10% в течение 2 мин | critical |

## Тестирование

```bash
# Запуск тестов (использую SQLite, PostgreSQL не нужен)
pytest tests/ -v
```

Тесты включают:
- **14 unit-тестов** эндпоинтов: root redirect, health, message (успешные и ошибочные сценарии), process (echo, sanitize, reject whitespace-only input, ошибки)
- **7 интеграционных тестов** метрик: `/metrics` response, кастомные counter/histogram, instrumentator, `app_log_events_total`, инкремент warning-событий

## Структура проекта

```
├── app/
│   ├── config.py          # Конфигурация (pydantic-settings, env vars)
│   ├── database.py        # SQLAlchemy engine, сессия, get_db dependency
│   ├── logging_config.py  # Structured JSON-логи (structlog)
│   ├── main.py            # FastAPI app, lifespan, instrumentator
│   ├── metrics.py         # Кастомные Prometheus Counter + Histogram
│   ├── models.py          # ORM-модель Message
│   ├── routes.py          # API-эндпоинты
│   ├── schemas.py         # Pydantic-схемы с валидацией (OWASP)
│   └── seed.py            # Seed-данные (12 сообщений)
├── tests/
│   ├── conftest.py        # Фикстуры (SQLite, TestClient)
│   ├── test_endpoints.py  # Unit-тесты эндпоинтов
│   └── test_metrics.py    # Интеграционные тесты метрик
├── prometheus/
│   ├── prometheus.yml     # Scrape targets (app, node-exporter)
│   └── alerts.yml         # Alert rules (latency, errors)
├── grafana/
│   ├── dashboards/
│   │   └── app-dashboard.json
│   └── provisioning/
│       ├── dashboards/dashboards.yml
│       └── datasources/datasources.yml
├── loki/
│   └── loki-config.yml
├── promtail/
│   └── promtail-config.yml
├── Dockerfile             # Multi-stage, non-root user
├── docker-compose.yml     # 7 сервисов
├── requirements.txt       # Python-зависимости
└── .gitignore
```
