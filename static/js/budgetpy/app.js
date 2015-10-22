'use strict';

/**
 * The application for the frontend for my budgeteer project.
 */
var budgeteer = angular.module('BudgeteerApp',[
   'ngRoute',
   'ngCookies',
   'bpyControllers',
   'genericFilters',
   'genericServices',
   'genericDirectives'
]);

budgeteer.config(['$routeProvider',
    function($routeProvider){
		$routeProvider.
			when('/welcome', {
				templateUrl: 'drill/welcome.html',
				controller: 'WelcomeCtrl'
			}).
			when('/lesson/submit', {
				templateUrl: 'lesson/submit.html',
				controller: 'WelcomeCtrl'
			}).
			when('/lesson/all', {
				templateUrl: 'lesson/all.html',
				controller: 'LessonCtrl'
			}).
			when('/practice/submit', {
				templateUrl: 'practice/submit.html',
				controller: 'WelcomeCtrl'
			}).
			when('/practice/all', {
				templateUrl: 'practice/all.html',
				controller: 'WelcomeCtrl'
			}).
			otherwise({
				redirectTo: '/welcome'
			});
	}
]);