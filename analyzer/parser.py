from analyzer.expression.binary_expression_syntax import BinaryExpressionSyntax
from analyzer.expression.empty_syntax import EmptySyntax
from analyzer.expression.equals_value_clause_syntax import EqualsValueClauseSyntax
from analyzer.expression.literal_expression_syntax import LiteralExpressionSyntax
from analyzer.expression.method_syntax import MethodSyntax
from analyzer.expression.module_syntax import ModuleSyntax
from analyzer.expression.parameter_list_syntax import ParameterListSyntax
from analyzer.expression.parameter_syntax import ParameterSyntax
from analyzer.expression.parenthesized_expression_syntax import ParenthesizedExpressionSyntax
from analyzer.expression.prefix_unary_expression_syntax import PrefixUnaryExpressionSyntax
from analyzer.expression.variable_declaration_syntax import VariableDeclarationSyntax
from analyzer.syntax_kind import SyntaxKind


class InvalidSyntaxError(Exception):
    pass


class Parser(object):
    def __init__(self, lexer):
        self.lexer = lexer
        self.token = next(self.lexer)

    def next_token(self):
        self.token = next(self.lexer)

    def eat(self, kind):
        if self.token.kind == kind:
            self.next_token()
        else:
            raise InvalidSyntaxError('syntax error')

    def factor(self):
        token = self.token
        if token.kind == SyntaxKind.PlusToken:
            self.eat(SyntaxKind.PlusToken)
            return PrefixUnaryExpressionSyntax(SyntaxKind.UnaryPlusExpression, token, self.factor())
        elif token.kind == SyntaxKind.MinusToken:
            self.eat(SyntaxKind.MinusToken)
            return PrefixUnaryExpressionSyntax(SyntaxKind.UnaryMinusExpression, token, self.factor())
        elif token.kind == SyntaxKind.NumericLiteralToken:
            self.eat(SyntaxKind.NumericLiteralToken)
            return LiteralExpressionSyntax(SyntaxKind.NumericLiteralExpression, token)
        elif token.kind == SyntaxKind.OpenParenToken:
            self.eat(SyntaxKind.OpenParenToken)
            node = self.expr()
            close_token = self.token
            self.eat(SyntaxKind.CloseParenToken)
            return ParenthesizedExpressionSyntax(token, node, close_token)

    def term(self):
        node = self.factor()

        while self.token.kind in [SyntaxKind.AsteriskToken, SyntaxKind.SlashToken]:
            token = self.token
            if token.kind == SyntaxKind.SlashToken:
                self.eat(SyntaxKind.SlashToken)
            elif token.kind == SyntaxKind.AsteriskToken:
                self.eat(SyntaxKind.AsteriskToken)

            if token.kind == SyntaxKind.SlashToken:
                node = BinaryExpressionSyntax(SyntaxKind.DivideExpression, node, token, self.term())
            elif token.kind == SyntaxKind.AsteriskToken:
                node = BinaryExpressionSyntax(SyntaxKind.MultiplyExpression, node, token, self.term())
        return node

    def expr(self):

        node = self.term()

        while self.token.kind in [SyntaxKind.PlusToken, SyntaxKind.MinusToken]:
            token = self.token
            if token.kind == SyntaxKind.PlusToken:
                self.eat(SyntaxKind.PlusToken)
            elif token.kind == SyntaxKind.MinusToken:
                self.eat(SyntaxKind.MinusToken)

            if token.kind == SyntaxKind.PlusToken:
                node = BinaryExpressionSyntax(SyntaxKind.AddExpression, node, token, self.term())
            elif token.kind == SyntaxKind.MinusToken:
                node = BinaryExpressionSyntax(SyntaxKind.SubtractExpression, node, token, self.term())

        return node

    ########################################################################
    def skip_whitespace(self):
        while self.token.kind in [SyntaxKind.WhitespaceTrivia, SyntaxKind.EndOfLineTrivia]:
            self.next_token()

    def parse(self):
        return self.module()

    def module(self):
        declarations = self.declarations()
        self.skip_whitespace()
        methods = self.methods()
        body = None
        end_of_file_token = None
        return ModuleSyntax(declarations, methods, body, end_of_file_token)

    def declarations(self):
        declarations = []
        while self.token.kind == SyntaxKind.VarKeyword:
            declarations.append(self.variable_declaration())
        return declarations

    def variable_declaration(self):
        var_token = self.token
        variables = []
        export_token = None
        semicolon_token = None
        self.eat(SyntaxKind.VarKeyword)
        self.skip_whitespace()
        while self.token.kind == SyntaxKind.IdentifierToken:
            variables.append(self.token)
            self.eat(SyntaxKind.IdentifierToken)
            if self.token.kind == SyntaxKind.CommaToken:
                variables.append(self.token)
                self.eat(SyntaxKind.CommaToken)
                self.skip_whitespace()
        self.skip_whitespace()
        if self.token.kind == SyntaxKind.ExportKeyword:
            export_token = self.token
            self.eat(SyntaxKind.ExportKeyword)
        if self.token.kind == SyntaxKind.SemicolonToken:
            semicolon_token = self.token
            self.eat(SyntaxKind.SemicolonToken)
        self.skip_whitespace()
        return VariableDeclarationSyntax(var_token, variables, export_token, semicolon_token)

    def methods(self):
        methods = []
        while self.token.kind in [SyntaxKind.FunctionKeyword, SyntaxKind.ProcedureKeyword]:
            methods.append(self.method())
            self.skip_whitespace()
        return methods

    def method(self):
        begin = self.token
        self.next_token()
        self.skip_whitespace()
        identifier = self.token
        self.eat(SyntaxKind.IdentifierToken)
        self.skip_whitespace()
        parameter_list = self.parameter_list()
        self.skip_whitespace()
        if self.token.kind == SyntaxKind.ExportKeyword:
            export = self.token
            self.skip_whitespace()
        else:
            export = None
        block = self.block()
        self.skip_whitespace()
        end = self.token
        self.next_token()

        return MethodSyntax(begin, identifier, parameter_list, export, block, end)

    def parameter_list(self):
        open_paren = self.token
        self.eat(SyntaxKind.OpenParenToken)
        self.skip_whitespace()
        parameters = []
        while self.token.kind == SyntaxKind.IdentifierToken:
            parameters.append(self.parameter())
            self.skip_whitespace()
            if self.token.kind == SyntaxKind.CommaToken:
                parameters.append(self.token)
                self.eat(SyntaxKind.CommaToken)
                self.skip_whitespace()
        close_paren = None
        if self.token.kind == SyntaxKind.CloseParenToken:
            close_paren = self.token
            self.eat(SyntaxKind.CloseParenToken)
        return ParameterListSyntax(open_paren, parameters, close_paren)

    def parameter(self):
        identifier = self.token
        self.eat(SyntaxKind.IdentifierToken)
        self.skip_whitespace()
        default = self.default()
        return ParameterSyntax(identifier, default)

    def default(self):
        if self.token.kind == SyntaxKind.EqualsToken:
            equals_token = self.token
            self.eat(SyntaxKind.EqualsToken)
            self.skip_whitespace()
            value = LiteralExpressionSyntax(self.token)
            self.next_token()
            return EqualsValueClauseSyntax(equals_token, value)
        return EmptySyntax()

    def block(self):
        self.skip_whitespace()
        return EmptySyntax()
