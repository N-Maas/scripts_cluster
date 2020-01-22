0.) ws_allocate <ordner_name> 60
	- Legt einen workspace an, in den du dann via rsync o.ä. die Instanzen kopieren kannst

1.) In deinem Home-Verzeichnis einen ordner "experiments" anlegen

2.) dort dann noch einen ordner für das entsprechende experiment anlegen und alle Skript-Dateien reinkopieren

3.) create_workload.sh
	- instance_dir, kValues, epsilon, start_scripts anpassen

4.) ./create_workload.sh 
	- Generiert workload.txt

5.) Ggf. start_kahypar-mf.py anpassen, falls du andere Commandline-Parameter brauchst

6.) ./slotbasedworkdistribution.py workload.txt & 
	- Startet die Jobs

7.) Die Ergebnisse landen dann in ~/experiments/<experiment-name>/results/script-name
