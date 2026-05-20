"""Seed deterministic mock users and completed payments.

Run with:
    uv run python scripts/seed_mock_payments.py
"""

import asyncio
from decimal import Decimal
from pathlib import Path
import sys

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert as pg_insert

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.db import AsyncSessionLocal
from app.models.payments import Payment
from app.models.users import Role, User, user_role_association
from app.schemas.payments import PaymentMethod, PaymentStatus


FALLBACK_PASSWORD_HASH = "$2b$12$mockseedplaceholdernotforloginonly0000000000000000000000"

MOCK_PEOPLE = [
    ("Ali", "Karimov"),
    ("Madina", "Rasulova"),
    ("Bekzod", "Tursunov"),
    ("Dilnoza", "Saidova"),
    ("Jasur", "Yuldashev"),
    ("Malika", "Nazarova"),
    ("Aziz", "Sobirov"),
    ("Shahnoza", "Ergasheva"),
    ("Sardor", "Qodirov"),
    ("Nilufar", "Akbarova"),
    ("Timur", "Mansurov"),
    ("Zarina", "Rahimova"),
    ("Rustam", "Ismoilov"),
    ("Sevara", "Hamidova"),
    ("Diyor", "Abdullayev"),
    ("Gulnoza", "Mirzayeva"),
    ("Farrukh", "Muminov"),
]

PAYMENT_METHODS = [
    PaymentMethod.PAYME,
    PaymentMethod.CLICK,
    PaymentMethod.UZUM,
]


def build_amounts() -> list[str]:
    """Create 50 varied amounts from 1,000.00 through 100,000.00."""
    minimum = Decimal("1000.00")
    maximum = Decimal("100000.00")
    step = (maximum - minimum) / Decimal(49)
    return [str((minimum + (step * index)).quantize(Decimal("0.01"))) for index in range(50)]


async def seed_mock_payments() -> None:
    async with AsyncSessionLocal() as db:
        payment_role = await db.scalar(select(Role).where(Role.name == "user"))
        if payment_role is None:
            payment_role = Role(name="user")
            db.add(payment_role)
            await db.flush()

        emails = [f"mock.payer{index:02d}@example.com" for index in range(1, len(MOCK_PEOPLE) + 1)]
        existing_users = await db.scalars(select(User).where(User.email.in_(emails)))
        users_by_email = {user.email: user for user in existing_users}

        password_hash = await db.scalar(select(User.password).limit(1))
        if password_hash is None:
            password_hash = FALLBACK_PASSWORD_HASH

        users: list[User] = []
        for index, (first_name, last_name) in enumerate(MOCK_PEOPLE, start=1):
            email = f"mock.payer{index:02d}@example.com"
            user = users_by_email.get(email)
            if user is None:
                user = User(
                    email=email,
                    password=password_hash,
                    first_name=first_name,
                    last_name=last_name,
                    is_active=True,
                )
                db.add(user)
                users_by_email[email] = user
            else:
                user.first_name = first_name
                user.last_name = last_name
                user.is_active = True
            users.append(user)

        await db.flush()

        for user in users:
            role_insert = pg_insert(user_role_association).values(user_id=user.id, role_id=payment_role.id)
            await db.execute(role_insert.on_conflict_do_nothing(index_elements=["user_id", "role_id"]))

        await db.execute(delete(Payment).where(Payment.user_id.in_([user.id for user in users])))

        amounts = build_amounts()
        payments = []
        for index, amount in enumerate(amounts):
            user = users[index // 3]
            payments.append(
                Payment(
                    user_id=user.id,
                    amount=amount,
                    method=PAYMENT_METHODS[index % len(PAYMENT_METHODS)],
                    status=PaymentStatus.COMPLETED,
                )
            )

        db.add_all(payments)
        await db.commit()

    print(f"Created {len(payments)} completed mock payments for {len(users)} users.")
    print("Each mock user has at most 3 payments.")


if __name__ == "__main__":
    asyncio.run(seed_mock_payments())
