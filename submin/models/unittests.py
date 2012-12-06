import unittest

model_tests = ["users.UserTests", "groups.GroupTests", "options.OptionTests",
			"trac.TracTests", "repository.RepositoryTests"]

def suite():
	s = unittest.TestSuite()
	subtests = ["submin.models.tests.%s" % x for x in model_tests]
	map(s.addTest, map(unittest.defaultTestLoader.loadTestsFromName, subtests))
	return s

if __name__ == "__main__":
	unittest.main()
