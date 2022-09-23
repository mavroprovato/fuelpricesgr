import fabric
import patchwork.files

# The directory where the application sources will be stored
APPLICATION_DIRECTORY = '~/fuelpricesgr'

# The git repository
GIT_REPOSITORY = 'https://github.com/mavroprovato/fuelpricesgr.git'


@fabric.task
def deploy(c):
    """Perform the deployment.

    :param c: The fabric connection.
    """
    print(f"Performing deployment on host {c.host} as user {c.user}")
    # Create the application directory if it does not exist
    if patchwork.files.exists(c, APPLICATION_DIRECTORY):
        print("Application directory exists")
    else:
        c.run(f'mkdir {APPLICATION_DIRECTORY}')
    with c.cd(APPLICATION_DIRECTORY):
        # Update the git repository
        if patchwork.files.exists(c, '~/fuelpricesgr/.git'):
            print("Git repository exists, updating code")
            c.run(f'git pull origin master')
        else:
            print("Does not exist, cloning the repository")
            c.run(f'git clone -b {GIT_REPOSITORY}')
        # Install the python dependencies
        print("Installing python dependencies")
        c.run('~/.local/bin/poetry install --no-dev')

    # Restart the server
    print("Restarting the server")
    c.run('sudo systemctl restart fuelpricesgr.service')
