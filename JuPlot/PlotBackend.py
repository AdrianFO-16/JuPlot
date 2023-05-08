from utils import *
from DataStructures import  *

import matplotlib.pyplot as plt
import matplotlib as mpl

from pandas import DataFrame
from numpy import ndarray

class PlotBackend(SAC):
    _theme = None

    def __init__(self, *args, **kwargs):
        super().__init__()

        self.figure = None
        self.theme = kwargs.get('theme', None)
        self.history = kwargs.get('history', [])
        self.current_plot = kwargs.get('current_plot', [])
        self.layout = (kwargs.get('nrows', 1), kwargs.get('ncols', 1))

    @staticmethod
    def migrate_backend(from_, to_, *args, **kwargs):
        inherited = {}
        if isinstance(from_, PlotBackend):
            inherited['history'] = from_.history
            inherited['current_plot'] = from_.current_plot
            inherited['theme'] = from_.theme
            inherited['layout'] = from_.layout
            # TODO: agregar self.data
            
        return to_(*args, **(inherited | kwargs))
         
    def __plot_cache(self, *args, **kwargs):
        self.current_plot.append((args, kwargs))
    
    @method_wrapper(__plot_cache)
    def plot(self, *args, **kwargs):
        self._plot_backend(*args, **kwargs)

    def __show_reset(self, *args, **kwargs):
        self.history.append(self.current_plot)
        self.current_plot = []
        self.figure = None

    @method_wrapper(__show_reset)
    def show(self, *args, **kwargs):
        self._show_backend()

    def redo_plot(self, n = None, *args, **kwargs):
        if n is None:
            plot = self.current_plot
        else:
            plot = self.history[n]

        if plot is None:
            print("Plot not active")
            return

        for args, kwargs in plot:
            self._plot_backend(*args, **kwargs)
        
        self._show_backend()
        self.figure = None
        self._reset_backend()

    #region Theme
    @property
    def theme(self):
        return self._theme

    @theme.setter
    def theme(self, new_theme):        
        self._theme = new_theme
        self._configure()

    # Config and customization
    def set_theme_param(self, element, key, value):
        """
        Override local parameter config
        """
        self.theme.edit_property(element, key, value)
        self._configure()

    def reset_theme(self):
        self.theme = None
    #endregion 

    #region Backend SAC Methods
    """
    Methods to be implemented in derived classes.
    Helper methods called in class wrappers.
    """
    @semi_abstract_method
    def _plot_backend(self, *args, **kwargs):
        pass
    
    @semi_abstract_method
    def _configure(self, *args, **kwargs):
        pass
        
    @semi_abstract_method
    def _show_backend(self, *args, **kwargs):
        pass
    
    @semi_abstract_method
    def _reset_backend(self, *args, **kwargs):
        pass
    #endregion

class EmptyBackend(PlotBackend):
    def __init__(self, *args, **kwargs):
        self.log = kwargs.get('log', True)
        if self.log: print("Empty Backend Initialized")

        super().__init__(*args, **kwargs)

    def dummy_output(func):
        def wrapper(self, *args, **kwargs):
            if self.log: print("Empty Backend:", end = " ")
            func(self, *args, **kwargs)
        return wrapper

    @dummy_output
    def _reset_backend(self, *args, **kwargs):
        if self.log: print("RESETTING")

    @dummy_output
    def _plot_backend(self, *args, **kwargs):
        if self.log: print("PLOTTING")
    
    @dummy_output
    def _configure(self, *args, **kwargs):
        if self.log: print("CONFIGURING")

    @dummy_output
    def _show_backend(self, *args, **kwargs):
        if self.log: print("SHOWING")

