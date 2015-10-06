/**
* Custom filters used in this application.
*/


var fltrs = angular.module('genericFilters', []);

function isInt(n){
    return Number(n) === n && n % 1 === 0;
}

function isFloat(n){
    return n === Number(n) && n % 1 !== 0;
}

fltrs.filter('formatFloat', ['numberFilter', function(number){
	return function(num, val){
		if(isFloat(num)){
			return number(num, val);
		}
		else{
			return num;
		}
	}
}])

//Taken from http://stackoverflow.com/questions/14478106/angularjs-sorting-by-property

fltrs.filter('orderObjectBy', function(){
	 return function(input, attribute) {
	    if (!angular.isObject(input)) return input;

	    var array = [];
	    for(var objectKey in input) {
	        array.push(input[objectKey]);
	    }

	    array.sort(function(a, b){
	        a = parseInt(a[attribute]);
	        b = parseInt(b[attribute]);
	        return a - b;
	    });
	    return array;
	 }
});

//Taken from http://justinklemm.com/angularjs-filter-ordering-objects-ngrepeat/
fltrs.filter('orderObjectsBy', function(){
	return function(items, field, reverse) {
	    var filtered = [];
	    angular.forEach(items, function(item) {
	      filtered.push(item);
	    });
	    filtered.sort(function (a, b) {
	      return (a[field] > b[field] ? 1 : -1);
	    });
	    if(reverse) filtered.reverse();
	    return filtered;
	  };
});

fltrs.filter('urlEncode', function() {
  return window.encodeURIComponent;
});