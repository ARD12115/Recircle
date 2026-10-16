"""
Database Seed - Demo users, topology, history
"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User, UserRole
from app.models.twin import TwinNode, TwinEdge
from app.core.security import get_password_hash
from app.services.twin.graph import load_twin_seed


async def seed_database(db: AsyncSession) -> None:
    """Seed database with demo data."""
    
    # Demo users
    demo_users = [
        {"email": "resident@demo.recircle", "password": "demo123", "role": UserRole.RESIDENT, "name": "Demo Resident"},
        {"email": "manager@demo.recircle", "password": "demo123", "role": UserRole.MANAGER, "name": "Demo Manager"},
        {"email": "admin@demo.recircle", "password": "demo123", "role": UserRole.ADMIN, "name": "Demo Admin"},
    ]
    
    for user_data in demo_users:
        result = await db.execute(select(User).where(User.email == user_data["email"]))
        if not result.scalar_one_or_none():
            user = User(
                email=user_data["email"],
                password_hash=get_password_hash(user_data["password"]),
                role=user_data["role"],
                name=user_data["name"],
                is_demo=True,
            )
            db.add(user)
    
    # Seed twin topology
    seed = load_twin_seed()
    
    for node_data in seed["nodes"]:
        result = await db.execute(select(TwinNode).where(TwinNode.id == node_data["id"]))
        if not result.scalar_one_or_none():
            node = TwinNode(
                id=node_data["id"],
                type=node_data["type"],
                name=node_data["name"],
                config_json=node_data["config"],
            )
            db.add(node)
    
    for edge_data in seed["edges"]:
        result = await db.execute(
            select(TwinEdge).where(
                TwinEdge.from_id == edge_data["from_id"],
                TwinEdge.to_id == edge_data["to_id"],
            )
        )
        if not result.scalar_one_or_none():
            edge = TwinEdge(
                from_id=edge_data["from_id"],
                to_id=edge_data["to_id"],
                weight=edge_data["weight"],
                route_prob=edge_data["route_prob"],
            )
            db.add(edge)
    
    await db.commit()
    print("Database seeded successfully")


if __name__ == "__main__":
    from app.db.session import async_session_maker, init_db
    
    async def main():
        await init_db()
        async with async_session_maker() as db:
            await seed_database(db)
    
    asyncio.run(main())