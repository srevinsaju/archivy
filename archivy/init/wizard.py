import os
from pathlib import Path

import click
from click import Context

from archivy.config import ArchivyConfig
from archivy.main import ArchivyFlaskApp


class Wizard:
    def __init__(self, ctx: Context):
        self.app = ArchivyFlaskApp()
        self.config = ArchivyConfig()
        self._ctx = ctx

    def pre_init_checks(self):
        if self.config.exists():
            click.confirm(
                "ArchivyConfig already found. Do you wish to reset it? "
                "Otherwise run `archivy config`",
                abort=True,
            )
        try:
            users_db = (Path(self.config["INTERNAL_DIR"]) / "db.json").resolve(strict=True)
            remove_old_users = click.confirm(
                "Found an existing user database. Do you want to remove them?"
            )
            if remove_old_users:
                users_db.unlink()
        except FileNotFoundError:
            pass

    def get_search_backend(self):
        es_enabled = click.confirm(
            "Would you like to enable Elasticsearch? For this to work "
            "when you run archivy, you must have ES installed."
            "See https://archivy.github.io/setup-search/ for more info."
        )
        if es_enabled:
            self.config.SEARCH_CONF["enabled"] = 1
        else:
            delattr(self.config, "SEARCH_CONF")

    def clear_old_secret_key(self):
        delattr(self.config, "SECRET_KEY")

    def create_new_admin(self, create_admin):
        click.echo("Enter the credentials for admin:")
        username = click.prompt("Username")
        password = click.prompt("Password", hide_input=True, confirmation_prompt=True)
        if not self._ctx.invoke(create_admin, username=username, password=password):
            return

    def create_multiple_admin(self, create_admin):
        self.create_new_admin(create_admin)
        create_new_user = click.confirm("Create another admin user?")
        if create_new_user:
            self.create_multiple_admin(create_admin)

    def get_data_dir(self):
        data_dir = click.prompt(
            "Enter the full path of the " "directory where you'd like us to store data.",
            type=Path,
            default=str(Path(".").resolve()),
        )
        (data_dir / "data").mkdir(exist_ok=True, parents=True)
        self.config["USER_DIR"] = str(data_dir)

    def get_host(self):
        self.config["HOST"] = click.prompt(
            "Host [localhost (127.0.0.1)]",
            type=str,
            default="127.0.0.1",
            show_default=False,
        )

    def get_port(self):
        self.config["PORT"] = click.prompt(
            "Port",
            type=int,
            default="17171",
            show_default=True,
        )

    def on_complete(self):
        # ask if to remove old users

        # remove the old configuration, and add version to it

        click.echo("This is the archivy installation initialization wizard.")

        # create data dir

        self.config.override()




        write_config(vars(config))
        click.echo(
            "ArchivyConfig successfully created at "
            + str((Path(self.config["INTERNAL_DIR"]) / "config.yml").resolve())
        )