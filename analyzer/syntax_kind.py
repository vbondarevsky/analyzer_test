from enum import Enum


class SyntaxKind(Enum):
    # Punctuation
    TildeToken = 1000  # ~
    PercentToken = 1001  # %
    AsteriskToken = 1002  # *
    OpenParenToken = 1003  # (
    CloseParenToken = 1004  # )
    MinusToken = 1005  # -
    PlusToken = 1006  # +
    OpenBracketToken = 1008  # [
    CloseBracketToken = 1009  # ]
    ColonToken = 1010  # :
    SemicolonToken = 1011  # ;
    CommaToken = 1013  # ,
    DotToken = 1015  # .
    QuestionToken = 1016  # ?
    SlashToken = 1017  # /
    HashToken = 1018  # #
    AmpersandToken = 1019  # &

    # Other
    EndOfFileToken = 4000

    # Comparison operator
    EqualsToken = 1007  # =
    LessThanToken = 1012  # <
    GreaterThanToken = 1014  # >
    LessThanEqualsToken = 2000  # <=
    GreaterThanEqualsToken = 2001  # >=
    LessThanGreaterThanToken = 2002  # <>

    # Tokens
    BadToken = 5000
    IdentifierToken = 5001
    NumericLiteralToken = 5002
    DateLiteralToken = 5003
    StringLiteralToken = 5004

    # Trivia
    SingleLineCommentTrivia = 7002
