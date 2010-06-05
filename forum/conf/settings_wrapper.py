"""
Definition of a Singleton wrapper class for livesettings
with interface similar to django.conf.settings
that is each setting has unique key and is accessible
via dotted lookup.

for example to lookup value of setting BLAH you would do

from forum.conf import settings as forum_settings

forum_settings.BLAH

NOTE that at the moment there is distinction between settings
(django settings) and forum_settings (livesettings)

the value will be taken from livesettings database or cache
note that during compilation phase database is not accessible
for the most part, so actual values are reliably available only 
at run time

livesettings is a module developed for satchmo project
"""
from livesettings import SortedDotDict, config_register

class ConfigSettings(object):
    """A very simple Singleton wrapper for settings
    a limitation is that all settings names using this class
    must be distinct, even though they might belong
    to different settings groups
    """
    __instance = None

    def __init__(self):
        """assigns SortedDotDict to self.__instance if not set"""
        if ConfigSettings.__instance == None:
            ConfigSettings.__instance = SortedDotDict()
        self.__dict__['_ConfigSettings__instance'] = ConfigSettings.__instance
        self.__ordering_index = {}

    def __getattr__(self, key):
        """value lookup returns the actual value of setting
        not the object - this way only very minimal modifications
        will be required in code to convert an app
        depending on django.conf.settings to livesettings
        """
        return getattr(self.__instance, key).value

    def register(self, value):
        """registers the setting
        value must be a subclass of livesettings.Value
        """
        key = value.key
        group_key = value.group.key

        ordering = self.__ordering_index.get(group_key, None)
        if ordering:
            ordering += 1
            value.ordering = ordering
        else:
            ordering = 1
            value.ordering = ordering
        self.__ordering_index[group_key] = ordering

        if key in self.__instance:
            raise Exception('setting %s is already registered' % key)
        else:
            self.__instance[key] = config_register(value)

    def as_dict(self):
        out = dict()
        for key in self.__instance.keys():
            #todo: this is odd that I could not use self.__instance.items() mapping here
            out[key] = self.__instance[key].value
        return out

#settings instance to be used elsewhere in the project
settings = ConfigSettings()