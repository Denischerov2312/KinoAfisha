from livereload import shell, Server
server = Server()
server.watch('index.html', shell('make html', cwd='docs'))
server.serve(root='')