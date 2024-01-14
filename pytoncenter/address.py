class Address:
    def __init__(self, any_form_addr: str):
        pass
    
    @property
    def workchain(self) -> int:
        return 0
    
    @property
    def hash_part(self) -> bytearray:
        return ""
    
    @property
    def is_test_only(self) -> bool:
        return False
    
    @property
    def is_user_friendly(self) -> bool:
        return False
    
    @property
    def is_bounceable(self) -> bool:
        return False
    
    @property
    def is_url_safe(self) -> bool:
        return False
    
    def to_string(self) -> str:
        return ""