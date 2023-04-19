"""
Arquivo principal do bot Daedalus.

O setup inicial é todo feito no módulo core.startup.
--
Autor: Leonardo Valim

Licenciado sob a MIT License.
"""


from sqlalchemy.orm import close_all_sessions

from core.startup import main
from core.utils import daedalus


if __name__ == "__main__":
    main(daedalus['token'])
    close_all_sessions()
    print('Bye')
