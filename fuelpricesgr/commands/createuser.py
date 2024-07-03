"""The create user command.
"""
import argparse
import logging
import getpass

from fuelpricesgr import storage


def parse_arguments() -> argparse.Namespace:
    """Parse the command line arguments.

    :return:
    """
    parser = argparse.ArgumentParser(description='Create a user.')
    parser.add_argument('--admin', default=False, action="store_true", help="Set the user as an administrator.")
    parser.add_argument("email", help="The user email")

    return parser.parse_args()


def create_user(args: argparse.Namespace):
    """Create the user.

    :param args: The command line arguments.
    """
    with storage.get_service() as service:
        user_exists = service.user_exists(email=args.email)
        if user_exists:
            raise ValueError(f"User with email {args.email} already exists")

        # Get password
        password1 = getpass.getpass("Password: ")
        password2 = getpass.getpass("Repeat password: ")
        if password1 != password2:
            raise ValueError("Passwords do not match")

        # Create user
        service.create_user(email=args.email, password=password1, admin=args.admin)


def main():
    """Creates the user.
    """
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)s %(levelname)s %(message)s')

    # Parse arguments
    args = parse_arguments()

    # Create user
    create_user(args=args)


if __name__ == '__main__':
    main()
