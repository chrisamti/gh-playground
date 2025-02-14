import unittest
import os
from changelog import list_files_in_subfolder, read_changelog_pr_file, parse_changelog_pr_file_content

class TestChangelog(unittest.TestCase):
    def setUp(self):
        self.test_dir = 'test_changelogs'
        os.makedirs(self.test_dir, exist_ok=True)
        self.test_file = os.path.join(self.test_dir, 'FE-1234_test.md')
        with open(self.test_file, 'w') as f:
            f.write("# jira:\n- FE-1234\n- CD2-1234\n\n# added:\n- this and that\n")

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        if os.path.exists(self.test_dir):
            os.rmdir(self.test_dir)

    def test_list_files_in_subfolder(self):
        files = list_files_in_subfolder(self.test_dir)
        self.assertIn('FE-1234_test.md', files)

    def test_read_changelog_pr_file(self):
        content = read_changelog_pr_file(self.test_file)
        self.assertIn('# jira:', content)
        self.assertIn('- FE-1234', content)

    def test_parse_changelog_pr_file_content(self):
        content = read_changelog_pr_file(self.test_file)
        sections, is_valid = parse_changelog_pr_file_content(content, self.test_file)
        self.assertTrue(is_valid)

        self.assertIn('jira:', sections)
        self.assertIn('added:', sections)
        self.assertEqual(sections['jira:'], ['FE-1234', 'CD2-1234'])
        self.assertEqual(sections['added:'], ['this and that'])


if __name__ == '__main__':
    unittest.main()