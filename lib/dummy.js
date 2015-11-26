// This action gets executed on exit
function exitAction() {
  console.log('Your EXIT callback could be called here');
}

// This action gets executed after N seconds of inactivity
function timedAction() {
  console.log('Your INTERMEDIATE callback could be called here');
}

// Engine must contain these two actions:
module.exports = {
  'exitAction' : exitAction,
  'timedAction': timedAction,
};

