from enum import Enum

class SCPClassEnum(str, Enum):
    Safe = "Safe"
    Euclid = "Euclid"
    Keter = "Keter"
    Thaumiel = "Thaumiel"
    Apollyon = "Apollyon"
    Archon = "Archon"
    Neutralized = "Neutralized"
    Explained = "Explained"
    Pending = "Pending"