class MatplotlibBackend(PlotBackend):

    """ Define base betweeen seaborn and matplotlib
    Definir diccionario enumPlots -> fx to plot
    """
    def __init__(self, *args,  **kwargs):
        super().__init__(*args, **kwargs)

        self.rc_params_dictionary = None

        if 'base' in kwargs:
            if kwargs['base'] == 'seaborn':
                print("Seaborn mode")
                self.__base = 'seaborn'
        else:
            self.__base = "matplotlib"
        

        """DEBERIA DE PONERLO EN ABSTRACT?
        Yo creo que si
        """
        self.data = None
        self.__data_accesser = None
        self.__data_dim = None

    def _reset_backend(self, *args, **kwargs):
        plt.cla()
        plt.clf()
        plt.close()

    def __configuration_actions(self):

        actions = {'title': lambda n,x: self.figure['axes'][n].set_title(x),
                   'suptitle': lambda _,x: self.figure['fig'].suptitle(x),
                   'limits': lambda n,x: (self.figure['axes'][n].set_xlim(x[0]), self.figure['axes'][n].set_ylim(x[1])),
                   'grid': lambda n,x: self.figure['axes'][n].grid(x),
                   'ticks': lambda n,x: (None if x[0] is None else self.figure['axes'][n].set_xticks(x[0]),
                                       None if x[1] is None else self.figure['axes'][n].set_yticks(x[1])),
                    'legend': lambda n,x: self.figure['axes'][n].legend() if x else None,                      
            }
        
        return actions


    def _plot_backend(self, *args, **kwargs):

        n_plot = 0
        if 'n_plot' in kwargs:
            n_plot = kwargs['n_plot']
            kwargs.pop('n_plot')

        with mpl.rc_context(self.rcParams):
            # Initialize backend figure object
            if self.figure is None:
                    
                    self._reset_backend()

                    if self.layout[0] * self.layout[1] > 1:
                        temp_fig = plt.subplots(*self.layout)
                        self.figure = dict(zip(('fig', 'axes'), (temp_fig[0], temp_fig[1].flatten().tolist())))
                    else:
                        self.figure = dict(zip(('fig', 'axes'), (plt.figure(), [plt.gca()])))
            

            #region Esta un poco sucio
            # TODO: Arreglar la suciedad
            matching_actions = dict.fromkeys(set(self.__configuration_actions().keys()).intersection(set(kwargs.keys())))
            matching_actions_args = {action:(n_plot, kwargs[action]) for action in matching_actions}

            for action in matching_actions:
                kwargs.pop(action)

            self.__handle_plot(n_plot, *args, **kwargs)

            self.__do_configuration_actions(matching_actions_args)
            #endregion

    
    def __dataframe_accesser(self, idx):
        if isinstance(idx, int):
            return self.data.iloc[:, idx]
        elif isinstance(idx, str):
            return self.data[idx]
        else:
            raise ValueError(f"Accessor: {idx} with type {type(idx)} invalid for dataframe data-type")
        
    def __ndarray_accesser(self, idx):
        return self.data[:, idx]
    
    def __list_tuple_accesser(self, idx):
        return self.data[idx]
    

    def __extract_data(self, xyz):
        
        """
        xyz -> tuple, list  -> data -> list, tuple

        xyz -> int -> data -> dataframe, array

        xyz -> string -> data -> dataframe

        xyz -> None -> data -> dataframe, array -> default extraction
        """

        # Handle data inputs
        if self.data is None and xyz is None:
            raise AssertionError("plot_type specified, yet no data was provided to plot")
        

        if self.data is not None:
            non_null_entries = range(self.__data_dim)
            #Default Case
            if xyz is not None:
                non_null_entries = {key: val for key, val in xyz.items() if val is not None}.values()

            return tuple(tuple(self.__data_accesser(val)) for val in non_null_entries)
        

        non_null_entries = {key: val for key, val in xyz.items() if val is not None}.values()
        return tuple(tuple(val) for val in non_null_entries)



    def __handle_data(self, kwargs):
        """
        Formas de ingresar datos para plotear:

        data -> como un dataframe
        data -> lista de 2,3 longitud con sublistas de la misma longitud

        -> solo en caso dataframe y numpy array se guarda la informacion

        caso data sobreescribe x,y,z

        x,y,z -> array like de la misma longitud para plotear de forma local
        x,y,z -> indexacion para la data guardada

        -> Uso
        Si x,y,z no es definido 
        """
        keys = ('x', 'y', 'z')

        xyz = {key: kwargs.get(key) for key in keys}

        # CASO DATA:
        data = kwargs.get('data')

        if data is not None:
            self.data = data
            #TODO: Definir una función que me de la extraccion de los datos basado en el tipo de data
            if isinstance(data, DataFrame):
                self.__data_accesser = self.__dataframe_accesser
                self.__data_dim = self.data.shape[1]
            elif isinstance(data, (list, tuple)):
                self.__data_accesser = self.__list_tuple_accesser
                self.__data_dim = len(self.data)
            elif isinstance(data, ndarray):
                self.__data_accesser = self.__ndarray_accesser
                self.__data_dim = self.data.shape[1]
            else:
                raise ValueError(f"data kwarg type: {type(data)} cannot be handled")
            kwargs.pop('data')

        # CASO X,Y,Z

        #TODO: Revisar que todo no sea nulo.
        if not all(map(lambda x: xyz[x] is None, xyz)):
            for key in keys:
                try:
                    kwargs.pop(key)
                except KeyError:
                    pass

            return xyz
        
        return None
        

    def __handle_plot(self, n_plot, *args, **kwargs):

        xyz = self.__handle_data(kwargs)

        plot_type = kwargs.get('plot_type')
        if plot_type is None:
            return 
        kwargs.pop('plot_type')

        # If plot type is defined then there must be a global or local xyz declaration
        to_plot = self.__extract_data(xyz)

        # TODO: Borrar el feedback
        # print('data:', self.data)
        # print('xyz: ', xyz)
        # print('to plot:', to_plot)


        plots = {
            PlotType.scatter: lambda: self.figure['axes'][n_plot].plot(*to_plot, **kwargs),
            PlotType.box: lambda: self.figure['axes'][n_plot].boxplot(*to_plot, **kwargs)

        }

        plots[plot_type]()
    
    def __do_configuration_actions(self, matching_actions_args):

        actions = self.__configuration_actions()

        for action, args in matching_actions_args.items():
            actions[action](*args)

        plt.tight_layout()


    def _show_backend(self, *args, **kwargs):
        plt.show()
    
    def _configure(self, *args, **kwargs):
        # Translate Theme object to dictionary
        if self.theme is not None:
            self.rcParams = self.__interpret_theme()

        else:
            self.rcParams = mpl.rcParamsDefault

    def __interpret_theme(self):

        rcParams = {}
                
        def set_param(path, val):
            rcParams[path] = val

        rules = {
            ThemeElement.figure: {
                'dpi': lambda x: set_param('figure.dpi', x),
                'paper_color': lambda x: set_param('figure.facecolor', x),
                'figsize': lambda x: set_param('figure.figsize', x),
                'plot_background_color': lambda x: set_param('axes.facecolor', x)
            },

            ThemeElement.font: {
                'size': lambda x: set_param('font.size', x),
                'color': lambda x: set_param('text.color', x),
                'family': lambda x: set_param('font.family', x),
                'weight': lambda x: set_param('font.weight', x),
            },

            ThemeElement.title: {
                'font': {
                    'size': lambda x: set_param('figure.titlesize', x),
                    'weight': lambda x: set_param('figure.titleweight', x),
                }
            },
            
            ThemeElement.axes: {
                'font': {
                    'size': lambda x: set_param('axes.labelsize', x),
                    'weight': lambda x: set_param('axes.labelweight', x),
                    'color': lambda x: set_param('axes.labelcolor', x)
                }
            },

            ThemeElement.legend: {
                'font': {
                    'color': lambda x: set_param('legend.labelcolor', x)
                }
            }

        }

        apply_dict_rules(rules, self.theme)

        return rcParams

class PlotlyBackend(PlotBackend):
    
    def _plot(self, data, plot_type, *args, **kwargs):
        pass

    def _show(self, *args, **kwargs):
        pass

    def _configure(self, *args, **kwargs):
        pass