# parse-bank-statement
This program, when ran as a script, takes a path to a PDF file or directory with PDF files and outputs the transactions in a JSON file.
When imported as a module (`import parse_bank_statement`) it provides the `parse_bank_statement` method that returns the transactions JSON. 
For now, Romanian banks Raiffeisen and Alpha Bank are suspported.

The program can be used mainly for analytics of your spending habits. The most natural way to use your transaction info is to label your transactions based on the transaction description and see how much you spend on each cathegory. An example Jupyter notebook will be provided in the near future.

## Run as script
First, install the `PyMuPDF` dependency. 
General advice: use `venv` or other tool to create a virtual environment so you don't mess up your OS's Python:
```
python3 -m venv statement-env
source statement-env/bin/activate
python3 -m pip install -U setuptools pip
python3 -m pip install PyMuPDF
```

To run the program:
```
python3 parse_bank_statement.py your_file_or_dir
```

To get the documentation:
```
python3 parse_bank_statement.py your_file_or_dir -h
```
Documentation:
```
usage: parse_bank_statement.py [-h] [-o [OUTPUT]] [-b [BANK]] [-v] [filename]

Extract transactions from bank statements.

positional arguments:
  filename              path to PDF statement or to directory with statements

optional arguments:
  -h, --help            show this help message and exit
  -o [OUTPUT], --output [OUTPUT]
                        output path of generated JSON; default path is {base_filename}.json
  -b [BANK], --bank [BANK]
                        kind of bank statement that is read. Supported banks: `raiffeisen`, `alpha`; default is `raiffeisen`
  -v, --verbose         print JSON string
```
