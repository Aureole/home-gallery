class GalleryException:
    pass

class DatabaseException(GalleryException):
    def __init__(self, message):
        Exception.__init__(self, message)

class DAOException(GalleryException):
    """
    Base DAO exception class
    """

class DAOCreateFailedError(DAOException):
    """
    DAO Create failed
    """
    
    message = "Create failed"

class DAOUpdateFailedError(DAOException):
    """
    DAO Update failed
    """
    
    message = "Update failed"


class DAODeleteFailedError(DAOException):
    """
    DAO Delete failed
    """

    message = "Delete failed"

class DAOConfigError(DAOException):
    """
    DAO is miss configured
    """

    message = "DAO is not configured correctly, missing model definition"