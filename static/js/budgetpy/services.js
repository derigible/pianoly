'use strict';
/**
 * The REST client for services. We want to put all interactions with the server here,
 * as well as any shared data structures or data retrieval.
 */

var services = angular.module('genericServices', ['ngResource']);

var baseErrHandler = function(response){
	console.log("failed to load the data.");
	return null;
}
var basePostErrHandler = function(response){
	console.log("failed to submit the data.");
	console.log(response);
	alert("failed to submit the data." + response);
	return null;
}

services.factory('USERKEY', function(){return 'user';})

services.factory('AuthServicer', ['$cookies', 'Auth', 'USERKEY',
    function($cookies, auth, userKey){
		return {
			email: null,
			perms: {level: 0},
			get_user: function(){
				if(this.email == null){
					var userCookie = $cookies.getObject(userKey);
					if(userCookie){
						this.email = userCookie.email;
						this.perms = userCookie.perms;
					}
				}
				return {email: this.email, password: '', perms: this.perms}
			},
			set_user: function(userData, self){
				if(typeof self == 'undefined'){
					self = this;
				}
				if(!self.is_loggedin(userKey)){
					self.email = userData.email;
					self.perms = userData.perms;
					$cookies.putObject(userKey, {email: self.email, perms: self.perms}, {path: '/'})
				}
				return false;
			},
			is_loggedin: function(){
				try{
					var user = $cookies.getObject(userKey);
					return user.email != '';
				} catch(err){
					return false;
				}
			},
			login: function(data, myfn){
				var set_user = this.set_user;
				var self = this;
				return auth.login({}, data, function(data){
					var empty = '';
					auth.perms({}, function(pdata, empty, uk){
						data.perms = pdata;
						set_user(data, self);
						myfn(uk)
					});
				})
			},
			logout : function(){
				if(this.is_loggedin(userKey)){
					var self = this;
					return auth.logout({}).$promise.then(function(data){
						$cookies.remove(userKey, {path : '/'});
						self.email = null;
						self.perms = {level : 'student'};
					});
				}
				return false;
			},
			register : function(userData){
				console.log(userData);
				return auth.register({}, userData).$promise;
			}
		}
	}
]);

services.factory('Auth', ['$resource',
    function($res){
		return $res('/admin/:action/', {},
					{
						register : {
							method: 'POST',
							interceptor: {responseError: basePostErrHandler},
							params: {action: 'register'}
						},
						login : {
							method: 'POST',
							interceptor: {responseError: basePostErrHandler},
							params: {action: 'login'}
						},
						logout : {
							method: 'DELETE',
							interceptor: {responseError: basePostErrHandler},
							params: {action: 'login'}
						},
						perms : {
							method: 'GET',
							interceptor: {responseError: basePostErrHandler},
							params: {action: 'permission'}
						}
					}, 
					{stripTrailingSlashes: false}
				);
    }
]);

/**
 * To use, pass in an object that has a key-value pair of entity:<entity> where
 * <entity> is one of the following:
 * 
 */
services.factory('EntityClient', ['$resource',
    function($res){
		return $res('/db/models/:entity/', {},
				{get : {
					method: 'GET',
					params: {entity:'assignmentinstance'},
					cache: true,
					interceptor: {responseError: baseErrHandler}
				},
				post : {
					method: 'POST',
					interceptor: {responseError: basePostErrHandler}
				},
				 put : {
					method: 'PUT',
					interceptor: {responseError: basePostErrHandler}
				 },
				 options : {
					 method: 'OPTIONS',
					 interceptor: {responseError: basePostErrHandler}
				 }
				}, 
				{stripTrailingSlashes: false}
		);
	}
]);

/**
 * Taken from http://stackoverflow.com/questions/25596399/set-element-focus-in-angular-way
 */
services.factory('Focus', function($timeout, $window) {
    return function(id) {
        // timeout makes sure that it is invoked after any other event has been triggered.
        // e.g. click events that need to run before the focus or
        // inputs elements that are in a disabled state but are enabled when those events
        // are triggered.
        $timeout(function() {
          var element = $window.document.getElementById(id);
          if(element)
            element.focus();
        });
      };
});

services.factory('NestedDictLookup', function(){
	return function(data, lookup){
		var lookups = lookup.split('.');
		var node = data;
		for(var i = 0; i < lookups.length; i++){
			if(!node.hasOwnProperty(lookups[i])){
				return null;
			} else {
				node = node[lookups[i]];
			}
		}
		return node;
	}
});