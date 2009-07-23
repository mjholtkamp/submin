import os
os.environ["SUBMIN_SETTINGS"] = "testsettings"
from bootstrap import settings

def header(*args):
	print "\n", " ".join(args)
	print "="*70

# Begin anew!
header("Removing database")
os.remove(settings.sqlite_path)
from models.user import backend, User, UnknownUserError

header("Setup (creating db etc)")
from models import backendSetup
backendSetup()

header("Adding users")
User.add("admin")
User.add("foo")
try:
	User.add("foo")
except Exception, e:
	print "Correctly raised:", e

User.add("bar")

admin = User("admin")
admin.is_admin = True

header("A list of all users:")
for user in User.list(admin):
	print "*", user, '(%r)' % user

header("Trying to retrieve nonexistent user")
try:
	nonexistent = User("Nonexistent")
except UnknownUserError:
	print 'Correcly threw UnknownUserError'

foo = User("foo")

header("This should only print the user foo:")
for user in User.list(foo):
	print "*", user, '(%r)' % user

assert foo.email == None
foo.email = "foo@foo.com"
foo.is_admin = True
foo.fullname = "Foo Bar"
admin.fullname = "A. Dmin"

assert foo.email == "foo@foo.com"

foo.remove()

print "="*78
print "GROUP STUFF"
print "="*78
from models.group import backend as gbend, Group, UnknownGroupError

Group.add("test")
try:
	Group.add("test")
except Exception, e:
	print "Correctly raised:", e

Group.add("foo")

bar = User("bar")
test = Group("test")
test.add_member(admin)
test.add_member(bar)

for group in Group.list():
	print "*", group, '(%r)' % group

	print "  Members:"
	for m in group.members():
		print "  *", m

print "Removing user `bar' from group `test'"
test.remove_member(bar)

print "Now, `test' has the following members:", ', '.join(test.members())
assert "bar" not in test.members(), "User `bar' should not be in group `test'!"

test.remove()
assert "test" not in Group.list(), "Group `test' should be removed, but is not!"

header("Trying to retrieve nonexistent group")
try:
	nonexistent = Group("Nonexistent")
except UnknownGroupError:
	print 'Correcly threw UnknownGroupError'

Group.add("bar")
Group.add("test")
test = Group("test")
test.add_member(admin)
all_groups = Group.list()
member_of = admin.member_of()
nonmember_of = admin.nonmember_of()

print "All groups:", [group.name for group in all_groups]
print "Groups admin is a member of:", member_of
print "Groups admin is not a member of:", nonmember_of

