def build_extractor(field_name, nas_name):
    def extractor(nas):
        if not getattr(nas, nas_name):
            return {}
        data = {field_name: getattr(nas, nas_name)}
        return data
    return extractor


def extract_pk(nas, field_name):
    return {field_name: getattr(nas, field_name)}
