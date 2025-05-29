## Groupe P
#### ALLOUT Kamila, RAMADAN Dina, TCHOUBOUKOFF Louka, GULER Serra, IBRHAHIM Loane

Notre projet consiste en... 

Nous avons donc fait un ETL sur deux fichiers CSV, un contenant les donnees des entreprises et l'autre des indicateurs
macroéoonomiques des pays. 

On a fait une jointure entre les deux sur la colonne des pays, et on a garde l'autre dataset afin de ne pas perdre les 
informations relatives aux entreprises.

On a retransformé ces deux tableaux dans model en calculant des ratio puis en realisant des joinutres. 
Ces tableaux ont ete exportés dans une base SQLite.

L'interface utilisateur permet de visualiser les résultats de ces transformations sous forme de tableaux interatifs 
et de graphiques dynamiques.