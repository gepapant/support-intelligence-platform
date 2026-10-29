from sqlalchemy import text

from app.db.session import engine


def main():
    if engine.dialect.name != "postgresql":
        print("Skipping PostgreSQL extension setup for non-PostgreSQL database.")
        return

    with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))

    print("pgvector extension is ready.")


if __name__ == "__main__":
    main()
