var drctvs = angular.module('genericDirectives', []);

/**
 * Taken from http://stackoverflow.com/questions/25596399/set-element-focus-in-angular-way
 */
drctvs.directive('eventFocus', ['Focus', function(focus) {
    return function(scope, elem, attr) {
        elem.on(attr.eventFocus, function() {
          focus(attr.eventFocusId);
        });

        // Removes bound events in the element itself
        // when the scope is destroyed
        scope.$on('$destroy', function() {
          elem.off(attr.eventFocus);
        });
      };
    }]);

/**
 * Header list submenu option.
 */
drctvs.directive('hli', function(){
	return {
		restrict: 'AE',
		template: function(elem, attr){
			return '<li><a href="'+attr.url+'">'+attr.txt+'</a></li>';
		}
	};
});

/**
 * Taken from http://stackoverflow.com/questions/12393703/how-to-include-one-partials-into-other-without-creating-a-new-scope
 */
drctvs.directive('staticInclude', function($http, $templateCache, $compile) {
    return function(scope, element, attrs) {
        var templatePath = attrs.staticInclude;
        $http.get(templatePath, { cache: $templateCache }).success(function(response) {
            var contents = element.html(response).contents();
            $compile(contents)(scope);
        });
    };
});

drctvs.directive('modal', function() {
	return {
		restrict: 'E',
		transclude: true,
		templateUrl: 'partials/modal.html'
	};
});

drctvs.directive('addAssign', function() {
  return {
	    restrict: 'E',
	    scope: true,
	    templateUrl: 'partials/add_assign.html'
	  };
});