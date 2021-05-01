#!/usr/bin/env python

import argparse
import copy
import re
import yaml


class Namespace(object):
    def __init__(self, somedict={}):
        self.add(somedict)

    def add(self, somedict):
        for key, value in somedict.items():
            assert isinstance(key, str) and re.match("[A-Za-z_-]", key)
            if isinstance(value, dict):
                if key in self.__dict__ and isinstance(self.__dict__[key], Namespace):
                    self.__dict__[key].add(value)
                else:
                    self.__dict__[key] = Namespace(value)
            else:
                self.__dict__[key] = value

    def get(self, key, default=None):
        value = None
        try:
            for k in key.split("."):
                value = self.__dict__[k] if value is None else vars(value)[k]
                assert value is not None
        except:
            value = default
        return value

    def set(self, key, value, force=False):
        if force or self.get(key) is None:
            somedict = {}
            v = somedict
            items = key.split(".")
            for i in range(len(items) - 1):
                k = items[i]
                v[k] = {}
                v = v[k]
            v[items[-1]] = value
            self.add(somedict)

    def to_dict(self):
        somedict = copy.deepcopy(self.__dict__)
        for key, value in somedict.items():
            if isinstance(value, Namespace):
                somedict[key] = value.to_dict()
        return somedict

    def __getattr__(self, attribute):
        raise AttributeError(
            f"Can not find {attribute} in namespace. Please write {attribute} in your config file(xxx.yaml)!")

    def __repr__(self):
        items = (f"{k}={v!r}" for k, v in self.__dict__.items())
        return "{}({})".format(type(self).__name__, ", ".join(items))

    def __eq__(self, other):
        if isinstance(self, Namespace) and isinstance(other, Namespace):
           return self.__dict__ == other.__dict__
        return NotImplemented


parser = argparse.ArgumentParser()
parser.add_argument('-c', '--config_files', nargs='+', default=['config.yaml'])
parser.add_argument('--overrides', nargs='+')
parser.add_argument('-e', '--exp_dir', required=True)
args = parser.parse_args()

config = Namespace()
for config_file in args.config_files:
    print(f'Loading {config_file}')
    with open(config_file) as f:
        config.add(yaml.safe_load(f))

for override in args.overrides:
    config.add(eval(override))
config.set("args", vars(args))
if args.exp_dir:
    config.set("exp.dir", args.exp_dir, force=True)
config.set("val.dataloader.batch_size", config.train.dataloader.batch_size)
config.set("test.dataloader.batch_size", config.val.dataloader.batch_size)
config.set("checkpoint.dir", config.exp.dir)

print(config)
print(yaml.dump(config.to_dict(), allow_unicode=True))
