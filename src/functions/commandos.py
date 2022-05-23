class Commandos:
    def __init__(self) -> None:
        pass

    def all_commands(self)->str:
        return self.commands() + self.admin_commands()

    @staticmethod
    def commands()->str:
        return """

Je hebt de volgende commando's tot je beschikking:

/user → gegevens over je instellingen
/system → Wat systeem gegevens"""

    @staticmethod
    def admin_commands()->str:
        return """
/admin → administrator commandos
/admin_help → Wat help"""