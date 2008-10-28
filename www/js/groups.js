load('dom')
load("selector")

var selector = null;

function refreshAndLog(response) {
	selector.reInit();
	LogResponse(response);
}

function removeMemberAjax(member) {
	AjaxAsyncPostRequest(document.location, "removeMember=" + member, refreshAndLog);
}

function addMemberAjax(member) {
	AjaxAsyncPostRequest(document.location, "addMember=" + member, refreshAndLog);
}

var old_load = window.onload;
window.onload = function() {
	if (old_load) old_load();
	groupSelectorInit()
}

/* Requests the groups via ajax, and forms two lists to be used by Selector */
function initUsers() {
	var added = [];
	var addable = [];
	var response = AjaxSyncPostRequest(document.location, 'listGroupUsers');
	LogResponse(response);
	var groupusers = FindResponse(response, 'listGroupUsers');
	if (!groupusers)
		return {"added": [], "addable": []};

	var users = groupusers.xml.getElementsByTagName("user");

	for (var user_idx=0; user_idx < users.length; ++user_idx) {
		var user = users[user_idx];
		if (user.getAttribute("member") == "true")
			added[added.length] = user.getAttribute("name");
		else
			addable[addable.length] = user.getAttribute("name");
	}
	
	return {"added": added, "addable": addable};
}

function groupSelectorInit() {
	selector = new Selector({
			"selectorId": "members",
			"urlPrefix": base_url + "users/show/",
			"initCallback": initUsers,
			"addCallback": addMemberAjax,
			"removeCallback": removeMemberAjax,
			"canLink": function(user) { return is_admin || user == me; }
	});
}
