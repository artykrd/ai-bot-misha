"""
AI Request repository for managing AI request records.
"""
from typing import List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.ai_request import AIRequest
from app.database.repositories.base import BaseRepository


class AIRequestRepository(BaseRepository[AIRequest]):
    """Repository for AI Request operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(AIRequest, session)

    async def get_by_id(self, request_id: int) -> Optional[AIRequest]:
        """Get AI request by ID."""
        return await self.get(request_id)

    async def get_user_requests(
        self,
        user_id: int,
        limit: Optional[int] = 50,
        offset: Optional[int] = 0,
        request_type: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[AIRequest]:
        """
        Get AI requests for a user.

        Args:
            user_id: User ID
            limit: Maximum number of requests to return
            offset: Offset for pagination
            request_type: Optional filter by request type (text, image, video)
            status: Optional filter by status (pending, completed, failed)

        Returns:
            List of AI requests
        """
        query = select(AIRequest).where(AIRequest.user_id == user_id)

        if request_type:
            query = query.where(AIRequest.request_type == request_type)

        if status:
            query = query.where(AIRequest.status == status)

        query = query.order_by(desc(AIRequest.created_at))

        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_user_total_spent(self, user_id: int) -> int:
        """
        Get total tokens spent by user.

        Args:
            user_id: User ID

        Returns:
            Total tokens spent
        """
        from sqlalchemy import func

        result = await self.session.execute(
            select(func.sum(AIRequest.tokens_cost))
            .where(AIRequest.user_id == user_id)
            .where(AIRequest.status == "completed")
        )
        total = result.scalar_one_or_none()
        return total if total is not None else 0

    async def get_model_usage_stats(self, user_id: int) -> dict:
        """
        Get model usage statistics for a user.

        Args:
            user_id: User ID

        Returns:
            Dictionary with model usage stats
        """
        from sqlalchemy import func

        result = await self.session.execute(
            select(
                AIRequest.ai_model,
                func.count(AIRequest.id).label("request_count"),
                func.sum(AIRequest.tokens_cost).label("total_tokens"),
            )
            .where(AIRequest.user_id == user_id)
            .where(AIRequest.status == "completed")
            .group_by(AIRequest.ai_model)
        )

        stats = {}
        for row in result:
            stats[row.ai_model] = {
                "request_count": row.request_count,
                "total_tokens": row.total_tokens if row.total_tokens else 0,
            }

        return stats
