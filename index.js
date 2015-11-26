var spawn = require('child_process').spawn;
var fs = require('fs');

// Taken from: https://groups.google.com/forum/#!topic/nodejs/b9JdFrJQqn0
function shell(cmd, opts, callback) {
  process.stdin.pause();
  process.stdin.setRawMode(false);

  var child = spawn(cmd, opts, {
    stdio: 'inherit',
  });
  child.on('exit', function() {
    process.stdin.setRawMode(true);
    process.stdin.resume();
    exitAction();
    process.exit();
  });

  return child;
}

var timer;
function triggerTimer() {
  if (!timer) {
    timer = setTimeout(function() {
      timedAction();
      timer = null;
    }, timeout * 1000);
  }
}

// This action gets executed on exit
function exitAction() {
  console.log('Your EXIT callback could be called here');
}

// This action gets executed after N seconds of inactivity
function timedAction() {
  console.log('Your INTERMEDIATE callback could be called here');
}

var savefile = 'somefile.txt';
var timeout = 5;  // in seconds

shell('script', ['-f', savefile]);
fs.watch(savefile, triggerTimer);
