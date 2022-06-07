import pandas as pd
from xml.sax import ContentHandler, parse

# Reference https://goo.gl/KaOBG3
class ExcelHandler(ContentHandler):
    def __init__(self):
        self.chars = [  ]
        self.cells = [  ]
        self.rows = [  ]
        self.tables = [  ]
    def characters(self, content):
        self.chars.append(content)
    def startElement(self, name, atts):
        if name=="Cell":
            self.chars = [  ]
        elif name=="Row":
            self.cells=[  ]
        elif name=="Table":
            self.rows = [  ]
    def endElement(self, name):
        if name=="Cell":
            self.cells.append(''.join(self.chars))
        elif name=="Row":
            self.rows.append(self.cells)
        elif name=="Table":
            self.tables.append(self.rows)

excelHandler = ExcelHandler()
parse('rteso04.xls', excelHandler)
df = pd.DataFrame(excelHandler.tables[0][4:])

df = df[pd.to_numeric(df[0], errors='coerce').notnull()]
for i in range(18,50):
    df[i] = 0
    # fuente
    if i == 35:
        df[i] = df[6]
    # número op
    elif i == 43:
        df[i] = df[0]
    # monto disponible
    elif i == 34:
        df[i] = df[17]
    # cuit
    elif i == 37:
        df[i] = df[11]
    # fecha op
    elif i == 46:
        df[i] = df[2]
    # monto total
    elif i == 32:
        df[i] = df[15]

pd.set_option('display.max_columns', None)
df.to_csv(r'rteso04.txt', header=None, index=None, sep=';', mode='w')
# print("llegué")