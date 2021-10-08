import traceback
from pymodm import MongoModel, fields
from bson import ObjectId
from sentry_sdk import capture_exception
from datetime import datetime
from ..decorators.cache import cache_id, cache_filter
from ..utils import get_current_time


class BaseMG(MongoModel):
    created_by = fields.CharField(default='', blank=True)
    updated_by = fields.CharField(default='', blank=True)
    created_time = fields.DateTimeField()
    updated_time = fields.DateTimeField()

    @classmethod
    def add(cls, payload):
        _init = {}
        for field in cls._mongometa.get_fields():
            if field.mongo_name == '_id' and not isinstance(payload.get('_id'), ObjectId):
                _init[field.mongo_name] = ObjectId()
            else:
                if field.mongo_name in ['created_time', 'updated_time'] and not isinstance(field.mongo_name, datetime):
                    _init[field.mongo_name] = get_current_time()
                else:
                    _init[field.mongo_name] = payload.get(field.mongo_name, field.default)
        return cls(**_init).save()

    def to_dict(self):
        _dict = self.to_son().to_dict()
        if '_id' in _dict.keys():
            _dict['_id'] = str(_dict['_id'])
        return _dict

    @classmethod
    def update_one(cls, filter, update_data):
        try:
            _keys = update_data.keys()
            _delete_keys = ['created_by', 'created_time', '_id']
            for _key in _delete_keys:
                if _key in _keys:
                    del update_data[_key]

            return cls.objects.raw(filter).update({
                '$set': update_data
            })
        except cls.DoesNotExist:
            return {}
        except Exception as e:
            capture_exception(e)
            traceback.print_exc()
            return {}

    @classmethod
    def get_all(cls):
        return cls.objects.all()

    @classmethod
    def find_one(cls, _filter, with_cache=True, cache_keys=[]):
        try:
            _keys = _filter.keys()

            def get_db():
                value = cls.objects.get(_filter)
                if value:
                    return value.to_dict()
                return {}

            if with_cache:
                @cache_filter(key_prefix=cls.Meta.collection_name, key_fields=cache_keys, options=[])
                def get_cache_by_filter(*args, **kwargs):
                    return get_db()

                return get_cache_by_filter(**_filter, options=[])
            return get_db()

        except cls.DoesNotExist:
            return {}
        except:
            capture_exception()
            traceback.print_exc()
            return {}

    @classmethod
    def get_by_filter(cls, _filter={}, _options={}, with_cache=True, cache_keys=[]):
        try:
            _keys = _filter.keys()
            __option_keys = _options.keys()

            def get_db():
                _query = [{
                    '$match': _filter
                }]
                if 'sort' in __option_keys:
                    _query.append({
                        '$sort': _options.get('sort')
                    })
                if 'offset' in __option_keys:
                    _query.append({
                        '$skip': _options.get('offset')
                    })
                if 'limit' in __option_keys:
                    _query.append({
                        '$limit': _options.get('limit')
                    })
                values = cls.objects.aggregate(*_query)
                return list(values)

            if with_cache:
                @cache_filter(key_prefix=cls.Meta.collection_name, key_fields=cache_keys, options=__option_keys)
                def get_cache_by_filter(*args, **kwargs):
                    return get_db()

                return get_cache_by_filter(**_filter, options=_options)
            return get_db()
        except cls.DoesNotExist:
            return {}
        except:
            capture_exception()
            traceback.print_exc()
            return {}

    @classmethod
    def get_by_filter_use_raw(cls, _filter={}):
        try:
            _keys = _filter.keys()

            def get_db():
                _query = _filter
                values = cls.objects.raw(_filter)
                return list(values)

            #
            # if with_cache:
            #     @cache_filter(key_prefix=cls.Meta.collection_name, key_fields=cache_keys, options=__option_keys)
            #     def get_cache_by_filter(*args, **kwargs):
            #         return get_db()
            #
            #     return get_cache_by_filter(**_filter, options=_options)
            return get_db()
        except cls.DoesNotExist:
            return []
        except:
            capture_exception()
            traceback.print_exc()
            return []

    @classmethod
    def get_by_id(cls, _id, with_cache=True):
        try:
            def get_db():
                value = cls.objects.get({'_id': fields.ObjectId(_id)})
                if value:
                    return value.to_dict()
                return {}

            if with_cache:
                @cache_id(key_prefix=cls.Meta.collection_name)
                def get_cache_by_id(with_id):
                    return get_db()

                return get_cache_by_id(_id)
            return get_db()
        except:
            capture_exception()
            traceback.print_exc()
            return {}

    @classmethod
    def get_by_list_ids(cls, list_ids):
        try:
            return cls.objects.raw({'_id': {'$in': [fields.ObjectId(id) for id in list_ids]}})
        except Exception as e:
            capture_exception(e)
            traceback.print_exc()
            return []

