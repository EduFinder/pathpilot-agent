from dataclasses import dataclass
from typing import Optional

@dataclass
class Student:
    name: str
    email: str
    resume_url: str
    id: Optional[str] = None
    created_at: Optional[str] = None

    def to_dict(self):
        return {
            "name": self.name,
            "email": self.email,
            "resume_url": self.resume_url
        }
