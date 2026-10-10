from ErisPulse.Core.Bases import Field, Model


class CommandCall(Model):

    __tablename__ = "gov_command_calls"

    id: int = Field(primary_key=True, autoincrement=True)
    ts: float = Field(index=True)
    command: str = Field(max_length=128, index=True)
    platform: str = Field(max_length=64, default="")
    user_id: str = Field(max_length=128, default="", index=True)
    success: bool = Field(default=True)
    error: str = Field(max_length=255, default="")


class BlockEvent(Model):

    __tablename__ = "gov_block_events"

    id: int = Field(primary_key=True, autoincrement=True)
    ts: float = Field(index=True)
    source: str = Field(max_length=16, choices=["middleware", "scope"], index=True)
    middleware: str = Field(max_length=128, default="")
    dimension: str = Field(max_length=16, default="")
    module: str = Field(max_length=128, default="")
    platform: str = Field(max_length=64, default="")
    detail_type: str = Field(max_length=64, default="")
    user_id: str = Field(max_length=128, default="")
    session_id: str = Field(max_length=128, default="")
