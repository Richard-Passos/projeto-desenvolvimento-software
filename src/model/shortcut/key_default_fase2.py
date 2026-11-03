"""Atalhos musicais padrão da fase 2.

Este módulo contém somente a definição declarativa dos símbolos aceitos pelo
editor musical. A interpretação dos símbolos continua sendo responsabilidade
das regras do modelo e o encaminhamento dos eventos continua sendo
responsabilidade do controller.
"""


class KeyDefaultFase2:
    """Catálogo dos atalhos musicais obrigatórios da fase 2."""

    NOTAS: tuple[str, ...] = ("A", "B", "C", "D", "E", "F", "G")
    ACIDENTES: tuple[str, ...] = ("#", "b")
    DURACOES: tuple[str, ...] = (
        ":1",
        ":2",
        ":3",
        ":4",
        ":5",
        ":6",
        ":7",
    )
    PAUSA: tuple[str, ...] = ("[", "]")
    OITAVAS: tuple[str, ...] = ("V", "?")
    BPM: tuple[str, ...] = ("<", ">")

    @classmethod
    def todos(cls) -> tuple[str, ...]:
        """Retorna todos os símbolos na ordem em que aparecem no teclado."""
        return (
            *cls.NOTAS,
            *cls.ACIDENTES,
            *cls.DURACOES,
            *cls.PAUSA,
            *cls.OITAVAS,
            *cls.BPM,
        )
