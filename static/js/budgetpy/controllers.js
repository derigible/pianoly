'use strict';

var ctrls = angular.module('bpyControllers', []);

/**
 * The master controller contains functions and data that will be
 * needed across all sections of the application.
 */
ctrls.controller('MasterCtrl', ['$scope', '$location', '$route', 'AuthServicer',
    function($scope, $loc, $route, adb){
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
					$route.reload();
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
					$route.reload(); 	
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

ctrls.controller('LessonCtrl', ['$scope', '$routeParams', '$cacheFactory', 'EntityClient', 
    function($scope, $rp, $cacheFactory, ec){
		var params = {};
		var changes = new Set();

		if($scope.$parent.user.level > 0){
			params.entity = "assignment";
		} else {
			params.entity = "userassignment";
			params._expand = true;
			params._depth = 1;
		}
		$scope.params = params;
		
		$scope.removeModal = function(){
			$scope.modal = false;
			$scope.$parent.$loc.search('modal', null);
		}

		ec.get(params, function(data){
			$scope.assignments = data.data;
			if(params.entity == "userassignment"){
				for(var i = 0; i < $scope.assignments.length; i++){
					var item = $scope.assignments[i];
					item.due_date = new Date(item.assignment.due_date);
					item.reqs = angular.fromJson(item.assignment.requirements);
					item.rcompleted = angular.fromJson(item.requirements);
					for(var j = 0; j < item.rcompleted.length; j++){
						item.reqs[j].complete = item.rcompleted[j];
					}
				}
			} else {
				for(var i = 0; i < $scope.assignments.length; i++){
					var a = $scope.assignments[i];
					a.reqs =  angular.fromJson($scope.assignments[i].requirements);
					a.reqs.edit = false;
					a.due_date = new Date(a.due_date);
					a.edit = false;
				}
			}
			console.log($scope.assignments)
		});
		
		$scope.changeManage = function(){
			if($scope.$parent.$loc.search().hasOwnProperty('manage')){
				$scope.$parent.$loc.search('manage', null);
				$scope.manage = false;
			} else {
				$scope.$parent.$loc.search('manage', true);
				$scope.manage = true;
			}
		}
		
		$scope.addChanged = function(a){
			changes.add(a);
		}
		
		$scope.addReq = function(a, req){
			if(!a.hasOwnProperty('new_reqs')){
				a.new_reqs = [];
			}
			a.new_reqs.push(req);
		}
		
		$scope.removeReq = function(a, req, index){
			if(!a.hasOwnProperty('remove_reqs')){
				a.remove_reqs = [];
			}
			a.remove_reqs.push(index);
			req.remove = a.remove_reqs.length - 1;
			console.log(a)
		}
		
		$scope.addReqBack = function(a, req){
			a.remove_reqs.splice(req.remove, 1);
			req.remove = -1;
		}
		
		$scope.submitChanges = function(){
			var to_submit = [];
			for(var i = 0; i < $scope.assignments.length; i++){
				var a = $scope.assignments[i];
				var s = {id: a.id, idx: i};
				var add = false;
				console.log(a)
				if(a.hasOwnProperty('new_reqs')){
					s.new_reqs = a.new_reqs;
					add = true;
				}
				if(a.hasOwnProperty('remove_reqs')){
					console.log("removing things")
					s.remove_reqs = a.remove_reqs;
					add = true;
				}
				if(add){
					to_submit.push(s);
				}
			}
			var c_to_submit = [];
			for(var i of changes){
				c_to_submit.push({id: i.id, 
								  desc: angular.toJson(i.reqs),
								  due_date: i.date.toISOString()
								 }
				);
			}
			var submit = {req_changes : to_submit,
						  assignment_changes: c_to_submit
						  };
			
			ec.put({entity: 'assignment'}, submit, function(data){
				alert("submit successful");
				for(var i = 0; i < to_submit.length; i++){
					var a = $scope.assignments[to_submit[i].idx];
					for(var j = 0; j < a.remove_reqs; j++){
						a.reqs.splice(a.remove_reqs[j], 1)
					}
				}
			});
		}
		
		$scope.addAssignment = function(){
			if($scope.$parent.$loc.search().hasOwnProperty('add_assign')){
				$scope.$parent.$loc.search('modal', null);
				$scope.modal = false;
			} else {
				$scope.$parent.$loc.search('modal', true);
				$scope.modal = true;
			}
			
		}
		
		$scope.anew = {
				description: '',
				due_date : new Date(),
				requirements:[{desc: ''}]
		};
		
		$scope.removeAssignment = function(item){
			var d = confirm("Are you sure you want to delete assignment with id " + item.id +"? Deletion cannot be undone.");
			if(d){
				var p = prompt("Type the word DELETE to confirm deletion.")
				if(p == "DELETE"){
					ec.delete({entity: 'assignment', ids: item.id}, function(){
						alert("delete successful");
						$scope.assignments.splice($scope.assignments.indexOf(item), 1);
					}, function(data){
						if(data.status == 403 || data.status == 401){
							alert("You do not have privilege to delete projects.")
						} else {
							alert("Failed to delete "+ $rp.entity + " " +  item.id);
						}
					});
				}
			}
		}
		
		$scope.addReq = function(){
			$scope.anew.requirements.push({desc: ''});
		}
		
		$scope.addAss = function(){
			ec.post({entity: 'assignment'}, {data : $scope.anew}, function(data){
				$scope.assignments.push({
					description : $scope.anew.description,
					due_date : $scope.anew.due_date,
					reqs : $scope.anew.requirements
				});
				$scope.anew = {due_date : new Date(),
						requirements: [{desc: ''}]
				};
				$scope.removeModal();
				$cacheFactory.get('$http').removeAll();
			});
		}
		
		$scope.modal = $scope.$parent.$loc.search().hasOwnProperty('modal');
		$scope.manage = $scope.$parent.$loc.search().hasOwnProperty('manage');
	}
]);

ctrls.controller('AssignerCtrl', ['$scope', '$routeParams', '$cacheFactory', 'WoodwardClient',
    function($scope, $rp, $cf, wc){
		wc.assignment_students($rp, function(data){
			$scope.data = data;
			$scope.data.assignment.due_date = new Date(data.assignment.due_date);
			for(var i = 0; i < $scope.data.assigned_to.length; i++){
				$scope.data.assigned_to[i].assigned = true;
			}
			for(var i = 0; i < $scope.data.to_assign.length; i++){
				$scope.data.to_assign[i].assigned = false;
			}
		});
		
		var to_remove = new Set();
		var to_add = new Set();
		
		$scope.remove = function(student){
			if(to_remove.has(student.id)){
			    to_remove.delete(student.id);
				student.assigned = true;
			} else {
				to_remove.add(student.id);
				student.assigned = false;
			}
		}

		$scope.add = function(student){
		    if(to_add.has(student.id)){
		        to_add.delete(student.id);
		        student.assigned = false;
		    } else {
		        to_add.add(student.id);
		        student.assigned = true;
		    }
		}

		$scope.submitChanges = function () {
		    var add = [];
		    var remove = [];
		    for (let i of to_add.values()) {
		        add.push(i);
		    }
		    for (let i of to_remove.values()) {
		        remove.push(i);
		    }
		    wc.student_assigned_assignment($rp, { "add": add, "remove": remove }, function (data) {
                console.log(data)
		        $scope.data.assigned_to = data.assigned_to;
		        $scope.data.to_assign = data.to_assign;
		        for (var i = 0; i < $scope.data.assigned_to.length; i++) {
		            $scope.data.assigned_to[i].assigned = true;
		        }
		        for (var i = 0; i < $scope.data.to_assign.length; i++) {
		            $scope.data.to_assign[i].assigned = false;
		        }
		        $cf.get('$http').removeAll();
                alert("Changes submitted.")
		    });
		}
	}
]);