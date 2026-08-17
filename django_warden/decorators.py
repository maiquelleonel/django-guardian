import functools
import logging

logger = logging.getLogger("django_guardian")


def prevent_windmill_loops(signal_type=None):
    """
    Decorator to protect signal receivers against infinite recursion loops.
    Ensures that if the signal receiver is triggered within its own call stack for the same instance,
    it exits early to avoid Windmill Loops.
    """

    def decorator(func):
        # Keep track of active invocations locally using a thread-safe approach or simple set
        func._active_instances = set()

        @functools.wraps(func)
        def wrapper(sender, instance, **kwargs):
            instance_id = id(instance)
            if instance_id in func._active_instances:
                logger.warning(
                    "Recursion blocked in signal '%s' for instance %s of %s",
                    func.__name__,
                    instance_id,
                    sender.__name__,
                )
                return None

            func._active_instances.add(instance_id)
            try:
                return func(sender, instance, **kwargs)
            finally:
                func._active_instances.discard(instance_id)

        return wrapper

    return decorator
