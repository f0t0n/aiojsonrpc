def dumps(serializer, *args, **kwargs):
    return serializer.dumps(*args, **kwargs)


def loads(serializer, *args, **kwargs):
    return serializer.loads(*args, **kwargs)
