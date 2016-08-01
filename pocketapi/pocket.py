#!/usr/bin/env python

import re

import requests
import urllib2

from exceptions import PocketRequestError


class Pocket:
    url = 'https://getpocket.com/v3/'

    def __init__(self, consumer_key=None, access_token=None,
                 redirect_uri='https://example.com/', proxy=None):

        self.consumer_key = consumer_key
        self.code = None
        self.redirect_uri = redirect_uri
        self.access_token = access_token
        self.username = None
        self.proxies = {
            'http': proxy,
            'https': proxy
        } if proxy else None

    @property
    def is_authenticated(self):
        return self.consumer_key is not None and self.access_token is not None

    @staticmethod
    def _get_default_headers():
        headers = {'X-Accept': 'application/json'}
        return headers

    def _make_post_request(self, url, data=None, headers=None):
        try:
            resp = requests.post(url, data=data, headers=headers,
                                 proxies=self.proxies)
            if resp.status_code == 200:
                print(resp.request.headers)
                print(resp.headers)
                return resp
            else:
                raise PocketRequestError(resp.status_code, resp.headers[
                    'X-Error-Code'], resp.headers['X-Errror'])
        except requests.exceptions.ConnectionError:
            print("Connection Error")
        except requests.exceptions.Timeout:
            print("Request Timed Out")
        except requests.exceptions.HTTPError:
            print("Invalid HTTP response")
        except requests.exceptions.TooManyRedirects:
            print("Request exceeded configured number of maximum redirections")

    @staticmethod
    def _get_key_value_from_response(resp, key):
        if isinstance(resp, requests.Response):
            ctype = resp.headers.get('content-type')

            if ctype == 'application/json':
                try:
                    return resp.json()[key]
                except KeyError:
                    raise KeyError("No key named " + key + " in response.")

            elif ctype == 'application/x-www-form-urlencoded':
                try:
                    pattern = key + '=([^&]+)?'
                    val = re.search(pattern=pattern,
                                    string=resp.content).group(0)
                    # urllib2.unquote('username%40gmail.com')
                    # username@gmail.com
                    return urllib2.unquote(val.split('=')[1])
                except AttributeError:
                    raise KeyError("No key named " + key + " in response.")

            else:
                msg = "Getpocket.com v3 API supports only two Content-Type " \
                      "namely, application/x-www-form-urlencoded and " \
                      "application/json."
                raise TypeError(msg)

        else:
            raise TypeError("Argument is not a requests.Response instance")

    def get_request_token(self, state=None, headers=None):
        uri = self.url + 'oauth/request'

        data = {
            'consumer_key': self.consumer_key,
            'redirect_uri': self.redirect_uri,
            'state': state
        }

        if headers is None:
            headers = self._get_default_headers()

        resp = self._make_post_request(uri, data, headers)
        self.code = self._get_key_value_from_response(resp, 'code')
        return self.code

    def get_auth_redirection_url(self, code):
        url = 'https://getpocket.com/auth/authorize?request_token=' + code + \
              '&redirect_uri=' + self.redirect_uri
        return url

    def get_access_token(self, code, headers=None):
        uri = self.url + 'oauth/authorize'

        data = {
            'consumer_key': self.consumer_key,
            'code': code
        }

        if headers is None:
            headers = self._get_default_headers()

        resp = self._make_post_request(uri, data, headers)
        self.access_token = self._get_key_value_from_response(resp,
                                                              'access_token')
        self.username = self._get_key_value_from_response(resp, 'username')
        return self.access_token

    def _add(self, url, title, tags, tweet_id, headers):

        uri = self.url + 'add'

        data = {
            'consumer_key': self.consumer_key,
            'access_token': self.access_token,
            'url': url,
            'title': title,
            'tags': tags,
            'tweet_id': tweet_id
        }

        if headers is None:
            headers = self._get_default_headers()

        resp = self._make_post_request(uri, data, headers)
        return resp.json()

    def add(self, url, title=None, tags=None, tweet_id=None, headers=None):
        """
        Add URL to user's account.

        :param url: The URL of the item
        :param title: Include title for cases where an item does not have a
        title.
        :param tags: A comma-separated list of tags to apply to the item
        :param tweet_id: Tweet status id for adding tweets
        :param headers: HTTP headers dictionary
        :return: requests.Response object
        """
        return self._add(url, title, tags, tweet_id, headers)

    def _retrieve(self, state, favorite, tag, content_type, sort, detail_type,
                  search, domain, since, count, offset, headers):

        uri = self.url + 'get'

        data = {
            'consumer_key': self.consumer_key,
            'access_token': self.access_token,
            'state': state,
            'favorite': favorite,
            'tag': tag,
            'contentType': content_type,
            'sort': sort,
            'detailType': detail_type,
            'search': search,
            'domain': domain,
            'since': since,
            'count': count,
            'offset': offset
        }

        if headers is None:
            headers = self._get_default_headers()

        resp = self._make_post_request(uri, data, headers)

        return resp.json()

    def retrieve(self, state=None, favorite=None, tag=None, content_type=None,
                 sort=None, detail_type=None, search=None, domain=None,
                 since=None, count=None, offset=None, headers=None):

        return self._retrieve(state, favorite, tag, content_type, sort,
                              detail_type, search, domain, since, count,
                              offset, headers)

    def _modify(self, actions, headers):
        uri = self.url + 'send'

        data = {
            'consumer_key': self.consumer_key,
            'access_token': self.access_token,
            'actions': actions
        }

        if headers is None:
            headers = self._get_default_headers()

        resp = self._make_post_request(uri, data, headers)
        return resp.json()

    def modify(self, actions, headers=None):
        return self._modify(actions, headers)
