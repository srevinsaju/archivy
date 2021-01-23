from functools import update_wrapper
from pathlib import Path
from os import environ

from click import Context
from flask_compress import Compress
from pkg_resources import iter_entry_points

import click
from click_plugins import with_plugins
from flask.cli import FlaskGroup, load_dotenv, shell_command, with_appcontext

from archivy.config import ArchivyConfig
from archivy.click_web import create_click_web_app
from archivy.data import open_file, format_file, unformat_file
from archivy.main import ArchivyFlaskApp
from archivy.models import User, DataObj


class ArchivyCommandLineFlaskGroup(FlaskGroup):
    def __init__(self, **kwargs):
        self._archivy_flask_app = ArchivyFlaskApp()
        self._archivy_flask_app.bootstrap_search()
        self._archivy_flask_app.bootstrap_login()
        self._archivy_flask_app.bootstrap_routes()
        Compress(self._archivy_flask_app)

        @self._archivy_flask_app.template_filter("pluralize")
        def pluralize(number, singular="", plural="s"):
            if number == 1:
                return singular
            else:
                return plural
        super().__init__(**kwargs, create_app=self.archivy)

    def archivy(self, script_info):
        return self._archivy_flask_app

    def command(self, *args, **kwargs):
        """This works exactly like the method of the same name on a regular
        :class:`click.Group` but it wraps callbacks in :func:`with_appcontext`
        unless it's disabled by passing ``with_appcontext=False``.
        """
        wrap_for_ctx = kwargs.pop("with_appcontext", True)
        wrap_for_archivy = kwargs.pop("with_archivy", False)

        def decorator(f):
            if wrap_for_ctx:
                f = with_appcontext(f)

            if wrap_for_archivy:
                archivy = self._archivy_flask_app
                f = with_archivy(f)
            return click.Group.command(self, *args, **kwargs)(f)

        return decorator

    def pass_archivy(self, f):
        """Marks a callback as wanting to receive the current context
        object as first argument.
        """

        def new_func(*args, **kwargs):
            return f(self._archivy_flask_app, *args, **kwargs)

        return update_wrapper(new_func, f)


@with_plugins(iter_entry_points("archivy.plugins"))
@click.group(cls=ArchivyCommandLineFlaskGroup)
def cli():
    pass


# add built in commands:
cli.add_command(shell_command)


@cli.command(
    "init", short_help="Initialise your archivy application"
)
@cli.pass_archivy
def init(ctx):
    pass


@cli.command("config", short_help="Open archivy config.")
def config():
    open_file(str(Path(app.config["INTERNAL_DIR"]) / "config.yml"))


@cli.command("hooks", short_help="Creates hook file if it is not setup and opens it.")
def hooks():
    hook_path = Path(app.config["USER_DIR"]) / "hooks.py"
    if not hook_path.exists():
        with hook_path.open("w") as f:
            f.write(
                "from archivy.config import BaseHooks\n"
                "class Hooks(BaseHooks):\n"
                "   # see available hooks at https://archivy.github.io/reference/hooks/\n"
                "   def on_dataobj_create(self, dataobj): # for example\n"
                "       pass"
            )
    open_file(hook_path)


@cli.command("run", short_help="Runs archivy web application")
@cli.pass_archivy
def run(app):
    click.echo("Running archivy...")
    load_dotenv()
    environ["FLASK_RUN_FROM_CLI"] = "false"
    app_with_cli = create_click_web_app(click, cli, app)
    app_with_cli.run(host=app.config["HOST"], port=app.config["PORT"])


@cli.command(short_help="Creates a new admin user")
@click.argument("username")
@click.password_option()
def create_admin(username, password):
    if len(password) < 8:
        click.echo("Password length too short")
        return False
    else:
        user = User(username=username, password=password, is_admin=True)
        if user.insert():
            click.echo(f"User {username} successfully created.")
            return True
        else:
            click.echo("User with given username already exists.")
            return False


@cli.command(short_help="Format normal markdown files for archivy.")
@click.argument("filenames", type=click.Path(exists=True), nargs=-1)
def format(filenames):
    for path in filenames:
        format_file(path)


@cli.command(short_help="Convert archivy-formatted files back to normal markdown.")
@click.argument("filenames", type=click.Path(exists=True), nargs=-1)
@click.argument("output_dir", type=click.Path(exists=True, file_okay=False))
def unformat(filenames, output_dir):
    for path in filenames:
        unformat_file(path, output_dir)


@cli.command(short_help="Sync content to Elasticsearch")
def index():
    data_dir = Path(app.config["USER_DIR"]) / "data"

    if not app.config["SEARCH_CONF"]["enabled"]:
        click.echo("Search must be enabled for this command.")
        return

    for filename in data_dir.rglob("*.md"):
        cur_file = open(filename)
        dataobj = DataObj.from_md(cur_file.read())
        cur_file.close()

        if dataobj.index():
            click.echo(f"Indexed {dataobj.title}...")
        else:
            click.echo(f"Failed to index {dataobj.title}")


if __name__ == "__main__":
    cli()
