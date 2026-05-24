from vnbrokers.domain.raw import RawPayload


def preserve_raw(data: object) -> RawPayload:
    return RawPayload(source="tcbs", data=data)
