from sys import path
from typing import List
import fitz
from dataclasses import dataclass, field
from enum import Enum, auto
from collections import namedtuple
import re, os
import argparse
import json

Block = namedtuple('Block', 'x0, y0, x1, y1, text, block_no, block_type') 

class RecordType(Enum):
    SOLD = auto()
    TRANSACTION = auto()
    OTHER = auto()

@dataclass
class Record:
    blocks:List
    type:RecordType = RecordType.TRANSACTION


def parse_bank_statement(pdf_path,output_file='extrase.json',verbose=False,bank='raiffeisen'):
    if os.path.isdir(pdf_path):
        filenames = [os.path.join(pdf_path, filename) for filename in os.listdir(pdf_path)]
    else:
        filenames = [pdf_path]
    
    records = []

    for filename in filenames:
        read_file(records, filename)
    
    transactions = [record for record in records if record.type == RecordType.TRANSACTION]
    solds = [record for record in records if record.type == RecordType.SOLD]

    
    transactions_dicts = []

    if bank == 'raiffeisen':
        extract_raiffeisen_transactions(transactions, transactions_dicts)
    elif bank == 'alpha':
        extract_alpha_bank_transactions(transactions, transactions_dicts)
    else:
        raise Exception('Not a supported bank yet. Try `alpha` or `raiffeisen`.')
    
    if verbose:
        print(transactions_dicts)

    return transactions_dicts


def read_file(records, filename):
    doc = fitz.open(filename)
    pages = [page for page in doc]
    for page in pages:
        blocks = [Block(*block) for block in page.get_text("blocks")] 
        records += process_blocks(blocks)
    return 

def get_next_record(blocks) -> Record:
    block = blocks.pop(0)
    if re.search(r'Comision plata', block.text):
        return Record([block], RecordType.TRANSACTION)
    if re.match(r'\d\d\.\d\d\.\d\d\d\d*', block.text):
        records = [block, blocks.pop(0)]

        return Record(records, RecordType.TRANSACTION)

    if block.text.startswith('Soldul zilei'):
        return Record([block], RecordType.SOLD)

    else:
        record = Record([block], RecordType.OTHER)
        return record

def process_blocks(blocks) -> List[Record]:
    records = []

    while blocks:
        records += [get_next_record(blocks)]

    return records


def extract_alpha_bank_transactions(transactions, transactions_dicts):
    for transaction in transactions:
        transaction_date, value_date, transaction_reference, description =\
            transaction.blocks[0].text.split('\n', 3)
        sum = transaction.blocks[1].text
        sign = -1 if re.match(r'\d*', sum)  else 1
        signed_sum_in_bani = int(''.join(re.findall(r'\d*', sum))) * sign
        
        transactions_dicts += [
                {
                    "transaction_date":transaction_date,
                    "value_date":value_date,
                    "transaction_reference":transaction_reference,
                    "description":description,
                    "signed_sum_in_bani":signed_sum_in_bani,
                }
        ]

def extract_raiffeisen_transactions(transactions, transactions_dicts):
    for transaction in transactions:
        registration_date, transaction_date, description = transaction.blocks[0].text.split('\n', 2)
        x1 = transaction.blocks[-1].x1
        sum = transaction.blocks[-1].text
        sign = 1 if abs(x1 - 454) > abs(x1 - 555)  else -1
        signed_sum_in_bani = int(
            ''.join(
                re.findall(
                    r'\d*', 
                    re.sub(r'\d\d\.\d\d\.\d\d\d\d', '', sum)
                    )
                )
            ) * sign

        transactions_dicts += [
                {
                    "registration_date":registration_date,
                    "transaction_date":transaction_date,
                    "description":description,
                    "signed_sum_in_bani":signed_sum_in_bani,
                }
        ]


if __name__ == '__main__':
    ####################################
    parser = argparse.ArgumentParser(description='Extract transactions from bank statements.')

    parser.add_argument('filename', type=str, nargs='?',
                        help='path to PDF statement')

    parser.add_argument('-o','--output', dest='output', type=str, nargs='?',
                        default=None,
                        help='output path of generated JSON; default path is {base_filename}.json')

    parser.add_argument('-b','--bank', dest='bank', type=str, nargs='?',
                        default='raiffeisen',
                        help='kind of bank statement that is read. Supported banks: `raiffeisen`, `alpha`; default is `raiffeisen`')

    parser.add_argument('-v','--verbose', dest='verbose', action='store_const', const=True, 
                        default=False,
                        help='print JSON string')

    args = parser.parse_args()

    pdf_path = args.filename
    output_file = args.output
    verbose = args.verbose
    bank = args.bank

    if output_file is None:
        output_file = os.path.splitext(pdf_path)[0]+'.json'

    ####################################
    transactions_dicts = parse_bank_statement(pdf_path=pdf_path, output_file=output_file, verbose=verbose, bank=bank)

    with open(output_file, 'w') as f:
        json.dump(transactions_dicts, f)