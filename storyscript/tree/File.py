from .String import String


class File(String):

    def __init__(self, data):
        super().__init__(data)
        if type(data) is list:
            self.chunks = data

    def json(self):
        json = super().json()
        json['$OBJECT'] = 'file'
        return json

    def __repr__(self):
        return 'File({})'.format(self.chunks)
