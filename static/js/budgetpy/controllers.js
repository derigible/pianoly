'use strict';

var ctrls = angular.module('bpyControllers', []);

/**
 * The master controller contains functions and data that will be
 * needed across all sections of the application.
 */
ctrls.controller('MasterCtrl', ['$scope', '$location', 'AuthServicer',
    function($scope, $loc, adb){
    	$scope.$loc = $loc;
    	$scope.logged_msg = 'Login';
    	
    	if(adb.is_loggedin()){
			$scope.user = adb.get_user();
			$scope.isLoggedIn = true;
			$scope.logged_msg = $scope.user.email.split('@')[0] || 'User';
		} else {
			$scope.user = adb.get_user();
			$scope.isLoggedIn = false;
			$scope.logged_msg = 'Login';
		}
    	$scope.register = function(){
    		adb.register($scope.user).then(function(){
				$scope._login();
				});
			
		}
		$scope._login = function(){
			if($scope.login_register.username.$valid && $scope.login_register.username.$viewValue){
				adb.login($scope.user, function(uk){
					$scope.login = false;
					$scope.isLoggedIn = true;
					$scope.logged_msg = $scope.user.email.split('@')[0] || 'User';
					$scope.user = adb.get_user(uk);
				});
			} else {
				alert("Need to add a valid email.")
			}
		}
		$scope.logout = function(){
			var p = adb.logout();
			if(p){
				p.then(function(){
					$scope.login = false;
					$scope.isLoggedIn = false;
					$scope.logged_msg = 'Login';
					$scope.user = adb.get_user();
				});	
			}
		}
    }
]);

ctrls.controller('WelcomeCtrl', ['$scope', 
    function($scope){
		$scope.announcements = [];
	}
]);

ctrls.controller('LessonCtrl', ['$scope', '$routeParams', 'EntityClient',
    function($scope, $rp, ec){
		ec.get();
	}
]);