Set shell = CreateObject("WScript.Shell")
shell.CurrentDirectory = "C:\Users\mateus.braga\OneDrive - Peers Consulting\Documentos\Caminhos de Rosa"
shell.Run """C:\Users\mateus.braga\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"" manage.py runserver 127.0.0.1:8000 --noreload", 0, False
