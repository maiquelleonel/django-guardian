import inspect

from django.core.checks import Tags, Warning, register
from django.db.models.signals import post_save, pre_save


@register(Tags.models)
def check_signals_windmill_loops(app_configs, **kwargs):
    """
    Scans registered pre_save and post_save receivers to detect potential
    infinite recursion (Windmill Loops) where a receiver calls .save()
    on the same instance without proper guards.
    """
    warnings = []

    # We inspect receivers of pre_save and post_save signals
    for signal_name, signal in [("pre_save", pre_save), ("post_save", post_save)]:
        for receiver in signal.receivers:
            # receiver is a tuple of (receiver_key, weakref_to_receiver_function)
            receiver_func = receiver[1]() if callable(receiver[1]) else receiver[1]
            if receiver_func is None:
                continue

            try:
                # Inspect the source code of the receiver function if available
                source = inspect.getsource(receiver_func)
            except (TypeError, OSError):
                # Built-in or dynamic functions without accessible source
                continue

            # If the receiver contains '.save(' but doesn't check for 'update_fields',
            # 'created', or use a recursion prevention wrapper, flag it.
            if ".save(" in source:
                has_guard = any(
                    guard in source
                    for guard in ["update_fields", "created", "prevent_windmill_loops", "raw", "kwargs.get('raw')"]
                )
                if not has_guard:
                    func_name = getattr(receiver_func, "__name__", str(receiver_func))
                    module_name = getattr(receiver_func, "__module__", "")
                    warnings.append(
                        Warning(
                            (
                                f"Signal receiver '{func_name}' in '{module_name}' "
                                "calls '.save()' on instance but has no explicit safety guard."
                            ),
                            hint=(
                                "Ensure it has an exit clause (e.g., checks 'created', "
                                "matching state, or uses @prevent_windmill_loops)."
                            ),
                            id="guardian.W002",
                        )
                    )

    return warnings
