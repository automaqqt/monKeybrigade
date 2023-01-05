from sqlmodel import Field, SQLModel


class Work(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    block_time: str
    venue_id: str
    mnky: bool
    venue_owner: str
    user: str

class DropBase(SQLModel):
    handle: str
    type: str
    state: str
    issue_time: str
    day: str
    hour: int
    winners: str
    trx_id: str


class Drop(DropBase, table=True):
    id: int = Field(default=None, primary_key=True)


class DropCreate(DropBase):
    pass
