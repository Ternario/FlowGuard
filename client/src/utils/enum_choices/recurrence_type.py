import enum


class RecurrenceType(str, enum.Enum):
    NONE = 'none'
    DAILY = 'daily'
    WEEKLY = 'weekly'
