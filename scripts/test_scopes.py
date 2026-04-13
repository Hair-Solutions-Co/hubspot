"""Quick scope check — tests which API surfaces the service key can reach."""
import sys, json
sys.path.insert(0, 'scripts')
from hubspot_object_reports import HubSpotClient, get_token

c = HubSpotClient(get_token())
tests = {}

def probe(label, method, path, **kw):
    try:
        r = c.request_json(method, path, **kw)
        if 'results' in r:
            tests[label] = f'OK ({len(r["results"])} results)'
        elif 'data' in r:
            tests[label] = 'OK (data returned)'
        elif 'status' in r and r['status'] == 'error':
            tests[label] = f'BLOCKED: {r.get("message","")}'
        else:
            tests[label] = f'OK (keys: {list(r.keys())[:5]})'
    except Exception as e:
        tests[label] = f'BLOCKED: {e}'

probe('CRM contacts',       'GET', '/crm/v3/objects/contacts',         params={'limit': 1})
probe('CRM deals',          'GET', '/crm/v3/objects/deals',            params={'limit': 1})
probe('CRM tickets',        'GET', '/crm/v3/objects/tickets',          params={'limit': 1})
probe('CRM orders',         'GET', '/crm/v3/objects/orders',           params={'limit': 1})
probe('CRM invoices',       'GET', '/crm/v3/objects/invoices',         params={'limit': 1})
probe('CRM subscriptions',  'GET', '/crm/v3/objects/subscriptions',    params={'limit': 1})
probe('CRM payments',       'GET', '/crm/v3/objects/commerce_payments',params={'limit': 1})
probe('CMS blog posts',     'GET', '/cms/v3/blogs/posts',              params={'limit': 1})
probe('HubDB tables',       'GET', '/cms/v3/hubdb/tables',             params={'limit': 1})
probe('Marketing emails',   'GET', '/marketing/v3/emails',             params={'limit': 1})
probe('Files',              'GET', '/files/v3/files',                   params={'limit': 1})
probe('Conversations',      'GET', '/conversations/v3/conversations/threads', params={'limit': 1})
probe('Forms',              'GET', '/marketing/v3/forms',              params={'limit': 1})
probe('Users',              'GET', '/settings/v3/users',               params={'limit': 1})

print('\nScope Availability Report')
print('=' * 50)
for k, v in tests.items():
    status = 'OK' if v.startswith('OK') else 'BLOCKED'
    icon = '\u2705' if status == 'OK' else '\u274c'
    print(f'  {icon} {k}: {v}')

ok = sum(1 for v in tests.values() if v.startswith('OK'))
print(f'\n{ok}/{len(tests)} scopes accessible')
