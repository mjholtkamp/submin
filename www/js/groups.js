load('dom')
load("selector")

function removeMemberAjax(member) {
	return AjaxSyncPostLog(document.location, "removeMember=" + member);
}

function addMemberAjax(member) {
	return AjaxSyncPostLog(document.location, "addMember=" + member);
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
	var response = AjaxSyncPostRequest(document.location, 'initSelector=1');
	var users = response.xml.getElementsByTagName("user");
	Log(response.text, response.success);

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
	var selector = new Selector({
			"selectorId": "members",
			"urlPrefix": media_url + "/users/show/",
			"init": initUsers,
			"addCallback": addMemberAjax,
			"removeCallback": removeMemberAjax,
			"canLink": function(user) { return is_admin || user == me; }
	});
}
