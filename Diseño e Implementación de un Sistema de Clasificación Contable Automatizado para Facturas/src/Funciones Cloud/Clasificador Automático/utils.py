"""
Checks if a significant coincidence exists between a word and a description.

Args:
    word (str): The word to be checked for coincidence.
    description (str): The description to search for the word.
    minimum_porcentage (float, optional): The minimum percentage of characters that must match between the word and the description to consider it a significant coincidence. Defaults to 0.8.

Returns:
    bool: True if a significant coincidence is found, False otherwise.
"""
def significativeCoincidence(word: str, description: str, minimum_percentage=0.8) -> bool:
    word_length = len(word)
    threshold = int(minimum_percentage * word_length)
    for i in range(len(description) - word_length + 1):
        if sum(1 for x, y in zip(description[i:i+word_length], word) if x == y) >= threshold:
            return True
    return False




"""
Checks if a set of key words are present in a description with high confidence.

Args:
    key_words (list of str): The list of key words to check for in the description.
    description (str): The description to search for the key words.

Returns:
    bool: True if a high percentage of the key words are found in the description, False otherwise.
"""
def checkKeyWords(key_words: list, description: str) -> bool:
    if not key_words:  # Checking if the list is empty at the beginning
        return False

    total_words = len(key_words)
    coincidences = sum(1 for word in key_words if significativeCoincidence(word, description))
    
    return coincidences / total_words >= 0.95


__all__ = [checkKeyWords]