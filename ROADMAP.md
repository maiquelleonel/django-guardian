# 🗺️ django-warden Roadmap & Feature Backlog

This document outlines the planned future features, custom checks, and enhancements for **django-warden**. We highly welcome contributions from the open-source community to help realize these milestones!

---

## 🚀 Upcoming Core Checks (Backlog)

These proposed system checks represent high-impact additions to the framework. Each check will prevent common scaling, performance, and reliability pitfalls before they reach production.

### 1. 🎨 Static Template DB Call Auditor (`warden.W008`)
*   **The Issue:** Traversing deep database relationships or calling methods inside template loops (e.g. `{% for item in orders %} {{ item.customer.profile.bio }} {% endfor %}`) triggers silent, untracked N+1 query loops on the presentation layer.
*   **Proposed Check:** Scan local template directories (`.html` files, supporting both Jinja2 and Django Templates). Flag any `{% for %}` loops containing second-level traversals (e.g., `item.customer.name` with multiple dots) or method calls.
*   **Recommendation Hint:** Suggest annotating or prefetching the necessary fields in the View before rendering.

### 2. ⚡ Serializer Nested N+1 Watchdog (`warden.W009`)
*   **The Issue:** Nested serializers (in DRF or Django Ninja) trigger automatic database lookups for each row if the corresponding View did not explicitly configure `select_related` or `prefetch_related`.
*   **Proposed Check:** Perform a static syntax analysis on DRF Serializers or Django Ninja schemas. If nested serialization is detected, locate the corresponding view file and verify that its `get_queryset` implementation contains the matching pre-load options.
*   **Recommendation Hint:** Alert and advise adding the specific pre-load option to the queryset.

### 3. 🚨 Transactional Background Task Guard (`warden.W010`)
*   **The Issue:** Dispatching background tasks (e.g., celery `.delay()` or `.apply_async()`) inside active `@transaction.atomic` blocks creates a race condition. The worker might pick up the task and attempt to read the database record before the transaction actually commits, causing `ObjectDoesNotExist` errors.
*   **Proposed Check:** Scan Python source files to detect Celery/task dispatch calls (`.delay()`, `.apply_async()`) made inside transactional code paths (functions decorated with `@transaction.atomic` or blocks within `with transaction.atomic():`).
*   **Recommendation Hint:** Advise wrapping the task call inside `transaction.on_commit(lambda: task.delay())`.

### 🗄️ 4. Dangerous Migration Guard (`warden.W011`)
*   **The Issue:** Running database migrations that alter large tables (such as `RenameField` or adding non-nullable columns without safe defaults) locks the table on high-volume PostgreSQL/MySQL instances, leading to production downtime.
*   **Proposed Check:** Analyze newly created Django migration files. Detect potentially blocking operations and warn about their concurrency risks.
*   **Recommendation Hint:** Recommend a safe, multi-phased backfill and deployment strategy for zero-downtime.

---

## 🛠️ How to Contribute to the Roadmap

If you are interested in picking up any of these roadmap items:
1. Review the [Contributing Guidelines](./CONTRIBUTING.md) to understand our coding standards (McCabe < 10, 100% test coverage SLA).
2. Open an issue on GitHub to discuss your proposed implementation strategy.
3. Submit a pull request referencing the issue!
