from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from app import app, db
from seed.seed import seed_all

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


@manager.command
def seed():
  seed_all()


if __name__ == '__main__':
  manager.run()
