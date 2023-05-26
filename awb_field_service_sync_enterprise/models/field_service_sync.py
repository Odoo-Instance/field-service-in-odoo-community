
from odoo import api, fields, models, _
import xmlrpc.client
import logging
_logger = logging.getLogger(__name__)
import requests

import re
import string
from dateutil import parser
TEMP_FOLDER = "/tmp/"  # Location where temporary files will be downloaded
PATTERN = r'[' + string.punctuation + ']'  # Create a regex pattern to match all special characters in string

FIELD_TYPES = {'DateTime': 'datetime',
               'Long Integer': 'integer',
               'Double': 'integer'}

DATETIME_FORMAT = '%m/%d/%y %H:%M:%S'


class FieldSeriviceSyncC(models.Model):
    _name = 'field.service.sync'
    _description = 'Field Service Sync Configuration'

    name = fields.Char('Configuration Name', required=True)
    hostname = fields.Char('Hostname', help='Indicate either the FQDN or the IPv4 address', required=True)
    database = fields.Char('Database', help='Indicate the database name of Odoo to connect to')
    username = fields.Char('Username', help='Indicate the username to use', required=True)
    password = fields.Char('Password', help='Indicate the password to use', required=True)
    auto_sync = fields.Boolean('Auto Sync')
    state = fields.Selection(string='Status',selection=[('draft','Draft'),('connected','Connected')])
    error_message = fields.Text('Error Message')
    project_id = fields.Integer('FSM Project ID')

    def connect(self):
        error_message = ''
        """
        This method connects to another Odoo and check if awb_field_service_sync module is installed
        @param config, single recordset of myob.sync.config record
        @return str, str
        """
        try:
            # Get xmlrpc endpoints
            awb_field_service_sync = False
            # Check if URL exist
            if self.check_url(self.hostname):
                models, db, uid, pwd = self._get_xmlrpc()
                # Check if awb_field_service_sync module is installed
                awb_field_service_sync = models.execute_kw(db, uid, pwd, 'ir.module.module', 'search',
                                                  [[['name', '=', 'awb_field_service_sync_community'], ['state', '=', 'installed']]],
                                                  {'limit': 1})
                if not awb_field_service_sync:
                    error_message = 'Make sure AWB Field Service Sync Community module is installed in remote host - %s' % self.hostname
            else:
                error_message = 'Unable to connect to %s. The remote host is unreachable' % self.hostname
        except Exception:
            error_message = 'Unable to connect to %s. Check your credentials and try again' % self.hostname

        if error_message == '':
            self.state = 'connected'
        else:
            self.state = 'draft'
        self.error_message = error_message
    def check_url(self, url):
        """
        Check if URL is reachable or not
        """
        try:
            # Get Url
            get = requests.get(url, timeout=(10, 30))
            # if the request succeeds
            if get.status_code == 200:
                return True
            else:
                return False
        # Exception
        except requests.exceptions.RequestException as e:
            # print URL with Errs
            return False

    def _get_xmlrpc(self):
        """
        This method prepares the xmlrpc endpoints
        @param config, single recordset of myob.sync.config record
        @return xmlrpc endpoints
        """
        url = self.hostname
        db = self.database
        username = self.username
        password = self.password
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        uid = common.authenticate(db, username, password, {})
        return models, db, uid, password

    def disconnect(self):
        self.error_message = ''
        self.state = 'draft'

    def process_values(self,model_name, method_name, args):
        print(args)
        models, db, uid, pwd = self._get_xmlrpc()
        rec = models.execute_kw(db, uid, pwd, model_name, method_name, args)
        return rec