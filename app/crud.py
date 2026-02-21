import os
import ssl
from dotenv import load_dotenv
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import Column, String, Float, select, update, delete
from sqlalchemy.orm import declarative_base
from typing import List, Dict
import uuid

# Load env from parent directory
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

DATABASE_URL = os.getenv("DATABASE_URL")

# Create SSL context for asyncpg
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"ssl": ssl_context},
    pool_pre_ping=True
)

async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()


class Item(Base):
    __tablename__ = "items"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def create_item(item: dict) -> dict:
    async with async_session_maker() as session:
        try:
            new_item = Item(
                id=item.get("id", str(uuid.uuid4())),
                name=item["name"],
                price=item["price"]
            )
            session.add(new_item)
            await session.commit()
            await session.refresh(new_item)
            return {"id": new_item.id, "name": new_item.name, "price": new_item.price}
        except Exception:
            await session.rollback()
            raise


async def read_items() -> List[dict]:
    async with async_session_maker() as session:
        try:
            result = await session.execute(select(Item))
            items = result.scalars().all()
            return [{"id": i.id, "name": i.name, "price": i.price} for i in items]
        except Exception:
            await session.rollback()
            raise


async def update_item(item_id: str, new_data: dict) -> dict:
    async with async_session_maker() as session:
        try:
            result = await session.execute(select(Item).where(Item.id == item_id))
            item = result.scalar_one_or_none()
            if not item:
                raise ValueError(f"Item with ID {item_id} not found")
            
            item.name = new_data["name"]
            item.price = new_data["price"]
            await session.commit()
            await session.refresh(item)
            return {"id": item.id, "name": item.name, "price": item.price}
        except Exception:
            await session.rollback()
            raise


async def delete_item(item_id: str) -> dict:
    async with async_session_maker() as session:
        try:
            result = await session.execute(select(Item).where(Item.id == item_id))
            item = result.scalar_one_or_none()
            if not item:
                raise ValueError(f"Item with ID {item_id} not found")
            
            await session.delete(item)
            await session.commit()
            return {"id": item.id, "name": item.name, "price": item.price}
        except Exception:
            await session.rollback()
            raise


async def dispose_engine():
    await engine.dispose()
