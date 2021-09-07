"""Stores context and chat history for a single exchange."""

from datetime import datetime
from typing import List

from tinydb.database import TinyDB

from higgins import const
from higgins.database import tiny
from dataclasses import asdict, dataclass, field

EPISODE_TABLE_NAME = "episodes"


@dataclass
class Context:
    active_window: str = None
    running_applications: List[str] = field(default_factory=list)


@dataclass
class Episode:
    chat_text: str
    context: Context = None
    start_time: str = field(default_factory=lambda: datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))


def save_episode(chat_history: List[str], db: TinyDB, dump_to_jsonl: bool = True):
    chat_text = " ".join(chat_history)
    records = tiny.query(EPISODE_TABLE_NAME, "chat_text", chat_text, db)
    if len(records) > 0:  # Avoid duplicates, like intros, wakeup words
        pass  # print("Found duplicate chat text in database. Ignoring.")
    else:
        episode = Episode(chat_text=chat_text)
        tiny.insert(EPISODE_TABLE_NAME, records=[asdict(episode)], db=db)
    table = db.table(EPISODE_TABLE_NAME)
    # print(f"There are {len(table)} episodes in database!")
    if dump_to_jsonl:
        tiny.export_openai_jsonl(
            table_name=EPISODE_TABLE_NAME,
            field_name="chat_text",
            db=db,
            export_path=const.EPISODE_JSONL_PATH,
        )


if __name__ == "__main__":
    context = Context(active_window="Google Chrome")
    episode = Episode(context=context, chat_text="Brendan: Hello. Higgins: How can I help you?")
    print(episode)
    print(asdict(episode))

    chat_history = [
        "Brendan: Message Leeman 'Yo man' on WhatsApp",
        "Higgins: No contacts found for Leeman. Who do you mean?",
        "Brendan: Bill Jack",
        "Higgins: Is 'Leeman' an alias for 'Bill Jack'?",
        "Brendan: Yes",
    ]
    db = tiny.load_database()
    save_episode(chat_history, db)
