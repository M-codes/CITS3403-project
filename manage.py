from app import create_app, db
from flask_migrate import MigrateCommand
from flask.cli import with_appcontext
import click

app = create_app()

# Optional: create a custom CLI command to init DB
@app.cli.command("init-db")
@with_appcontext
def init_db():
    db.create_all()
    click.echo("Database initialized.")
