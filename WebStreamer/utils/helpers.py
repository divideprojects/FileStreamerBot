from secrets import token_urlsafe


def extract_user_id_from_random_link(random_link: str) -> int:
    """Extract user_id from random_link

    Args:
        random_link (str): Random link

    Returns:
        int: User ID
    """
    return int(random_link[3:-4])


def generate_random_url(user_id: int) -> str:
    """Generate random url

    Args:
        user_id (int): User ID

    Returns:
        str: Random url
    """
    return token_urlsafe(2) + str(user_id) + token_urlsafe(3)
