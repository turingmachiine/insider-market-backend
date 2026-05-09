from abc import ABC, abstractmethod

from src.profile_service.application.dto import ProfileDTO
from src.profile_service.domain.entities import Profile, UserBalance


class IProfileMapper(ABC):
    @staticmethod
    @abstractmethod
    def to_dto(profile: Profile, balance: UserBalance) -> ProfileDTO:
        pass


class ProfileMapper(IProfileMapper):
    @staticmethod
    def to_dto(profile: Profile, balance: UserBalance) -> ProfileDTO:
        return ProfileDTO(
            id=profile.id,
            user_id=profile.user_id,
            display_name=profile.display_name,
            bio=profile.bio,
            avatar_url=profile.avatar_url,
            favorite_club=profile.favorite_club,
            balance=balance.balance,
            reserved_balance=balance.reserved_balance,
            available_balance=balance.available_balance,
            currency=balance.currency,
            created_at=profile.created_at,
            updated_at=profile.updated_at,
        )
