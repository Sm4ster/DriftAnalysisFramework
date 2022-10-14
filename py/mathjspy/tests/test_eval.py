# Copyright (c) 2014 mathjspy
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# @license: http://www.opensource.org/licenses/mit-license.php
# @author: see AUTHORS file


class TestEval(object):

    def setup(self):
        from mathjspy import MathJS
        self.mjs = MathJS()

    def test_simple_math(self):
        result = self.mjs.eval('1 + 2 * 6')
        assert result == 13

    def test_parenthesis(self):
        result = self.mjs.eval('(1 + 2) * 6 + (3 * 4) * 2 + 9 / 3')
        assert result == 45

    def test_variable_in_expression(self):
        self.mjs.set('var_a', 7)
        result = self.mjs.eval('var_a + 5')
        assert result == 12

    def test_variable_dictionary_expression(self):
        self.mjs.update({'var_a': 6, 'var_b': 8})
        result = self.mjs.eval('var_a + 10 * var_b + (var_a / 2 + 3) + var_b')
        assert result == 100

    def test_mapped_expression(self):
        self.mjs.update({'var_a': 6, 'var_b': 8})
        expr_map = [['var_c', 'var_a + 10 * var_b + (var_a / 2 + 3) + var_b'], ['var_d', 'var_c + 50']]
        self.mjs.eval_map(expr_map)
        assert self.mjs.get('var_d') == 150

    def test_equations(self):
        assert self.mjs.eval('1 + 1 - 7 + 5') == 0
        assert self.mjs.eval('4 - 3 * (4 - 2 * (6 - 3) ) / 2') == 7
        assert self.mjs.eval('16 - 3 * (8 - 3) ^ 2 / 5') == 1
        assert self.mjs.eval('3 + 6 * (5 + 4) / 3 - 7') == 14
        assert self.mjs.eval('9 - 5 / (8 - 3) * 2 + 6') == 13
        assert self.mjs.eval('150 / (6 + 3 * 8) - 5') == 0
        assert self.mjs.eval('(36 - 6) / (12 + 3)') == 2
        assert self.mjs.eval('7 + (6 * 5 ^ 2 + 3)') == 160
