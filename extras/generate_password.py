from werkzeug.security import generate_password_hash

def generate_password(password):
    hash_password = generate_password_hash(str(password))
    return hash_password

print(generate_password("admin"))