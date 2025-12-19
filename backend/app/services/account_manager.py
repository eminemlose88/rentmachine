from ..db.crud import crud
from ..db.models import Account, AccountStatus, LogLevel, SystemLog
import random

class AccountManager:
    async def get_available_account(self, region: str = "us-east-1") -> Account:
        """
        Finds an active account with quota in the specified region.
        For now, simplistic logic: fetch all active, filter by region locally (or in query), pick one.
        """
        # In a real app, optimize query to filter by region inside DB
        accounts = await crud.get_active_accounts()
        
        # Filter by region
        available = [acc for acc in accounts if region in acc.regions]
        
        if not available:
            return None
            
        # Strategy: Random load balancing
        return random.choice(available)

    async def mark_account_dead(self, account_id: str, reason: str):
        await crud.update_account_status(account_id, AccountStatus.DEAD)
        await crud.log_event(SystemLog(
            level=LogLevel.ERROR,
            message=f"Account {account_id} marked DEAD. Reason: {reason}",
            metadata={"account_id": account_id}
        ))

account_manager = AccountManager()
