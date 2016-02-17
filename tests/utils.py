from functools import wraps

from django.conf import UserSettingsHolder, settings
try:
    from django.test.signals import setting_changed
except ImportError:
    setting_changed = None


# This was taken from django 1.9 django.tests.utils, and adapted to be 
# compatible with a wider range of django versions.
class override_settings(object):
    """
    Acts as either a decorator, or a context manager. If it's a decorator it
    takes a function and returns a wrapped function. If it's a contextmanager
    it's used with the ``with`` statement. In either event entering/exiting
    are called before and after, respectively, the function/block is executed.
    """
    def __init__(self, **kwargs):
        self.options = kwargs

    def __enter__(self):
        self.enable()

    def __exit__(self, exc_type, exc_value, traceback):
        self.disable()

    def __call__(self, test_func):
        @wraps(test_func)
        def inner(*args, **kwargs):
            with self:
                return test_func(*args, **kwargs)
        return inner

    def save_options(self, test_func):
        if test_func._overridden_settings is None:
            test_func._overridden_settings = self.options
        else:
            # Duplicate dict to prevent subclasses from altering their parent.
            test_func._overridden_settings = dict(
                test_func._overridden_settings, **self.options)

    def enable(self):
        # Changing installed apps cannot be done in a backward-compatible way
        assert 'INSTALLED_APPS' not in self.options

        override = UserSettingsHolder(settings._wrapped)
        for key, new_value in self.options.items():
            setattr(override, key, new_value)
        self.wrapped = settings._wrapped
        settings._wrapped = override
        for key, new_value in self.options.items():
            if setting_changed:
                setting_changed.send(sender=settings._wrapped.__class__,
                                     setting=key, value=new_value, enter=True)

    def disable(self):
        settings._wrapped = self.wrapped
        del self.wrapped
        for key in self.options:
            new_value = getattr(settings, key, None)
            if setting_changed:
                setting_changed.send(sender=settings._wrapped.__class__,
                                     setting=key, value=new_value, enter=False)
