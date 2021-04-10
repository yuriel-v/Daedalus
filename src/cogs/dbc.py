from discord.ext import commands


class DaedalusBaseCog(commands.Cog):
    def __init__(self):
        self._help_info = ''
        self._prefix = ''

    def cog_info(self, command=None) -> str:
        if command is not None and str(command).lower() in self.cmds.keys():
            reply = f'-- {self._prefix + (" " if self._prefix else "")}{str(command).lower()} --\n' + self.cmds[str(command)].help
        else:
            reply = '\n'.join([x.strip() for x in self._help_info.split('\n')]).strip()

        return reply
