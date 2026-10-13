from enum import Enum


class UserRole(str, Enum):
    agent = "agent"
    admin = "admin"
