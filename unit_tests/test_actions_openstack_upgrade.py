import os
import sys

from mock import patch, MagicMock

os.environ['JUJU_UNIT_NAME'] = 'swift-storge'

# python-apt is not installed as part of test-requirements but is imported by
# some charmhelpers modules so create a fake import.
sys.modules['apt'] = MagicMock()
sys.modules['apt_pkg'] = MagicMock()

with patch('charmhelpers.contrib.hardening.harden.harden') as mock_dec:
    mock_dec.side_effect = (lambda *dargs, **dkwargs: lambda f:
                            lambda *args, **kwargs: f(*args, **kwargs))
    with patch('lib.misc_utils.is_paused') as is_paused:
        with patch('lib.swift_storage_utils.register_configs'):
            import actions.openstack_upgrade as openstack_upgrade

from test_utils import (
    CharmTestCase
)

TO_PATCH = [
    'config_changed',
    'do_openstack_upgrade',
]


class TestSwiftStorageUpgradeActions(CharmTestCase):

    def setUp(self):
        super(TestSwiftStorageUpgradeActions, self).setUp(openstack_upgrade,
                                                          TO_PATCH)

    @patch('actions.charmhelpers.contrib.openstack.utils.config')
    @patch('actions.charmhelpers.contrib.openstack.utils.action_set')
    @patch('actions.charmhelpers.contrib.openstack.utils.'
           'git_install_requested')
    @patch('actions.charmhelpers.contrib.openstack.utils.'
           'openstack_upgrade_available')
    def test_openstack_upgrade_true(self, upgrade_avail, git_requested,
                                    action_set, config):
        git_requested.return_value = False
        upgrade_avail.return_value = True
        config.return_value = True

        openstack_upgrade.openstack_upgrade()

        self.assertTrue(self.do_openstack_upgrade.called)
        self.assertTrue(self.config_changed.called)

    @patch('actions.charmhelpers.contrib.openstack.utils.config')
    @patch('actions.charmhelpers.contrib.openstack.utils.action_set')
    @patch('actions.charmhelpers.contrib.openstack.utils.'
           'git_install_requested')
    @patch('actions.charmhelpers.contrib.openstack.utils.'
           'openstack_upgrade_available')
    def test_openstack_upgrade_false(self, upgrade_avail, git_requested,
                                     action_set, config):
        git_requested.return_value = False
        upgrade_avail.return_value = True
        config.return_value = False

        openstack_upgrade.openstack_upgrade()

        self.assertFalse(self.do_openstack_upgrade.called)
        self.assertFalse(self.config_changed.called)
