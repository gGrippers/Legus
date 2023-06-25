from databases import Database

async def create_room_table(database: Database):
    query = """
    CREATE TABLE IF NOT EXISTS rooms (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        max_players INTEGER NOT NULL,
        password TEXT,
        current_players INTEGER DEFAULT 0
    );
    """
    await database.execute(query)