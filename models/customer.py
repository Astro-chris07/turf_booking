class Customer:
    def __init__(self, id, username, password, is_admin=False):
        self.id = id
        self.username = username
        self.password = password  # Consider hashing this before storing!
        self.is_admin = is_admin

    def __repr__(self):
        return f"<Customer {self.username}>"

    def is_admin_user(self):
        return self.is_admin
