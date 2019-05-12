import re

a = 'jsonlaolao*#洪文.dshfjsdf.st.txt'

print(re.sub(r'\..*$|json|\W', '', a))

