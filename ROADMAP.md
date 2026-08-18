# 🗺️ django-warden Roadmap & Feature Backlog

This document outlines the planned future features, custom checks, and enhancements for **django-warden**. We highly welcome contributions from the open-source community to help realize these milestones!

---

## 🚀 Upcoming Core Checks (Backlog)

These proposed system checks represent high-impact additions to the framework. Each check will prevent common scaling, performance, and reliability pitfalls before they reach production.

### 1. 🎨 Static Template DB Call Auditor (`warden.W012`)
*   **The Issue:** Traversing deep database relationships or calling methods inside template loops (e.g. `{% for item in orders %} {{ item.customer.profile.bio }} {% endfor %}`) triggers silent, untracked N+1 query loops on the presentation layer.
*   **Proposed Check:** Scan local template directories (`.html` files, supporting both Jinja2 and Django Templates). Flag any `{% for %}` loops containing second-level traversals (e.g., `item.customer.name` with multiple dots) or method calls.
*   **Recommendation Hint:** Suggest annotating or prefetching the necessary fields in the View before rendering.

### 2. ⚡ Serializer Nested N+1 Watchdog (`warden.W013`)
*   **The Issue:** Nested serializers (in DRF or Django Ninja) trigger automatic database lookups for each row if the corresponding View did not explicitly configure `select_related` or `prefetch_related`.
*   **Proposed Check:** Perform a static syntax analysis on DRF Serializers or Django Ninja schemas. If nested serialization is detected, locate the corresponding view file and verify that its `get_queryset` implementation contains the matching pre-load options.
*   **Recommendation Hint:** Alert and advise adding the specific pre-load option to the queryset.

### 3. 🚨 Transactional Background Task Guard (`warden.W014`)
*   **The Issue:** Dispatching background tasks inside active `@transaction.atomic` blocks creates race conditions and phantom executions across task queues:
    *   **Celery / External Brokers (Redis/RabbitMQ/SQS):** Calling `.delay()` or `.apply_async()` immediately enqueues the task before the DB transaction commits, causing `ObjectDoesNotExist` in the worker or execution of cancelled jobs on rollback.
    *   **Django Tasks (`django.tasks` / DEP 0014) & `steady_queue`:** Calling `.enqueue()` when using separate task databases (multi-DB architecture) suffers from the exact same race condition and phantom execution traps.
*   **Proposed Check:** Scan Python AST / source files to detect background task dispatch calls (`.delay()`, `.apply_async()`, `.enqueue()`, `.enqueue_on_commit()`) invoked directly inside transactional code paths (functions decorated with `@transaction.atomic` or blocks within `with transaction.atomic():`).
*   **Recommendation Hint:** Advise wrapping the task dispatch inside `transaction.on_commit(lambda: task.delay())` (or `transaction.on_commit(partial(task.enqueue, ...))` / native `enqueue_on_commit` helpers).

### 🗄️ 4. Dangerous Migration Guard (`warden.W015`)
*   **The Issue:** Running database migrations that alter large tables (such as `RenameField` or adding non-nullable columns without safe defaults) locks the table on high-volume PostgreSQL/MySQL instances, leading to production downtime.
*   **Proposed Check:** Analyze newly created Django migration files. Detect potentially blocking operations and warn about their concurrency risks.
*   **Recommendation Hint:** Recommend a safe, multi-phased backfill and deployment strategy for zero-downtime.

---

## 🛠️ How to Contribute to the Roadmap

If you are interested in picking up any of these roadmap items:
1. Review the [Contributing Guidelines](./CONTRIBUTING.md) to understand our coding standards (McCabe < 10, 100% test coverage SLA).
2. Open an issue on GitHub to discuss your proposed implementation strategy.
3. Submit a pull request referencing the issue!
