def extract_user_id_from_random_link(random_link: str) -> int:
    """Extract user_id from random_link

    Args:
        random_link (str): Random link

    Returns:
        int: User ID
    """
    return int(random_link[3:-4])
