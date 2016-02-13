# Shellther
Software Carpentry instructor shell. This program starts a command line terminal which logs output and uses an *engine* to push the content periodically to a back end (such as Etherpad).

## Install via PIP
To run shellther, you need to have Python installed.

Install shellther from pip as follows:
```
$ pip install git+git://github.com/c-martinez/shellther.git
```

## Configure

Create a configuration file with the following format:

```
[shellther]
apikey = <etherpad api key>
baseurl = http://<etherpad host url>/api
```

## Running

Run an etherpad exclusively dedicated for your terminal:

```
$ shellther <padID> [--config <configfile>] --dedicated
```
or an add a section to an existing etherpad
```
$ shellther <padID> [--config <configfile>] --section [--marker <marker>]
```

This will update the content of your Etherpad, for example:

![etherpad example](./images/etherpad.png)

## TODO's
 - Testing
 - Unit testing
 - Improve documentation
 - Nice version numbering
