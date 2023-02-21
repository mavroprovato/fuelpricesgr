"""The create user command.
"""
import argparse
import logging

import sqlalchemy.orm

from fuelpricesgr import database


def parse_arguments() -> argparse.Namespace:
    """Parse the command line arguments.

    :return:
    """
    parser = argparse.ArgumentParser(description='Create a user.')
    parser.add_argument('--admin', default=False, action="store_true", help="Set the user as an administrator.")
    parser.add_argument("email", help="The user email")

    return parser.parse_args()


def create_user(db: sqlalchemy.orm.Session, args: argparse.Namespace):
    """Create the user.

    :param db: The database session.
    :param args: The command line arguments.
    """


def main():
    """Creates the user.
    """
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)s %(levelname)s %(message)s')

    # Parse arguments
    args = parse_arguments()

    # Import data
    with database.SessionLocal() as db:
        create_user(db=db, args=args)


if __name__ == '__main__':
    main()
