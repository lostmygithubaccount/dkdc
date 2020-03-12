import json
import subprocess
import logging

from utils import run_command
from datetime import datetime, timedelta


module_logger = logging.getLogger(__name__)


def blob_upload(container, name, file, accountname):
    return run_command(["az",
                        "storage",
                        "blob",
                        "upload",
                        "-c",
                        container,
                        "-f",
                        file,
                        "-n",
                        name,
                        "--account-name",
                        accountname], shell=True)


def set_account(subscription):
    return run_command(["az", "account", "set", "-s", subscription], shell=True)


def list_blobs(accountname, container, prefix, output="json"):
    return run_command(["az",
                        "storage",
                        "blob",
                        "list",
                        "--account-name",
                        accountname,
                        "-c",
                        container,
                        "--prefix",
                        prefix,
                        "-o",
                        output], shell=True, stream_stdout=False, return_stdout=True)


def generate_sas(accountname, container, name, permissions="r",
                 expiry=(datetime.utcnow() + timedelta(days=365)).strftime("%Y-%m-%dT%H:%MZ")):

    return run_command(["az",
                        "storage",
                        "blob",
                        "generate-sas",
                        "--container-name",
                        container,
                        "--name",
                        name,
                        "--account-name",
                        accountname,
                        "--permissions",
                        permissions,
                        "--expiry",
                        expiry], shell=True, stream_stdout=False, return_stdout=True)


def get_secret_from_common_keyvault(secret_name):
    """
    Gets the specified secret from the common keyvault

    :param secret_name: the secret name
    :type secret_name: str
    :return: the secret value
    :rtype: str
    """

    common_keyvault_name = "vienna-test-westus"
    return get_secret_from_keyvault(common_keyvault_name, secret_name)


def get_secret_from_keyvault(vault_name, secret_name):
    """
    Gets the specified secret from the specified keyvault

    :param vault_name: the keyvault name
    :type vault_name: str
    :param secret_name: the secret name
    :type secret_name: str
    :return: the secret value
    :rtype: str
    """

    args = [
        "az",
        "keyvault",
        "secret",
        "show",
        "--vault-name",
        vault_name,
        "--name",
        secret_name
    ]

    try:
        output = run_command(args, shell=True, stream_stdout=False, return_stdout=True)
        parsed = json.loads(output)
        return parsed["value"]
    except subprocess.CalledProcessError as e:
        module_logger.error("Failed to get secret.\nCommand: {}\nReturn Code: {}\nStdout: {}\nStderr: {}".format(
            e.cmd,
            e.returncode,
            e.output,
            e.stderr
        ))
        raise e
    except json.JSONDecodeError as e:
        module_logger.error("Unable to decode json.\nContent: {}".format(e.doc))
        raise e
