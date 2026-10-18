"""Offline ELF disassembly using workspace Capstone/pyelftools; not REA evidence."""
import argparse
import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / 'analysis-packages'))
from elftools.elf.elffile import ELFFile
from capstone import Cs, CS_ARCH_ARM, CS_MODE_ARM, CS_MODE_THUMB

parser = argparse.ArgumentParser()
parser.add_argument('binary')
parser.add_argument('pattern')
args = parser.parse_args()
with open(args.binary, 'rb') as stream:
    elf = ELFFile(stream)
    functions = {}
    for section in elf.iter_sections():
        if section['sh_type'] in ('SHT_DYNSYM', 'SHT_SYMTAB'):
            for symbol in section.iter_symbols():
                if symbol['st_info']['type'] == 'STT_FUNC' and symbol['st_size']:
                    functions[symbol.name] = (symbol['st_value'], symbol['st_size'])
    names = {address & ~1: name for name, (address, _) in functions.items()}
    rel = elf.get_section_by_name('.rel.plt')
    plt = elf.get_section_by_name('.plt')
    if rel and plt:
        dyn = elf.get_section(rel['sh_link'])
        for index, relocation in enumerate(rel.iter_relocations()):
            names[plt['sh_addr'] + 20 + index * 12] = dyn.get_symbol(relocation['r_info_sym']).name
    def read(address, length):
        for section in elf.iter_sections():
            if section['sh_type'] != 'SHT_NOBITS' and section['sh_addr'] <= address < section['sh_addr'] + section['sh_size']:
                start = address - section['sh_addr']
                return section.data()[start:start + length]
        return b''
    for name, (value, size) in functions.items():
        if not re.search(args.pattern, name):
            continue
        address = value & ~1
        print('\nFUNCTION', name, hex(address), size)
        decoder = Cs(CS_ARCH_ARM, CS_MODE_THUMB if value & 1 else CS_MODE_ARM)
        decoder.skipdata = True
        for instruction in decoder.disasm(read(address, size), address):
            annotation = ''
            if instruction.mnemonic in ('bl', 'blx') and instruction.op_str.startswith('#'):
                annotation = names.get(int(instruction.op_str[1:], 16), '')
            print(f'{instruction.address:08x} {instruction.mnemonic:10} {instruction.op_str:35} {annotation}')
