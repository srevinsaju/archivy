class BaseHooks:
    """
    Class of methods users can inherit to configure and extend archivy with hooks.


    ## Usage:

    Archivy checks for the presence of a `hooks.py` file in the
    user directory that stores the `data/` directory with your notes and bookmarks.
    This location is usually set during `archivy init`.

    Example `hooks.py` file:

    ```python
    from archivy.config import BaseHooks

    class Hooks(BaseHooks):
        def on_edit(self, dataobj):
            print(f"Edit made to {dataobj.title}")

        def before_dataobj_create(self, dataobj):
            from random import randint
            dataobj.content += f"\\nThis note's random number is {randint(1, 10)}"

        # ...
    ```

    If you have ideas for any other hooks you'd find useful if they were supported,
    please open an [issue](https://github.com/archivy/archivy/issues).
    """

    def on_data_object_create(self, data_object):
        """Hook for data_object creation."""
        pass

    def before_data_object_create(self, data_object):
        """Hook called immediately before data_object creation."""
        pass

    def on_user_create(self, user):
        """Hook called after a new user is created."""
        pass

    def on_edit(self, data_object):
        """Hook called whenever a user edits through the web interface or the API."""
