// Based on IPython's base.js.utils
// Original Copyright (c) IPython Development Team.
// Distributed under the terms of the Modified BSD License.

// Modifications Copyright (c) Juptyer Development Team.
// Distributed under the terms of the Modified BSD License.

let $ = require("jquery");

let all = function (promises) {
  // A form of jQuery.when that handles an array of promises
  // and equalises the behavior regardless if there's one or more than
  // one elements.
  if (!Array.isArray(promises)) {
    throw new Error("$.all() must be passed an array of promises");
  }
  return $.when.apply($, promises).then(function () {
    // if single argument was expanded into multiple arguments,
    // then put it back into an array for consistency
    if (promises.length === 1 && arguments.length > 1) {
      // put arguments into an array
      return [Array.prototype.slice.call(arguments, 0)];
    } else {
      return Array.prototype.slice.call(arguments, 0);
    }
  });
};

let update = function (d1, d2) {
  // Transfers the keys from d2 to d1. Returns d1
  $.map(d2, function (i, key) {
    d1[key] = d2[key];
  });
  return d1;
};

let maxIframeSize = function () {
  // Returns the current iframe viewport size
  let box = document.querySelector(".content-wrapper").getBoundingClientRect();
  return [box.width, box.height];
};

module.exports = {
  all,
  update,
  maxIframeSize
};
