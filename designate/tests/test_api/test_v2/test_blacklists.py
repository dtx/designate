# Copyright 2014 Rackspace Hosting
# All rights reserved
#
# Author: Betsy Luzader <betsy.luzader@rackspace.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
from designate.tests.test_api.test_v2 import ApiV2TestCase


class ApiV2BlacklistsTest(ApiV2TestCase):
    def setUp(self):
        super(ApiV2BlacklistsTest, self).setUp()

    def test_get_blacklists(self):
        # Set the policy file as this is an admin-only API
        self.policy({'find_blacklists': '@'})

        response = self.client.get('/blacklists/')

        # Check the headers are what we expect
        self.assertEqual(200, response.status_int)
        self.assertEqual('application/json', response.content_type)

        # Check the body structure is what we expect
        self.assertIn('blacklists', response.json)
        self.assertIn('links', response.json)
        self.assertIn('self', response.json['links'])

        # Test with 0 blacklists
        self.assertEqual(0, len(response.json['blacklists']))

        data = [self.create_blacklist(
            pattern='x-%s.org.' % i) for i in xrange(0, 10)]

        self._assert_paging(data, '/blacklists', key='blacklists')

    def test_get_blacklist(self):
        blacklist = self.create_blacklist(fixture=0)

        # Set the policy file as this is an admin-only API
        self.policy({'find_blacklist': '@'})

        response = self.client.get('/blacklists/%s' % blacklist['id'],
                                   headers=[('Accept', 'application/json')])

        # Verify the headers
        self.assertEqual(200, response.status_int)
        self.assertEqual('application/json', response.content_type)

        # Verify the body structure
        self.assertIn('blacklist', response.json)
        self.assertIn('links', response.json['blacklist'])
        self.assertIn('self', response.json['blacklist']['links'])

        # Verify the returned values
        self.assertIn('id', response.json['blacklist'])
        self.assertIn('created_at', response.json['blacklist'])
        self.assertIsNone(response.json['blacklist']['updated_at'])
        self.assertEqual(self.get_blacklist_fixture(0)['pattern'],
                         response.json['blacklist']['pattern'])

    def test_get_bkaclist_invalid_id(self):
        self._assert_invalid_uuid(self.client.get, '/blacklists/%s')

    def test_create_blacklist(self):
        self.policy({'create_blacklist': '@'})
        fixture = self.get_blacklist_fixture(0)
        response = self.client.post_json('/blacklists/',
                                         {'blacklist': fixture})

        # Verify the headers
        self.assertEqual(201, response.status_int)
        self.assertEqual('application/json', response.content_type)

        # Verify the body structure
        self.assertIn('blacklist', response.json)
        self.assertIn('links', response.json['blacklist'])
        self.assertIn('self', response.json['blacklist']['links'])

        # Verify the returned values
        self.assertIn('id', response.json['blacklist'])
        self.assertIn('created_at', response.json['blacklist'])
        self.assertIsNone(response.json['blacklist']['updated_at'])
        self.assertEqual(fixture['pattern'],
                         response.json['blacklist']['pattern'])

    def test_delete_blacklist(self):
        blacklist = self.create_blacklist(fixture=0)
        self.policy({'delete_blacklist': '@'})

        self.client.delete('/blacklists/%s' % blacklist['id'], status=204)

    def test_delete_bkaclist_invalid_id(self):
        self._assert_invalid_uuid(self.client.delete, '/blacklists/%s')

    def test_update_blacklist(self):
        blacklist = self.create_blacklist(fixture=0)
        self.policy({'update_blacklist': '@'})

        # Prepare the update body
        body = {'blacklist': {'description': 'prefix-%s' %
                                             blacklist['description']}}

        response = self.client.patch_json('/blacklists/%s' %
                                          blacklist['id'], body,
                                          status=200)

        # Verify the headers
        self.assertEqual(200, response.status_int)
        self.assertEqual('application/json', response.content_type)

        # Verify the body structure
        self.assertIn('blacklist', response.json)
        self.assertIn('links', response.json['blacklist'])
        self.assertIn('self', response.json['blacklist']['links'])

        # Verify the returned values
        self.assertIn('id', response.json['blacklist'])
        self.assertIsNotNone(response.json['blacklist']['updated_at'])
        self.assertEqual('prefix-%s' % blacklist['description'],
                         response.json['blacklist']['description'])

    def test_update_bkaclist_invalid_id(self):
        self._assert_invalid_uuid(self.client.patch_json, '/blacklists/%s')
