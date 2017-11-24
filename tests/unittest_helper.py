import unittest

from flask import Flask
from prometheus_client import CollectorRegistry
from prometheus_flask_exporter import PrometheusMetrics


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.testing = True
        self.client = self.app.test_client()

    def metrics(self, **kwargs):
        registry = kwargs.pop('registry', CollectorRegistry(auto_describe=True))
        return PrometheusMetrics(self.app, registry=registry, **kwargs)

    def assertMetric(self, name, value, *labels, **kwargs):
        if labels:
            text = '%s{%s} %s' % (
                name, ','.join(
                    '%s="%s"' % (labelname, labelvalue)
                    for labelname, labelvalue in labels
                ), value
            )
        else:
            text = '%s %s' % (name, value)

        response = self.client.get(kwargs.get('endpoint', '/metrics'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(text.encode('utf-8'), response.data)

    def assertAbsent(self, name, *labels, **kwargs):
        if labels:
            text = '%s{%s} ' % (
                name, ','.join(
                    '%s="%s"' % (labelname, labelvalue)
                    for labelname, labelvalue in labels
                )
            )
        else:
            text = '%s ' % name

        response = self.client.get(kwargs.get('endpoint', '/metrics'))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(text.encode('utf-8'), response.data)
