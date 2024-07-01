import string, random 

def generate_secret_key(key_length: int = 30):
    key_components = list(string.ascii_lowercase) + list(string.ascii_uppercase) + list(range(0, 10)) + [character for character in list(string.punctuation) if (character not in ["(", ")", "[", "]", "\\"])]
    output_string  = ""

    for _ in range(key_length):
        output_string += str(random.choice(key_components))

    return output_string 

SECRET_KEY = generate_secret_key()
