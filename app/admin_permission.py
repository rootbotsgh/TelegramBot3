from config import ADMIN_USER_ID
# === PERMISSION CHECK ===
def is_admin(user_id):
    return user_id == ADMIN_USER_ID