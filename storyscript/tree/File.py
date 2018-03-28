from .String import String


class File(String):

    def json(self):
        json = super().json()
        json['$OBJECT'] = 'file'
        return json

    def __repr__(self):
        return 'File({})'.format(self.chunks)
