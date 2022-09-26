import os
import sys

import dotenv
import fabric
import invoke
import patchwork.files

dotenv.load_dotenv()

# The directory where the application sources will be stored
APPLICATION_DIRECTORY = '~/fuelpricesgr'

# The git repository
GIT_REPOSITORY = 'https://github.com/mavroprovato/fuelpricesgr.git'


@fabric.task
def deploy(context):
    """Perform the deployment.

    :param context: The context.
    """
    deploy_api(context)
    deploy_frontend(context)


@fabric.task
def deploy_api(context):
    """Deploy the API.

    :param context: The context.
    """
    print(f"Performing deployment on host {context.host} as user {context.user}")
    # Create the application directory if it does not exist
    if patchwork.files.exists(context, APPLICATION_DIRECTORY):
        print("Application directory exists")
    else:
        context.run(f'mkdir {APPLICATION_DIRECTORY}')
    with context.cd(APPLICATION_DIRECTORY):
        # Update the git repository
        if patchwork.files.exists(context, '~/fuelpricesgr/.git'):
            print("Git repository exists, updating code")
            context.run(f'git pull origin master')
        else:
            print("Does not exist, cloning the repository")
            context.run(f'git clone -b {GIT_REPOSITORY}')
        # Install the python dependencies
        print("Installing python dependencies")
        context.run('~/.local/bin/poetry install --no-dev --remove-untracked')
    # Restart the server
    print("Restarting the server")
    context.run('sudo systemctl restart fuelpricesgr.service')


@fabric.task
def deploy_frontend(context):
    """Deploy the frontend.

    :param context: The context.
    """
    print("Building the frontend")
    invoke.run('npm run build --prefix frontend')
    if 'FRONTEND_BUCKET' not in os.environ:
        sys.exit("'FRONTEND_BUCKET' is not defined, cannot deploy frontend")

    invoke.run(f"aws s3 sync frontend/dist/ s3://{os.environ['FRONTEND_BUCKET']} --acl public-read")
