### liblainuri-javascript

Javascript client and example implementation

Get the prepared distributable from dist/lainuri.v.v.v.min.js

### Developing/testing

To work with the sources, you need to spin up a simple http-server to serve the static files, for the browser to be able to properly set the Origin-header.

For ex.

cpanm Mojolicious
perl -MMojolicious::Lite -MCwd -e 'app->static->paths->[0]=getcwd; app->start' daemon -l http://*:8000

will start up a simple static content server

Then just point your browser to the test server

`firefox http://localhost:8000/index.html`

### Building a distributable

This is done simply by concatenating the dependencies and the library itself together.

`cat lib/axios.0.19.0-beta.1.min.js lainuri.js > dist/hetula.0.0.1.min.js`

This might cause issues with environments alredy using axios, so the build "system" will probably change "soon" :)
Setting up webpack would be an overkill.

## Or just pick the file

Copy

`lainuri.js`

to your program and deal with dependencies manually.
