from mock import MagicMock
from test_utils import CharmTestCase, patch_open

import lib.swift_storage_context as swift_context


TO_PATCH = [
    'config',
    'log',
    'related_units',
    'relation_get',
    'relation_ids',
    'unit_private_ip',
    'get_ipv6_addr',
]


class SwiftStorageContextTests(CharmTestCase):

    def setUp(self):
        super(SwiftStorageContextTests, self).setUp(swift_context, TO_PATCH)
        self.config.side_effect = self.test_config.get

    def test_swift_storage_context_missing_data(self):
        self.relation_ids.return_value = []
        ctxt = swift_context.SwiftStorageContext()
        self.assertEquals(ctxt(), {})
        self.relation_ids.return_value = ['swift-proxy:0']
        self.related_units.return_value = ['swift-proxy/0']
        self.relation_get.return_value = ''
        self.assertEquals(ctxt(), {})

    def test_swift_storage_context_with_data(self):
        self.relation_ids.return_value = []
        ctxt = swift_context.SwiftStorageContext()
        self.assertEquals(ctxt(), {})
        self.relation_ids.return_value = ['swift-proxy:0']
        self.related_units.return_value = ['swift-proxy/0']
        self.relation_get.return_value = 'fooooo'
        self.assertEquals(ctxt(), {'swift_hash': 'fooooo'})

    def test_rsync_context(self):
        self.unit_private_ip.return_value = '10.0.0.5'
        ctxt = swift_context.RsyncContext()
        ctxt.enable_rsyncd = MagicMock()
        ctxt.enable_rsyncd.return_value = True
        self.assertEquals({'local_ip': '10.0.0.5'}, ctxt())
        self.assertTrue(ctxt.enable_rsyncd.called)

    def test_rsync_context_ipv6(self):
        self.test_config.set('prefer-ipv6', True)
        self.get_ipv6_addr.return_value = ['2001:db8:1::1']
        ctxt = swift_context.RsyncContext()
        ctxt.enable_rsyncd = MagicMock()
        ctxt.enable_rsyncd.return_value = True
        self.assertEquals({'local_ip': '2001:db8:1::1'}, ctxt())
        self.assertTrue(ctxt.enable_rsyncd.called)

    def test_rsync_enable_rsync(self):
        with patch_open() as (_open, _file):
            ctxt = swift_context.RsyncContext()
            _file.read.return_value = 'RSYNC_ENABLE=false'
            ctxt.enable_rsyncd()
            _file.write.assert_called_with('RSYNC_ENABLE=true')
            _file.read.return_value = '#foo'
            ctxt.enable_rsyncd()
            _file.write.assert_called_with('RSYNC_ENABLE=true\n')

    def test_swift_storage_server_context(self):
        self.unit_private_ip.return_value = '10.0.0.5'
        self.test_config.set('account-server-port', '500')
        self.test_config.set('object-server-port', '501')
        self.test_config.set('container-server-port', '502')
        self.test_config.set('object-server-threads-per-disk', '3')
        self.test_config.set('object-replicator-concurrency', '3')
        self.test_config.set('account-max-connections', '10')
        self.test_config.set('container-max-connections', '10')
        self.test_config.set('object-max-connections', '10')
        ctxt = swift_context.SwiftStorageServerContext()
        result = ctxt()
        ex = {
            'container_server_port': '502',
            'object_server_port': '501',
            'account_server_port': '500',
            'local_ip': '10.0.0.5',
            'object_server_threads_per_disk': '3',
            'object_replicator_concurrency': '3',
            'account_max_connections': '10',
            'container_max_connections': '10',
            'object_max_connections': '10',
        }
        self.assertEquals(ex, result)
