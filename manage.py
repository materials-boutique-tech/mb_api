from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from seed.seed import seed_all

from app import app, db

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


@manager.command
def seed():
  seed_all()


if __name__ == '__main__':
  manager.run()
