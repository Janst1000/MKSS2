# Setup
Es gibt verschiedene Möglichkeiten wie dieses Projekt aufgesetzt werden kann. Entweder kann ein Venv mit den Python Paketen erstellt werden oder unter Nix bzw. 

NixOS kann eine komplette Umgebung mit den Python Paketen und Postman erstellt und in einer Shell nutzbar gemacht werden. Diese Shell hat keinerlei Auswirkungen auf andere installierte Pakete oder ausgeführte Programme. Mehr Infos zu Nix und NixOS gibt es hier unter https://nixos.org/
## Venv
Unter Windows oder Linux kann einfach ein Venv mit der requirements.txt erstellt werden.
### Linux
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
### Windows
```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```



## Nix/NixOS
Unter NixOS oder Nix kann sehr einfach eine Bash-Shell mit allen notwendigen Paketen erstellt werden. 
```bash
nix-shell
```
Die Nix-Shell wird durch die shell.nix erzeugt. Diese liest die requirements.txt aus und erstellt eine Python Umgebugen mithilfe von mach-nix. Zusätzlich wird Postman in der Shell zur Verfügung gestellt um REST-Anfragen manuell zu testen.
> Postman gilt als unfree Paket in Nix, da es nicht vollständig open source ist. Daher werden in der nix-shell "unfree" Packages erlaubt.

# Starten der API
Die API kann als einfaches Python Skript gestartet werden. Standardmäßig ist sie dann unter Port 5000 zu erreichen.
```bash
python3 api/app.py
```

## Ausführen von Unittests
Die Unittests sind in app_test.py definiert und können als einfaches Pythonskript ausgeführt werden.

```bash
python3 api/app_test.py
```

Bei erfolgreichen Tests sollte die Ausgabe wie folgt sein:
```bash
[nix-shell:~/KSS/MKSS2]$ python3 api/app_test.py
.......
----------------------------------------------------------------------
Ran 7 tests in 0.068s

OK

```