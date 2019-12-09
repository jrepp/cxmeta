import uuid


def random_name():
    """
    Return the last part of a UUID
    """
    return str(uuid.uuid4()).split('-')[-1]
