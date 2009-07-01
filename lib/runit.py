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
backend.setup()

header("Adding users")
User.add("admin")
User.add("foo")
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
from models.new_group import backend as gbend, Group

header("Setup")
gbend.setup()

Group.add("test")
Group.add("foo")

test = Group("test")
test.add_member(admin)
test.add_member(User("bar"))

for group in Group.list():
	print "*", group, '(%r)' % group

	print "  Members:"
	for m in group.members():
		print "  *", m
