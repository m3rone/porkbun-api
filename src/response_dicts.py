from dataclasses import dataclass

@dataclass
class Ping:
    status: str
    yourIp: str
    xForwardedFor: str
    credentialsValid: bool
    
    @classmethod
    def from_json(cls, mapping: dict[str]):
        return Ping(**mapping)
    
