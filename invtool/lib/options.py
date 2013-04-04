def build_extractor(field_name, nas_name):
    def extractor(nas):
        if not getattr(nas, nas_name):
            return {}
        data = {field_name: getattr(nas, nas_name)}
        return data
    return extractor
