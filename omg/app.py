#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, jsonify, request

import storyscript


class Handler:
    app = Flask(__name__)

    @app.route('/lex', methods=['POST'])
    def lex():
        files = request.json
        # TODO: use https://github.com/storyscript/storyscript/pull/414 here
        filename, value = files.popitem()
        return jsonify(storyscript.loads(value))

    @app.route('/parse', methods=['POST'])
    def parse():
        files = request.json
        # TODO: use https://github.com/storyscript/storyscript/pull/414 here
        filename, value = files.popitem()
        return jsonify(storyscript.loads(value))

    @app.route('/compile', methods=['POST'])
    def compile():
        files = request.json
        # TODO: use https://github.com/storyscript/storyscript/pull/414 here
        filename, value = files.popitem()
        return jsonify(storyscript.loads(value))

    @app.route('/grammar', methods=['GET'])
    def grammar():
        return storyscript.grammar()

    @app.route('/version', methods=['GET'])
    def version():
        return storyscript.__version__


if __name__ == '__main__':
    handler = Handler()
    app = handler.app
    handler.app.run(host='0.0.0.0', port=8000)
