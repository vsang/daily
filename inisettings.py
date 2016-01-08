#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import ConfigParser

class Dict(dict):
    def _KEY(self, key):
        return key.upper().replace('.', '_')

    def _V(self, value):
        if isinstance(value, basestring):
            if value.lower() == 'true':
                value = True
            elif value.lower() == 'false':
                value = False
            elif value.isdigit():
                value = int(value)
        return value

    def __getattr__(self, key):
        return self.get(self._KEY(key))

    def __setattr__(self, key, value):
        return 

    def __setitem__(self, key, value):
        return super(Dict, self).__setitem__(self._KEY(key), self._V(value))

    def __getitem__(self, key):
        return super(Dict, self).__getitem__(self._KEY(key))


'''The difference from Dict:
1. read content from a ini
2. so for key:value, value is always a Dict'''
class IniSettings(Dict):
    def __init__(self, file_path=''):
        if file_path:
            self._load(file_path)

    # This is to get the ini section.
    # Do not return None since the returned
    # value will be used to retrive the ini option.
    def __getattr__(self, key):
        v = self.get(self._KEY(key))
        if not v:
            return Dict()
        return v

    def _load(self, file_path):
        cf = ConfigParser.ConfigParser()
        cf.read(file_path)
        for s in cf.sections():
            od = Dict()
            for o in cf.options(s):
                v = cf.get(s, o)
                od[o] = v
            self[s] = od

    def merge(self, properties):
        for ks, vs in properties.items():
            if not ks in self:
                self[ks] = Dict()
            for ko, vo in vs.items():
                self[ks][ko] = vo


def get_app_settings():
    base_dir = os.path.dirname(__file__)
    local_config_file = os.path.join(base_dir, 'app.properties.local.ini')
    local_settings = IniSettings(local_config_file)

    app_config_file = os.path.join(base_dir, 'app.properties.ini')
    app_settings = IniSettings(app_config_file)
    app_settings.merge(local_settings)
    return app_settings

settings = inisettings = get_app_settings()


if __name__ == '__main__':
    general_set = '''
[log]
level=3
test=true
oldkey=oldvalue
sub.key=what_is aasdf
[sec.a]
opt_a=oa
opt.b=ob
'''
    local_set = """
[log]
level= 4
test =  true
new_field = 33333
[bug]
asign=asignee lastname
"""


    with open('app.properties.ini', 'w') as general_set_f:
        general_set_f.write(general_set)
    with open('app.properties.local.ini', 'w') as local_set_f:
        local_set_f.write(local_set)

    print 'Testing key is not case sensitive...'
    assert settings.log == settings.LOG
    assert settings.log.level == settings.LOG.Level

    print 'Testing local overrides the general setting...'
    assert settings.log.level == 4
    assert settings.log.test is True
    assert settings.log.oldkey == 'oldvalue'

    print 'Testing key/value convertion....'
    assert settings.log.sub_Key == 'what_is aasdf'
    assert settings.sec_a.OPT_a == 'oa'
    assert settings.SEC_A.opt_b == 'ob'

    print 'Testing new section found in local...'
    assert settings.bug.asign == 'asignee lastname'

    print 'Testing getitem......'
    assert settings['log']['level'] == 4
    assert settings['lOg']['leVel'] == 4

    print 'Testing none set key get None..'
    assert settings.log.nonkey is None
    assert settings.nonsection.nonkey is None

    print 'Result success'



