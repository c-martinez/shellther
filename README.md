# SC-shell
Software Carpentry instructor shell. This program starts a command line terminal which logs output and uses an *engine* to push the content periodically to a back end (such as Etherpad).

## Install via NPM
To run SC-shell, you need to have NodeJS installed.

Install SC-shell from NPM as follows:
```
$ npm install --global https://github.com/c-martinez/sc-shell
```

## Configure

The SC-shell configuration file is located in `$NPM_PREFIX/lib/node_modules/sc-shell/config.js` where `$NPM_PREFIX` is the global npm path. If you don't know this path, you can find it out by running: `$ npm config get prefix`.

Edit your configuration file to use the desired engine. For example, the following configuration uses the Etherpad engine:

```
// Configuration for working with Etherpad
var etherpadConfig = {
  engine: 'etherpad',
  apikey: 'e792c32e44952f8d24c2cabe35bf36a12003d04726d3579c36f5a1d00569c81c',
  host: 'localhost',
  port: 9001,
  padID: 'scshell-test',
};

module.exports = etherpadConfig;
```

This configuration writes to an pad called `scshell-test`, hosted on the localhost.

## Running

To run SC-shell, run the `scshell` command as follows:

```
$ scshell
Script started, file is shellLog.txt
$ ps
  PID TTY          TIME CMD
19442 pts/18   00:00:00 bash
19475 pts/18   00:00:00 ps
$ exit
exit
Script done, file is shellLog.txt
```

This will update the content of your back end repository. For example, the following is the result using the Etherpad engine:

![etherpad example][images/etherpad.png]

## TODO's
 - Add more engines
 - Etherpad engine
   - Incremental updates
   - Clean special characters from content before pushing
