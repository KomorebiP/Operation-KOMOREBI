"""Prevent passing workflow records from being attached to another revision."""
import copy
import unittest
from unittest.mock import patch

from update_publication_metadata import LIBRARIES, validate_library_records
from update_source_navigation import library_qualification_table, library_release_table


class LibraryObservationTests(unittest.TestCase):
    def test_newer_checks_and_older_release_sources_are_distinct(self):
        records=copy.deepcopy(LIBRARIES[:1])
        records[0]['remote_commit']='2'*40
        records[0]['release_commit']='1'*40
        records[0]['checks'][0]['head_sha']='2'*40
        with patch('update_source_navigation.LIBRARIES',records):
            checks=library_qualification_table()
            releases=library_release_table()
        for library in records:
            self.assertNotEqual(library['remote_commit'],library['release_commit'])
            self.assertIn('/commit/'+library['remote_commit'],checks)
            self.assertIn('/commit/'+library['release_commit'],releases)
            self.assertNotIn('/commit/'+library['remote_commit'],releases)

    def test_a_pass_for_another_commit_is_rejected(self):
        records=copy.deepcopy(LIBRARIES)
        records[0]['checks'][0]['head_sha']=records[0]['release_commit']
        with self.assertRaisesRegex(ValueError,'different library revision'):
            validate_library_records(records)

    def test_incomplete_or_failed_run_cannot_support_a_passing_observation(self):
        for status,conclusion in [('in_progress',None),('completed','failure')]:
            records=copy.deepcopy(LIBRARIES)
            records[0]['checks'][0].update(status=status,conclusion=conclusion)
            with self.assertRaisesRegex(ValueError,'completed successful run'):
                validate_library_records(records)

    def test_run_from_another_repository_is_rejected(self):
        records=copy.deepcopy(LIBRARIES)
        records[0]['checks'][0]['url']=records[1]['checks'][0]['url']
        with self.assertRaisesRegex(ValueError,'does not match repository and run'):
            validate_library_records(records)


if __name__=='__main__':
    unittest.main()
