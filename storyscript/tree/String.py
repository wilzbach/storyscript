from .Path import Path


class String:

    def __init__(self, data):
        self.chunks = [data]

    def add(self, bit):
        self.chunks.append(bit)

    def complex(self):
        for bit in self.chunks:
            if isinstance(bit, Path):
                return True

    def json(self):
        result = {'$OBJECT': 'string'}
        if self.complex():
            string = []
            values = []
            for bit in self.chunks:
                if isinstance(bit, Path):
                    values.append(bit.json())
                    string.append('{}')
                else:
                    string.append(bit)
            result['values'] = values
            result['string'] = ''.join(string).strip()
            return result
        stripped_chunk = [bit.strip() for bit in self.chunks]
        joined_string = ' '.join(stripped_chunk)
        result['string'] = joined_string
        return result

    def __repr__(self):
        return 'String({})'.format(self.chunks)
