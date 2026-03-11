# Ejecuta este código para ver la estructura 
import os 
for root, dirs, files in os.walk('.'): 

    level = root.replace('.', '').count(os.sep) 
    indent = ' ' * 2 * level 
    print(f'{indent}{os.path.basename(root)}/') 
    subindent = ' ' * 2 * (level + 1) 
    for file in files: 

        print(f'{subindent}{file}')