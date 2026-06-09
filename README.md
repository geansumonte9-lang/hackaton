Proyecto de accesibilidad hackaton

ScanApp automatiza el pre-diagnóstico de accesibilidad universal en Chile mediante IA. Analiza fotos en conjunto para crear informes consolidados, evitando duplicaciones y vinculando hallazgos a la OGUC (DS 50) y leyes de inclusión. Incluye checklist manual, gestión de acciones correctivas por edificio y previene errores técnicos ante la DOM.

Descagan python :https://www.python.org/downloads/
despues de instalar les va a aparecer un icono de carpeta en una punta del pc lo instalan tienen que apretar la casilla add python to PATH

luego de eso se intala las carpetas del proyecto 
todas se juntan en una carpeta:Auditor por ej usted decide
luego heche los documentos a la carpeta ,despues que se traspase todo vaya a la carpeta , al lado de recargar la carpeta va a ver esot que va mas o menos asi Este equipo > Escritorio > (nombre que alla escogido), todo eso lo borrar y escribe cmd.Asi tal cual cmd 
veras una pantalla neegra donde aparece una linea blanca pardadeando justo en ello copiara y pegara esto: pip install streamlit google-genai reportlab python-dotenv
despues ve a 
aistudio.google.com/apikey copia y pega en el navegador google
,Haz clic en el botón "Create API key"
Te aparece un texto largo tipo AIzaSyB3k... — ese es tu clave
Cópiala (Ctrl+C) , luego abre la carpeta creada con los archivos mouse a espacio vacio luego nuevo ,documento de texto,al ver el archivo se llamara  nuevo documento.txt,borra todo y escribe solo con punto al principio .env , .env window preguntara cambiar extencion apretas si , en ello pegaras esto:EMINI_API_KEY=(mas el texto largo copiado) y luego de todo eso guardalo arriba en la esquina dice archivo y guardar lo apretas.
luego de todo eso vas a la misma ventana negra oh si lo cerraste ,vas a la carpeta al lado del buscador aparece window y mas luego alli apretas y borras todo escribes cmd ,se te abrira la venta negra y copias y pegas esto:
streamlit run app.py y taran estara listo 
 ahora si leiste todo y es mac la cosa cambias vas a buscador y abres la textedit abre un documento en blanco escribes EMINI_API_KEY=(mas el texto largo copiado) en el cual el codigo buscar en aistudio.google.com/apikey y abrilo en el navegador y guardas en el nombre lo mismo escribe solo .env asi tal cual .env y donde guardar en la carpeta nueva con los documentos los cuales descargamos click en guardar y lo mismo apretas manteniendo el cmd + espacio(el cmd teclado justo al lado del espacio) sin soltar la barra espaciadora los sueltas y se abre terminal  copia y pega :cd Desktop/(nombre de la carpetas que nombraste con dpcumentos) sin nada mas solo cambias eso y listo ,luego eso deberia abrir con un nombre mas largo y justo alli copias y pegas esto :pip install streamlit google-genai reportlab python-dotenv se descargaran las cosas , en el cual no tenemos que temer y despues de todo eso copiamos y pegamos en el mismo lugar despues de la descarga streamlit run app.py y estariamos 







