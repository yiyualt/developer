"""CallbackMixin — shared _fire implementation for callback-enabled components.

Every component that supports callbacks previously duplicated the same
_fire logic. CallbackMixin provides it once as a reusable base.
"""

from typing import List

from langchain.callbacks.base import CallbackHandler


class CallbackMixin:
    """Mixin that provides a shared ``_fire`` method for callback dispatch.

    Classes that accept ``callbacks`` should inherit this mixin and set
    ``self.callbacks`` in ``__init__``. The ``_fire`` method iterates
    all registered handlers and invokes the matching event method.

    Usage::

        class MyComponent(CallbackMixin):
            def __init__(self, callbacks=None):
                self.callbacks = callbacks or []

            def do_something(self):
                self._fire("on_llm_start", prompt="hello")
    """

    callbacks: List[CallbackHandler]

    def _fire(self, event: str, **kwargs) -> None:
        """Invoke an event on all registered callback handlers.

        Args:
            event: The handler method name (e.g. ``"on_llm_start"``).
            **kwargs: Arguments passed to the handler method.
        """
        for handler in self.callbacks:
            getattr(handler, event)(**kwargs)
