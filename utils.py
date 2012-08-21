# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import date
from settings import DEVS


def dictify(dicts, key, dict2up={}, add_data={}):
    ''' Rearranges iterable of dictionaries to dictionary of lists
    ({'key': val1, 'otherkey': otherval1, ...},
     {'key': val2, 'otherkey': otherval2, ...},
     {'key': val1, 'otherkey': otherval3, ...})
        ->
    {val1: [{'otherkey': otherval1, ...}, {'otherkey': otherval3, ...}],
    {val2: [{'otherkey': otherval1, ...},] }
    '''
    result = {}
    result.update(dict2up)
    for d in dicts:
        if not isinstance(d, dict):
            d = dict(d)
        value = d[key]
        needed_list = result.get(value)
        if needed_list is None:
            result[value] = []
        d.update(add_data)
        result[value].append(d)
    return result


def get_tckt_title(tckt_dict):
    ''' Composes title for ticket '''
    created_on = tckt_dict['time']
    created_on = date.fromtimestamp(created_on // (10 ** 6))
    reporter = DEVS.get(tckt_dict['reporter'], tckt_dict['reporter'])
    return '{0} ({1})'.format(reporter, created_on.strftime("%d.%m.%Y"))


def concatenate_dict(listdict):
    ''' Concatenates values in dictionary of list of strings

    {'key': ['val1', 'val2', ...], ...}
     ->
    {'key': 'val1 val2 ...', ...}

    Used for determining list of HTML classes
    '''
    for key, val_list in listdict.items():
        listdict[key] = ' '.join(val_list)
    return listdict

if __name__ == "__main__":
    test = ({'key': 'val1', 'otherkey': 'otherval1'},
            {'key': 'val2', 'otherkey': 'otherval2'},
            {'key': 'val1', 'otherkey': 'otherval3'})
    from pprint import pprint

    print('Simple case')
    pprint(dictify(test, 'key'))

    print('\nUpdate existing data')
    testdict = {'val1': [{'otherkey': 'initial value'}]}
    pprint(dictify(test, 'key', dict2up=testdict))

    print('\nAdd data to all the dicts')
    pprint(dictify(test, 'key', add_data={'addkey': 'additional value'}))
