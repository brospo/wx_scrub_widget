

class Data:
    TYPE_ALIAS = {"<class 'pandas.core.frame.DataFrame'>": 'DataFrame',
                  "<type 'unicode'>": 'String',
                  "<type 'int'>": 'Integer',
                  "<type 'float'>": 'Float',
                  "<type 'list'>": 'List',
                  "<type 'str'>": 'String'}

    def __init__(self, _data, _title):
        #dataframe, numpy array, single value
        self.data = _data
        self.title = _title
        self.value_title = Data.TYPE_ALIAS[str(type(_data))]

        self.args = None
        self.kwargs = None

    def set_args(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        print 'Setting kwargs for %s' %self.title