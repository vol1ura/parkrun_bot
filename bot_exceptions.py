class ParsingException(Exception):
    """Exception raised if page can't be parsed. In most cases it will be when table is empty.

        Attributes:
            message -- explanation of the error
        """
    def __init__(self, message="Page parsing failed"):
        self.message = message
        super().__init__(self.message)
