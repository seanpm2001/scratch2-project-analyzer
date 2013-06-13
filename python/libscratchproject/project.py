import os
import simplejson

from collections import namedtuple

PROJECT_DIR_PREFIX='/nfsmount/projectstore'
VERSION_DIR_PREFIX='/nfsmount/versionstore'

def calculate_project_dirpath(prefix, project_id):
    project_id = str(project_id)
    s = project_id.rjust(9, '0')
    path = os.path.join(prefix, s[0:2],s[2:4],s[4:6],s[6:8],s[8:])
    return path

class BaseObj(object):
    def __init__(self, info_dict):
        self._d = info_dict

    def __getattr__(self, name):
        if self._d.has_key(name):
            return self._d[name]
        else:
            raise AttributeError

class ScratchObj(BaseObj):
    def __init__(self, info_dict):
        BaseObj.__init__(self, info_dict)

    @property
    def variables(self):
        return [ScratchDataStructureObj(x) for x in self._d['variables']]


class ScratchMediaObj(BaseObj):
    def __init__(self, info_dict):
        BaseObj.__init__(self, info_dict)

class ScratchDataStructureObj(BaseObj):
    def __init__(self, info_dict):
        BaseObj.__init__(self, info_dict)


class Sprite(ScratchObj):
    def __init__(self, sprite_dict):
        ScratchObj.__init__(self, sprite_dict)

    @property
    def spriteInfo(self):
        return namedtuple('SpriteInfo',
            self._d['info'].keys())(**(self._d['info']))

    @property
    def costumes(self):
        return [ScratchMediaObj(x) for x in self._d['costumes']]

    @property
    def sounds(self):
        return [ScratchMediaObj(x) for x in self._d['sounds']]


class _Project(ScratchObj):
    def __init__(self, project_id, load_versions=False):
        filepath = \
            os.path.join(calculate_project_dirpath(PROJECT_DIR_PREFIX, 
            project_id), 'LATEST')
        with open(filepath) as fp:
            d = simplejson.loads(fp.read())

        ScratchObj.__init__(self, d)

    @property
    def info(self):
        return namedtuple('ProjectInfo',
            self._d['info'].keys())(**(self._d['info']))

    @property
    def children(self):
        def convertChild(child):
            if child.has_key('spriteInfo'):
                return Sprite(child)
            else:
                return BaseObj(child)
                
        return [convertChild(child) for child in self._d['children']]

    @property
    def sprites(self):
        return [Sprite(x) for x in self._d['children']]