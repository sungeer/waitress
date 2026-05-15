from dataclasses import dataclass


@dataclass
class StartupState:
    db_pool_ready: bool = False

    app_started: bool = False  # 代表全部


startup_state = StartupState()
