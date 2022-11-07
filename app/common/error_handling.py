class AppErrorBaseClass(Exception):
    pass


class ObjectNotFound(AppErrorBaseClass):
    pass


class ErrorFound(AppErrorBaseClass):
    pass
