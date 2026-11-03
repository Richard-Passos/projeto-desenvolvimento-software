"""LISTA TEMPORÁRIA DE INSTRUMENTOS PARA O PROTÓTIPO VISUAL.

ATENÇÃO:
    Este arquivo existe somente para a calibração da UI. A lista oficial deve
    substituir este módulo quando a equipe responsável por model/service/infra
    definir a fonte de dados dos instrumentos General MIDI.

Os números MIDI abaixo usam a numeração de programa General MIDI iniciando em
1, conforme os rótulos exibidos na imagem estática.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class InstrumentoTemporario:
    nome: str
    midi: int
    categoria: str


# SUBSTITUIR ESTA TUPLA PELA LISTA OFICIAL POSTERIORMENTE.
INSTRUMENTOS_TEMPORARIOS = (
    InstrumentoTemporario("Acoustic Grand Piano", 1, "Pianos"),
    InstrumentoTemporario("Bright Acoustic Piano", 2, "Pianos"),
    InstrumentoTemporario("Electric Grand Piano", 3, "Pianos"),
    InstrumentoTemporario("Honky-tonk Piano", 4, "Pianos"),
    InstrumentoTemporario("Electric Piano 1", 5, "Pianos"),
    InstrumentoTemporario("Electric Piano 2", 6, "Percussão"),
    InstrumentoTemporario("Harpsichord", 7, "Percussão"),
    InstrumentoTemporario("Church Organ", 20, "Órgãos"),
    InstrumentoTemporario("Accordion", 22, "Órgãos"),
    InstrumentoTemporario("Harmonica", 23, "Órgãos"),
    InstrumentoTemporario("Tango Accordion", 24, "Órgãos"),
    InstrumentoTemporario("Drawbar Organ", 17, "Órgãos"),
    InstrumentoTemporario("Acoustic Guitar", 25, "Guitarras"),
    InstrumentoTemporario("Electric Guitar", 27, "Guitarras"),
    InstrumentoTemporario("Electric Guitar (clean)", 28, "Guitarras"),
    InstrumentoTemporario("Electric Guitar (muted)", 29, "Guitarras"),
    InstrumentoTemporario("Overdriven Guitar", 30, "Guitarras"),
    InstrumentoTemporario("Acoustic Bass", 33, "Baixos"),
    InstrumentoTemporario("Electric Bass", 34, "Baixos"),
    InstrumentoTemporario("Slap Bass 1", 37, "Baixos"),
    InstrumentoTemporario("Violin", 41, "Baixos"),
    InstrumentoTemporario("String Ensemble 1", 49, "Baixos"),
    InstrumentoTemporario("Orchestral Harp", 47, "Sopros de madeira / Pipe"),
    InstrumentoTemporario("Flute", 74, "Sopros de madeira / Pipe"),
    InstrumentoTemporario("Piccolo", 73, "Sopros de madeira / Pipe"),
    InstrumentoTemporario("Recorder", 75, "Sopros de madeira / Pipe"),
    InstrumentoTemporario("Pan Flute", 76, "Sopros de madeira / Pipe"),
    InstrumentoTemporario("Lead 1 (square)", 81, "Sintetizadores pad"),
    InstrumentoTemporario("Lead 2 (sawtooth)", 82, "Sintetizadores pad"),
    InstrumentoTemporario("Pad 1 (new age)", 89, "Sintetizadores pad"),
)
